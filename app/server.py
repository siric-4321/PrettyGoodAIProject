from __future__ import annotations

import asyncio
import html
import json
from pathlib import Path
from urllib.parse import quote

import httpx
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from .analyzer import analyze_and_save
from .config import settings
from .patient_agent import PatientAgent
from .scenario_store import get_scenario
from .transcripts import Transcript


ROOT = Path(__file__).resolve().parents[1]

RECORDING_DIR = ROOT / "artifacts" / "recordings"
RECORDING_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(title="Pretty Good AI Patient Simulator")


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.api_route("/voice", methods=["GET", "POST"])
async def voice(request: Request, scenario: str):
    try:
        get_scenario(scenario)

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    ws_url = f"{settings.public_ws_url}?scenario={quote(scenario)}"

    # Keep the initial greeting tiny. The assessment line immediately
    # plays a recording disclosure, so this greeting is intentionally
    # allowed to be interrupted.
    greeting = html.escape("Hello.", quote=True)

    ws_url_xml = html.escape(ws_url, quote=True)
    scenario_xml = html.escape(scenario, quote=True)

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <ConversationRelay
        url="{ws_url_xml}"
        welcomeGreeting="{greeting}"
        welcomeGreetingInterruptible="speech"
        interruptible="none"
        preemptible="false"
        reportInputDuringAgentSpeech="none"
        dtmfDetection="true"
        speechTimeout="900">
      <Parameter name="scenario_id" value="{scenario_xml}" />
    </ConversationRelay>
  </Connect>
</Response>'''

    return Response(
        content=twiml,
        media_type="application/xml",
    )


def is_disclosure(text: str) -> bool:
    normalized = text.lower()

    phrases = (
        "this call may be recorded",
        "call may be recorded",
        "recorded for quality",
        "recorded for training",
        "quality and training purposes",
    )

    return any(
        phrase in normalized
        for phrase in phrases
    )


def is_hard_terminal(text: str) -> bool:
    """
    These phrases mean the assessment interaction itself is over.

    We handle them deterministically rather than asking the LLM whether
    it should restart the scenario.
    """
    normalized = text.lower()

    terminal_phrases = (
        "you've reached the pretty good ai test line",
        "you have reached the pretty good ai test line",
        "you've reached pretty good ai test line",
        "you have reached pretty good ai test line",
    )

    return any(
        phrase in normalized
        for phrase in terminal_phrases
    )


async def collect_receptionist_turn(
    websocket: WebSocket,
    first_text: str,
    transcript: Transcript,
    wait_seconds: float = 0.8,
) -> tuple[str, list[dict]]:
    """
    The remote assessment agent can occasionally send a spoken greeting
    as multiple completed STT prompts separated by short pauses.

    Wait briefly after the first prompt and combine immediately following
    prompt messages into one receptionist turn.

    Non-prompt events are returned so the main loop can process them.
    """
    parts = [first_text]
    deferred_messages: list[dict] = []

    while True:
        try:
            raw = await asyncio.wait_for(
                websocket.receive_text(),
                timeout=wait_seconds,
            )
        except asyncio.TimeoutError:
            break

        message = json.loads(raw)
        msg_type = message.get("type")

        if msg_type == "prompt":
            if not message.get("last", True):
                continue

            text = message.get(
                "voicePrompt",
                "",
            ).strip()

            if not text:
                continue

            transcript.add(
                "receptionist",
                text,
            )

            if is_disclosure(text):
                continue

            parts.append(text)

            # Another prompt arrived quickly, so reset the short wait
            # and see whether the receptionist is still speaking.
            continue

        # Preserve non-prompt events for normal handling.
        deferred_messages.append(message)

    combined = " ".join(parts).strip()

    return combined, deferred_messages


@app.websocket("/ws")
async def conversation_socket(
    websocket: WebSocket,
    scenario: str,
):
    await websocket.accept()

    data = get_scenario(scenario)

    patient = PatientAgent(data)

    transcript = Transcript(
        scenario_id=scenario,
    )

    pending_messages: list[dict] = []

    try:
        while True:

            # Process any events captured while collecting a fragmented
            # receptionist turn before waiting for another WebSocket event.
            if pending_messages:
                message = pending_messages.pop(0)

            else:
                raw = await websocket.receive_text()
                message = json.loads(raw)

            msg_type = message.get("type")

            # ---------------------------------------------------------
            # SETUP
            # ---------------------------------------------------------

            if msg_type == "setup":

                transcript.call_sid = message.get(
                    "callSid",
                    "unknown",
                )

                transcript.flush()

                continue

            # ---------------------------------------------------------
            # RECEPTIONIST SPEECH
            # ---------------------------------------------------------

            if msg_type == "prompt":

                if not message.get("last", True):
                    continue

                receptionist_text = message.get(
                    "voicePrompt",
                    "",
                ).strip()

                if not receptionist_text:
                    continue

                transcript.add(
                    "receptionist",
                    receptionist_text,
                )

                # Recording notices are not conversational turns.
                if is_disclosure(receptionist_text):
                    continue

                # Give the assessment receptionist a short opportunity
                # to finish a fragmented utterance.
                receptionist_text, deferred = await collect_receptionist_turn(
                    websocket,
                    receptionist_text,
                    transcript,
                )

                pending_messages.extend(deferred)

                if not receptionist_text:
                    continue

                # -----------------------------------------------------
                # Deterministic terminal-state protection
                # -----------------------------------------------------

                if is_hard_terminal(receptionist_text):

                    goodbye = "Thank you. Goodbye."

                    transcript.add(
                        "patient",
                        goodbye,
                    )

                    await websocket.send_json(
                        {
                            "type": "text",
                            "token": goodbye,
                            "last": True,
                            "interruptible": False,
                            "preemptible": False,
                        }
                    )

                    await asyncio.sleep(2.0)

                    await websocket.send_json(
                        {
                            "type": "end",
                            "handoffData": json.dumps(
                                {
                                    "reason": "remote_test_line_ended",
                                }
                            ),
                        }
                    )

                    break

                # -----------------------------------------------------
                # NORMAL PATIENT RESPONSE
                # -----------------------------------------------------

                patient_text, should_end = await patient.respond(
                    receptionist_text
                )

                if not patient_text:
                    continue

                transcript.add(
                    "patient",
                    patient_text,
                )

                await websocket.send_json(
                    {
                        "type": "text",
                        "token": patient_text,
                        "last": True,

                        # Do not let premature remote speech chop the
                        # patient's sentence in half.
                        "interruptible": False,

                        # Do not let a later application response replace
                        # the current patient response.
                        "preemptible": False,
                    }
                )

                # -----------------------------------------------------
                # NATURAL END
                # -----------------------------------------------------

                if should_end:

                    speech_seconds = min(
                        6.0,
                        max(
                            1.5,
                            len(patient_text.split()) / 2.4,
                        ),
                    )

                    await asyncio.sleep(
                        speech_seconds
                    )

                    await websocket.send_json(
                        {
                            "type": "end",
                            "handoffData": json.dumps(
                                {
                                    "reason": "scenario_complete",
                                }
                            ),
                        }
                    )

                    break

                continue

            # ---------------------------------------------------------
            # INTERRUPT
            # ---------------------------------------------------------

            if msg_type == "interrupt":

                transcript.add(
                    "system",
                    (
                        "Patient speech interrupted TTS after: "
                        + message.get(
                            "utteranceUntilInterrupt",
                            "",
                        )
                    ),
                    event="interrupt",
                )

                continue

            # ---------------------------------------------------------
            # DTMF
            # ---------------------------------------------------------

            if msg_type == "dtmf":

                transcript.add(
                    "system",
                    f"DTMF: {message.get('digit')}",
                    event="dtmf",
                )

                continue

            # ---------------------------------------------------------
            # CONVERSATIONRELAY ERROR
            # ---------------------------------------------------------

            if msg_type == "error":

                transcript.add(
                    "system",
                    message.get(
                        "description",
                        "ConversationRelay error",
                    ),
                    event="error",
                )

                continue

    except WebSocketDisconnect:
        pass

    finally:

        transcript.flush()

        if transcript.turns:

            try:
                await analyze_and_save(
                    transcript.scenario_id,
                    transcript.call_sid,
                    transcript.as_plain_text(),
                )

            except Exception as exc:

                transcript.add(
                    "system",
                    f"Post-call analysis failed: {exc}",
                    event="analysis_error",
                )

                transcript.flush()


@app.post("/recording-status")
async def recording_status(
    request: Request,
):

    form = await request.form()

    if form.get("RecordingStatus") != "completed":

        return {
            "ok": True,
            "status": form.get("RecordingStatus"),
        }

    recording_url = str(
        form.get(
            "RecordingUrl",
            "",
        )
    )

    recording_sid = str(
        form.get(
            "RecordingSid",
            "recording",
        )
    )

    call_sid = str(
        form.get(
            "CallSid",
            "call",
        )
    )

    if not recording_url:

        return {
            "ok": False,
            "reason": "missing RecordingUrl",
        }

    target = (
        RECORDING_DIR
        / f"{call_sid}_{recording_sid}.mp3"
    )

    async with httpx.AsyncClient(
        auth=(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
        ),
        timeout=60,
    ) as client:

        response = await client.get(
            recording_url + ".mp3"
        )

        response.raise_for_status()

        target.write_bytes(
            response.content
        )

    return {
        "ok": True,
        "saved": target.name,
    }