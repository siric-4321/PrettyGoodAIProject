from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = ROOT / "scenarios" / "scenarios.json"


def load_scenarios() -> list[dict]:
    return json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))


def get_scenario(scenario_id: str) -> dict:
    for scenario in load_scenarios():
        if scenario["id"] == scenario_id:
            return scenario
    raise KeyError(f"Unknown scenario: {scenario_id}")
