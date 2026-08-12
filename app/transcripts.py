from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_DIR = ROOT / "artifacts" / "transcripts"
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

_lock = Lock()

@dataclass
class Transcript:
    scenario_id: str
    call_sid: str = "pending"
    turns: list[dict] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add(self, speaker: str, text: str, event: str = "speech") -> None:
        text = (text or "").strip()
        if not text:
            return
        self.turns.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "speaker": speaker,
            "event": event,
            "text": text,
        })
        self.flush()

    @property
    def base_name(self) -> str:
        return f"{self.scenario_id}_{self.call_sid}"

    def flush(self) -> None:
        with _lock:
            txt_path = TRANSCRIPT_DIR / f"{self.base_name}.txt"
            json_path = TRANSCRIPT_DIR / f"{self.base_name}.json"
            lines = [
                f"Scenario: {self.scenario_id}",
                f"Call SID: {self.call_sid}",
                f"Started: {self.started_at}",
                "",
            ]
            for turn in self.turns:
                lines.append(f"[{turn['timestamp']}] {turn['speaker'].upper()}: {turn['text']}")
            txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            json_path.write_text(json.dumps({
                "scenario_id": self.scenario_id,
                "call_sid": self.call_sid,
                "started_at": self.started_at,
                "turns": self.turns,
            }, indent=2), encoding="utf-8")

    def as_plain_text(self) -> str:
        return "\n".join(f"{t['speaker']}: {t['text']}" for t in self.turns)
