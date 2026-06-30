"""Central configuration for Project Sampark.

All Sarvam model ids, endpoints, and runtime toggles live here so the rest of the
code never hard-codes a model name. Values are read from the environment (.env);
sensible defaults let the repo run out-of-the-box in MOCK mode without a key.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # python-dotenv optional; env can be set by the shell
    pass


# --- Sarvam API (verified June 2026 — see docs/../_research/sarvam-api-reference.md) ---
SARVAM_BASE_URL = "https://api.sarvam.ai"
SARVAM_OPENAI_BASE_URL = "https://api.sarvam.ai/v1"  # OpenAI-compatible (chat + tools)

# Model ids. sarvam-m is DEPRECATED — do not use. 30b = low-latency voice loop.
CHAT_MODEL = os.getenv("SARVAM_CHAT_MODEL", "sarvam-30b")      # or sarvam-105b
STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v3")
TTS_MODEL = os.getenv("SARVAM_TTS_MODEL", "bulbul:v3")
TRANSLATE_MODEL = os.getenv("SARVAM_TRANSLATE_MODEL", "mayura:v1")


@dataclass
class Settings:
    api_key: str = field(default_factory=lambda: os.getenv("SARVAM_API_KEY", ""))
    # n8n agentic backend webhook the tools call to fan out downstream.
    n8n_webhook_url: str = field(default_factory=lambda: os.getenv("N8N_WEBHOOK_URL", ""))
    # Force mock even if a key is present (handy for offline demos / CI).
    force_mock: bool = field(
        default_factory=lambda: os.getenv("USE_MOCK", "").lower() in ("1", "true", "yes")
    )

    @property
    def use_mock(self) -> bool:
        """Mock when explicitly forced OR when no API key is configured."""
        return self.force_mock or not self.api_key


settings = Settings()


# Default Bulbul (TTS) voice per language. anushka/abhilash exist on v2 & are safe
# fallbacks; v3 adds many more (see _research/sarvam-api-reference.md §3).
DEFAULT_SPEAKER = {
    "hi-IN": "anushka",
    "ta-IN": "vidya",
    "te-IN": "vidya",
    "bn-IN": "anushka",
    "kn-IN": "vidya",
    "ml-IN": "vidya",
    "mr-IN": "anushka",
    "gu-IN": "anushka",
    "pa-IN": "anushka",
    "od-IN": "anushka",
    "en-IN": "anushka",
}


def speaker_for(language_code: str) -> str:
    return DEFAULT_SPEAKER.get(language_code, "anushka")
