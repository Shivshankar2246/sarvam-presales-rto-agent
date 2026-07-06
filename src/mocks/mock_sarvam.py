"""Offline mock of SarvamClient.

Purpose: the repo must run end-to-end for a reviewer who hasn't added an API key
yet. This mock mirrors SarvamClient's interface exactly and ships a small,
keyword-driven scripted agent that reproduces the three demo scenarios
(COD->prepaid, reschedule, address-fix) in Hindi / Tamil / English.

The moment a real SARVAM_API_KEY is present, src/sarvam_client.get_client()
returns the REAL client instead and none of this code runs.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any


# --- Minimal objects that mimic the OpenAI chat-completion response shape ---------
@dataclass
class _Func:
    name: str
    arguments: str


@dataclass
class _ToolCall:
    function: _Func
    id: str = field(default_factory=lambda: f"call_{uuid.uuid4().hex[:8]}")
    type: str = "function"


@dataclass
class _Msg:
    role: str = "assistant"
    content: str | None = None
    tool_calls: list[_ToolCall] | None = None


@dataclass
class _Choice:
    message: _Msg


@dataclass
class _Resp:
    choices: list[_Choice]
    usage: dict[str, int] = field(default_factory=lambda: {"total_tokens": 0})


# --- Canned, localized copy for the three scripted scenarios -----------------------
GREETING = {
    "hi-IN": "नमस्ते, मैं ज़िवा से मीरा बोल रही हूँ। आपका ऑर्डर आज डिलीवरी के लिए निकला है। क्या आप घर पर रहेंगे?",
    "ta-IN": "வணக்கம், நான் ஜிவா-ல் இருந்து மீரா பேசுறேன். உங்க ஆர்டர் இன்னைக்கு டெலிவரிக்கு வந்துருக்கு. நீங்க வீட்ல இருப்பீங்களா?",
    "en-IN": "Hi, this is Meera from Zivaa. Your order is out for delivery today. Will you be home to receive it?",
}

TOOL_REPLY = {
    "convert_to_prepaid": {
        "hi-IN": "कोई बात नहीं! मैं आपके लिए फ्री शिपिंग लगा देती हूँ और अभी WhatsApp पर एक UPI लिंक भेज रही हूँ — GPay या PhonePe से अभी पे कर दीजिए, ऑर्डर आज ही निकल जाएगा और डिलीवरी के वक़्त कैश की ज़रूरत नहीं।",
        "ta-IN": "பரவாயில்லை! உங்களுக்கு இலவச ஷிப்பிங் போட்டு, இப்பவே WhatsApp-ல ஒரு UPI லிங்க் அனுப்புறேன் — GPay அல்லது PhonePe-ல இப்பவே பணம் கட்டிடுங்க, ஆர்டர் இன்னைக்கே கிளம்பிடும், டெலிவரி நேரத்துல காசு தேவையில்ல.",
        "en-IN": "No problem! I'll add free shipping and send a UPI link on WhatsApp now — pay via GPay or PhonePe and your order ships today, with no cash needed at the door.",
    },
    "reschedule_delivery": {
        "hi-IN": "कोई बात नहीं! मैं कल दोपहर के लिए डिलीवरी रीशेड्यूल कर देती हूँ।",
        "ta-IN": "பரவாயில்லை! நாளைக்கு மதியம் டெலிவரி ரீஸ்கெட்யூல் பண்றேன்.",
        "en-IN": "No problem! I'll reschedule the delivery for tomorrow afternoon.",
    },
    "update_address": {
        "hi-IN": "ठीक है, मैं पता अपडेट कर देती हूँ — दूसरी मंज़िल, ब्लू गेट के सामने। डिलीवरी आज ही हो जाएगी।",
        "ta-IN": "சரி, முகவரியை அப்டேட் பண்றேன் — இரண்டாவது மாடி, ப்ளூ கேட் எதிரில.",
        "en-IN": "Got it, I'll update the address — second floor, opposite the blue gate. Delivery will happen today.",
    },
    "cancel_order": {
        "hi-IN": "ठीक है, मैं ऑर्डर कैंसिल कर देती हूँ। समय देने के लिए धन्यवाद।",
        "ta-IN": "சரி, ஆர்டரை கேன்சல் பண்றேன். உங்க நேரத்துக்கு நன்றி.",
        "en-IN": "Alright, I'll cancel the order. Thank you for your time.",
    },
}

CLOSING = {
    "hi-IN": "हो गया! धन्यवाद, आपका दिन शुभ हो।",
    "ta-IN": "முடிஞ்சது! நன்றி, உங்களுக்கு நல்ல நாள்.",
    "en-IN": "All done! Thank you, have a great day.",
}

TOOL_ARGS = {
    "convert_to_prepaid": lambda oid: {"order_id": oid},
    "reschedule_delivery": lambda oid: {"order_id": oid, "preferred_slot": "tomorrow 12-3pm"},
    "update_address": lambda oid: {
        "order_id": oid,
        "corrected_address": "2nd floor (was marked ground floor)",
        "landmark": "opposite the blue gate",
    },
    "cancel_order": lambda oid: {"order_id": oid, "reason": "customer changed their mind"},
}


def _detect_tool(text: str) -> str | None:
    """Very small intent router for the offline demo."""
    t = text.lower()

    def has(*words: str) -> bool:
        return any(w in t for w in words) or any(w in text for w in words)

    if has("cancel", "nahi chahiye", "don't want", "dont want", "mat bhejo", "return kar", "रद्द"):
        return "cancel_order"
    if has("address", "galat", "wrong", "floor", "landmark", "gate", "gali", "पता", "second floor", "blue gate"):
        return "update_address"
    if has("cash nahi", "no cash", "nahi hai", "paise nahi", "upi", "online", "card", "nakad",
           "कैश नहीं", "नहीं है", "don't have cash", "no money"):
        return "convert_to_prepaid"
    if has("not available", "reschedule", "tomorrow", "kal", "baad", "busy", "out of town",
           "travel", "ooru", "ஊர்", "நாளை", "ghar pe nahi", "nahi rahunga", "नहीं रहूँगा"):
        return "reschedule_delivery"
    return None


class MockSarvamClient:
    """Drop-in stand-in for SarvamClient when no API key is configured."""

    is_mock = True

    # ---- STT ----
    def transcribe(self, audio_bytes: bytes, language_code: str = "unknown") -> dict[str, Any]:
        return {
            "transcript": "[mock STT — no audio decoded; run with a SARVAM_API_KEY for real STT]",
            "language_code": language_code,
        }

    # ---- TTS ----
    def synthesize(self, text: str, language_code: str, speaker: str | None = None) -> bytes:
        # No audio in mock — the CLI prints the spoken line instead.
        return b""

    # ---- Chat (scripted) ----
    def chat(self, messages, tools=None, tool_choice="auto", temperature=0.2):
        # Post-call analytics requests get a deterministic JSON answer (offline-friendly).
        if any(isinstance(m, dict) and "POST_CALL_ANALYTICS" in (m.get("content") or "")
               for m in messages):
            return _Resp([_Choice(_Msg(content=self._analytics_json(messages)))])

        lang = self._lang_from_system(messages)
        order_id = self._order_id_from_system(messages)
        last = messages[-1]

        # After a tool executed, the executor appended its result -> give a closing line.
        if isinstance(last, dict) and last.get("role") == "tool":
            return _Resp([_Choice(_Msg(content=CLOSING.get(lang, CLOSING["en-IN"])))])

        # First assistant turn -> greeting.
        assistant_turns = sum(
            1 for m in messages if (m.get("role") if isinstance(m, dict) else None) == "assistant"
        )
        if assistant_turns == 0:
            return _Resp([_Choice(_Msg(content=GREETING.get(lang, GREETING["en-IN"])))])

        # Otherwise route the customer's latest line to a tool, if any.
        user_text = last.get("content", "") if isinstance(last, dict) else ""
        tool = _detect_tool(user_text or "")
        if tool:
            tc = _ToolCall(function=_Func(name=tool, arguments=json.dumps(TOOL_ARGS[tool](order_id))))
            return _Resp([_Choice(_Msg(content=TOOL_REPLY[tool].get(lang, TOOL_REPLY[tool]["en-IN"]),
                                       tool_calls=[tc]))])

        # No clear intent -> a gentle clarifying nudge.
        nudge = {
            "hi-IN": "जी, कृपया बताइए — क्या आप डिलीवरी के समय घर पर रहेंगे?",
            "ta-IN": "சரி, தயவுசெய்து சொல்லுங்க — டெலிவரி நேரத்துல வீட்ல இருப்பீங்களா?",
            "en-IN": "Sure — just to confirm, will you be home at the delivery time?",
        }
        return _Resp([_Choice(_Msg(content=nudge.get(lang, nudge["en-IN"])))])

    # ---- Translate ----
    def translate(self, text, target_language_code="en-IN", source_language_code="auto"):
        return f"[mock-translate→{target_language_code}] {text}"

    # ---- analytics (deterministic, offline) ----
    def _analytics_json(self, messages) -> str:
        text = " ".join(
            m.get("content", "") for m in messages
            if isinstance(m, dict) and m.get("role") == "user"
        )
        tool = _detect_tool(text)
        mapping = {
            "convert_to_prepaid": dict(disposition="CONVERTED_PREPAID", rto_cause="COD cash not ready",
                                       objection="no cash on hand", prepaid_offered=True, prepaid_accepted=True,
                                       summary_en="Customer had no cash; agent converted the COD order to UPI prepaid."),
            "reschedule_delivery": dict(disposition="RESCHEDULED", rto_cause="customer unavailable",
                                        objection="not available at delivery time", prepaid_offered=False,
                                        prepaid_accepted=False,
                                        summary_en="Customer was unavailable; delivery rescheduled to a confirmed slot."),
            "update_address": dict(disposition="ADDRESS_FIXED", rto_cause="incomplete/incorrect address",
                                   objection="address needs correction", prepaid_offered=False, prepaid_accepted=False,
                                   summary_en="Address was incomplete; agent captured the correction on the call."),
            "cancel_order": dict(disposition="CANCELLED", rto_cause="customer changed mind",
                                 objection="no longer wants the order", prepaid_offered=False, prepaid_accepted=False,
                                 summary_en="Customer no longer wanted the order; cancelled to avoid a guaranteed return."),
        }
        base = mapping.get(tool, dict(disposition="UNKNOWN", rto_cause="unclear", objection="none",
                                      prepaid_offered=False, prepaid_accepted=False,
                                      summary_en="Call outcome unclear from transcript."))
        lang = ("ta-IN" if any("஀" <= c <= "௿" for c in text)
                else "hi-IN" if any("ऀ" <= c <= "ॿ" for c in text)
                else "en-IN")
        return json.dumps({**base, "sentiment": "positive", "language": lang}, ensure_ascii=False)

    # ---- helpers ----
    @staticmethod
    def _lang_from_system(messages) -> str:
        for m in messages:
            role = m.get("role") if isinstance(m, dict) else None
            if role == "system":
                sys = m.get("content", "")
                for code in ("hi-IN", "ta-IN", "te-IN", "bn-IN", "kn-IN", "ml-IN", "mr-IN", "en-IN"):
                    if code in sys:
                        return code
        return "en-IN"

    @staticmethod
    def _order_id_from_system(messages) -> str:
        for m in messages:
            role = m.get("role") if isinstance(m, dict) else None
            if role == "system" and "order_id=" in (m.get("content", "")):
                seg = m["content"].split("order_id=", 1)[1]
                return seg.split()[0].strip(".,)")
        return "ORD-MOCK"
