from __future__ import annotations

import argparse
import time
from urllib.parse import quote

from twilio.rest import Client

from app.config import settings, ASSESSMENT_NUMBER
from app.scenario_store import load_scenarios, get_scenario


def make_call(client: Client, scenario_id: str):
    # Hard safety guard: this challenge runner can call exactly one destination.
    if settings.pgai_test_number != ASSESSMENT_NUMBER:
        raise RuntimeError(f"Refusing to call any number except {ASSESSMENT_NUMBER}")

    voice_url = f"{settings.public_base_url}/voice?scenario={quote(scenario_id)}"
    recording_callback = f"{settings.public_base_url}/recording-status"
    call = client.calls.create(
        to=ASSESSMENT_NUMBER,
        from_=settings.twilio_phone_number,
        url=voice_url,
        method="POST",
        record=True,
        recording_channels="dual",
        recording_status_callback=recording_callback,
        recording_status_callback_event=["completed"],
        timeout=30,
        time_limit=210,
    )
    print(f"Started {scenario_id}: {call.sid}")
    return call.sid


def wait_for_completion(client: Client, sid: str, poll_seconds: int = 4, max_seconds: int = 300):
    started = time.monotonic()
    while time.monotonic() - started < max_seconds:
        call = client.calls(sid).fetch()
        if call.status in {"completed", "busy", "failed", "no-answer", "canceled"}:
            print(f"Finished {sid}: {call.status}, duration={call.duration}s")
            return call.status
        time.sleep(poll_seconds)
    print(f"Timed out waiting for {sid}; check Twilio console.")
    return "timeout"


def main():
    parser = argparse.ArgumentParser(description="Run Pretty Good AI voice challenge scenarios")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Run all ten scenarios sequentially")
    group.add_argument("--scenario", help="Run one scenario ID")
    parser.add_argument("--pause", type=int, default=8, help="Seconds between completed calls")
    args = parser.parse_args()

    settings.validate()
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    scenarios = load_scenarios() if args.all else [get_scenario(args.scenario)]
    print(f"Destination locked to assessment number: {ASSESSMENT_NUMBER}")
    print(f"Caller number: {settings.twilio_phone_number}")

    for index, scenario in enumerate(scenarios, start=1):
        print(f"\n[{index}/{len(scenarios)}] {scenario['id']} | {scenario['title']}")
        sid = make_call(client, scenario["id"])
        wait_for_completion(client, sid)
        if index < len(scenarios):
            time.sleep(args.pause)


if __name__ == "__main__":
    main()
