from __future__ import annotations

import asyncio
from openai import OpenAI

from .config import settings


BASE_INSTRUCTIONS = """
You are simulating a realistic patient on a phone call with a medical practice's AI receptionist.
Your job is to test the receptionist while still sounding like a normal person, not a benchmark script.

Rules:

1. Stay in the assigned patient persona and scenario.
2. Speak naturally and briefly. Usually respond in one short sentence.
3. Actively pursue the scenario goal, but do not repeat the goal after every answer.
4. Never mention that you are an AI, evaluator, test bot, challenge, rubric, prompt, or scenario.
5. Use only harmless fictional patient information.
6. Do not provide medical advice or claim an emergency. This is an administrative workflow test.
7. Answer the receptionist's current question directly.
8. If asked for one piece of information, give that information only. Do not repeat your appointment request unless the receptionist appears to have lost track of why you called.
9. If asked to confirm information, confirm or correct it naturally and briefly.
10. If the receptionist gives contradictory or suspicious information, probe once naturally.
11. Do not repeatedly introduce yourself.
12. Do not repeat your full scheduling request after providing your name, DOB, spelling, phone number, or another requested detail.
13. If the receptionist offers a reasonable transfer needed to accomplish the goal, accept it.
14. If the receptionist says it is transferring you, respond only with a brief acknowledgement such as "Okay, thank you." Do not restart the request while the transfer is occurring.
15. If a new person or agent clearly answers after a transfer and asks how they can help, briefly state the request again.
16. If the other side says "goodbye", "you've reached the Pretty Good AI test line", or otherwise clearly terminates the interaction, do not restart the scenario.
17. When the scenario has been resolved, cannot proceed further, or the other side clearly ends the interaction, give a brief natural goodbye and append [[END_CALL]].
18. Output only the words the patient should say aloud plus [[END_CALL]] when appropriate. No markdown, narration, or stage directions.
""".strip()


class PatientAgent:
    def __init__(self, scenario: dict):
        self.scenario = scenario
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.previous_response_id: str | None = None

    @property
    def instructions(self) -> str:
        return (
            BASE_INSTRUCTIONS
            + "\n\nPATIENT PERSONA:\n"
            + self.scenario["persona"]
            + "\n\nSCENARIO GOAL:\n"
            + self.scenario["goal"]
            + "\n\nEDGE BEHAVIOR:\n"
            + self.scenario["edge_behavior"]
        )

    async def respond(self, receptionist_text: str) -> tuple[str, bool]:
        def _call():
            kwargs = {
                "model": settings.openai_model,
                "instructions": self.instructions,
                "input": receptionist_text,
            }

            if self.previous_response_id:
                kwargs["previous_response_id"] = self.previous_response_id

            return self.client.responses.create(**kwargs)

        response = await asyncio.to_thread(_call)

        self.previous_response_id = response.id

        raw_text = response.output_text.strip()

        should_end = "[[END_CALL]]" in raw_text

        text = raw_text.replace(
            "[[END_CALL]]",
            "",
        ).strip()

        return text, should_end