from __future__ import annotations

import asyncio
from pathlib import Path
from openai import OpenAI

from .config import settings

ROOT = Path(__file__).resolve().parents[1]
BUG_DIR = ROOT / "artifacts" / "bug_reports"
BUG_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_PROMPT = """
You are a rigorous QA analyst reviewing a phone conversation between a simulated patient and a healthcare practice AI receptionist.
Find only meaningful product bugs or quality issues. Prefer a few strong findings over nitpicks.

Check for:
- incorrect scheduling behavior or contradictions
- failure to clarify ambiguous dates or requests
- hallucinated hours, insurance, policies, availability, or confirmations
- loss of conversation state or ignored corrections
- failure to complete the user's intent
- awkward turn taking, repeated questions, bad interruption handling, or severe latency symptoms visible in the transcript
- unsafe or inappropriate administrative/medical behavior

For each real issue, output this format:
### [Severity: High|Medium|Low] Short bug title
**Evidence:** quote or tightly paraphrase the relevant exchange
**Why it matters:** concrete user impact
**Expected behavior:** what a better agent should do

If there is no defensible bug, write: "No material bug found in this call." Then add up to two useful quality observations.
Do not invent facts that are not present in the transcript.
""".strip()

async def analyze_and_save(scenario_id: str, call_sid: str, transcript_text: str) -> Path:
    client = OpenAI(api_key=settings.openai_api_key)

    def _call() -> str:
        response = client.responses.create(
            model=settings.openai_model,
            instructions=ANALYSIS_PROMPT,
            input=f"Scenario: {scenario_id}\nCall SID: {call_sid}\n\nTRANSCRIPT\n{transcript_text}",
        )
        return response.output_text.strip()

    result = await asyncio.to_thread(_call)
    path = BUG_DIR / f"{scenario_id}_{call_sid}.md"
    path.write_text(
        f"# Call QA Analysis\n\n**Scenario:** {scenario_id}\n\n**Call SID:** {call_sid}\n\n{result}\n",
        encoding="utf-8",
    )
    return path
