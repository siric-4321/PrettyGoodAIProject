from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

ASSESSMENT_NUMBER = "+18054398008"

@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    public_ws_url: str = os.getenv("PUBLIC_WS_URL", "").rstrip("/")
    pgai_test_number: str = os.getenv("PGAI_TEST_NUMBER", ASSESSMENT_NUMBER)

    def validate(self) -> None:
        required = {
            "OPENAI_API_KEY": self.openai_api_key,
            "TWILIO_ACCOUNT_SID": self.twilio_account_sid,
            "TWILIO_AUTH_TOKEN": self.twilio_auth_token,
            "TWILIO_PHONE_NUMBER": self.twilio_phone_number,
            "PUBLIC_BASE_URL": self.public_base_url,
            "PUBLIC_WS_URL": self.public_ws_url,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
        if self.pgai_test_number != ASSESSMENT_NUMBER:
            raise RuntimeError(
                f"Safety check failed: PGAI_TEST_NUMBER must remain {ASSESSMENT_NUMBER} for this assessment."
            )
        if not self.twilio_phone_number.startswith("+"):
            raise RuntimeError("TWILIO_PHONE_NUMBER must be in E.164 format, for example +15551234567")
        if not self.public_base_url.startswith("https://"):
            raise RuntimeError("PUBLIC_BASE_URL must use https://")
        if not self.public_ws_url.startswith("wss://"):
            raise RuntimeError("PUBLIC_WS_URL must use wss://")

settings = Settings()
