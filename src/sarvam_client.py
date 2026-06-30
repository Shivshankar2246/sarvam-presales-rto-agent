"""Thin, transparent wrapper over the four Sarvam APIs used by Sampark.

Design choices:
- Chat/LLM goes through the OpenAI SDK pointed at Sarvam's OpenAI-compatible
  endpoint (https://api.sarvam.ai/v1). This gives us battle-tested tool-calling.
- STT / TTS / Translate use plain `requests` against the documented REST
  endpoints — transparent, no SDK-signature surprises, easy to read in review.

Every method mirrors a method on MockSarvamClient (src/mocks/mock_sarvam.py) so the
agent code is identical whether we're hitting the real API or running offline.

Sources for every endpoint/field: _research/sarvam-api-reference.md
"""
from __future__ import annotations

import base64
from typing import Any

import requests

from config import (
    CHAT_MODEL,
    SARVAM_BASE_URL,
    SARVAM_OPENAI_BASE_URL,
    STT_MODEL,
    TRANSLATE_MODEL,
    TTS_MODEL,
    settings,
    speaker_for,
)


class SarvamClient:
    """Real Sarvam API client. Requires SARVAM_API_KEY."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.api_key
        if not self.api_key:
            raise ValueError(
                "SARVAM_API_KEY is required for the real client. "
                "Get one (₹100 free credits) at https://dashboard.sarvam.ai"
            )
        self._headers = {"api-subscription-key": self.api_key}
        self._openai = None  # lazy — only import openai when chat is actually used

    # ---- Speech-to-Text (Saaras) -------------------------------------------------
    def transcribe(self, audio_bytes: bytes, language_code: str = "unknown") -> dict[str, Any]:
        """POST /speech-to-text (multipart). Returns {transcript, language_code}.

        mode=codemix keeps Hinglish/Tanglish faithful instead of forcing one script.
        """
        resp = requests.post(
            f"{SARVAM_BASE_URL}/speech-to-text",
            headers=self._headers,
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={"model": STT_MODEL, "mode": "codemix", "language_code": language_code},
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        return {
            "transcript": body.get("transcript", ""),
            "language_code": body.get("language_code") or language_code,
        }

    # ---- Text-to-Speech (Bulbul) -------------------------------------------------
    def synthesize(self, text: str, language_code: str, speaker: str | None = None) -> bytes:
        """POST /text-to-speech (JSON). Returns decoded WAV bytes ready to play."""
        payload = {
            "text": text[:2500],  # bulbul:v3 hard cap
            "target_language_code": language_code,
            "model": TTS_MODEL,
            "speaker": speaker or speaker_for(language_code),
            "speech_sample_rate": 22050,
            "output_audio_codec": "wav",
        }
        resp = requests.post(
            f"{SARVAM_BASE_URL}/text-to-speech",
            headers={**self._headers, "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        audios = resp.json().get("audios", [])
        if not audios:
            return b""
        return base64.b64decode(audios[0])

    # ---- Chat / LLM (sarvam-30b) via OpenAI-compatible endpoint ------------------
    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "auto",
        temperature: float = 0.2,
    ) -> Any:
        """POST /v1/chat/completions. Returns the OpenAI-style response object.

        Tool-calling is the whole point: the model decides when to reschedule,
        fix an address, convert to prepaid, or cancel.
        """
        if self._openai is None:
            from openai import OpenAI  # imported lazily

            self._openai = OpenAI(api_key=self.api_key, base_url=SARVAM_OPENAI_BASE_URL)

        kwargs: dict[str, Any] = {
            "model": CHAT_MODEL,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        return self._openai.chat.completions.create(**kwargs)

    # ---- Translate (Mayura) — normalize transcripts to English for ops/CRM ------
    def translate(self, text: str, target_language_code: str = "en-IN",
                  source_language_code: str = "auto") -> str:
        """POST /translate. Used to render dispositions in English for the ops team."""
        resp = requests.post(
            f"{SARVAM_BASE_URL}/translate",
            headers={**self._headers, "Content-Type": "application/json"},
            json={
                "input": text[:1000],
                "source_language_code": source_language_code,
                "target_language_code": target_language_code,
                "model": TRANSLATE_MODEL,
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json().get("translated_text", "")


def get_client():
    """Return a real or mock client based on config — the rest of the app is agnostic."""
    if settings.use_mock:
        from mocks.mock_sarvam import MockSarvamClient

        return MockSarvamClient()
    return SarvamClient()
