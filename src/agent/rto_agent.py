"""RTOAgent — the brain of the call.

Holds the conversation with sarvam-30b, lets the model call tools, executes them
via the n8n backend, and tracks the final disposition. Works identically against the
real Sarvam client and the offline mock (their response objects share a shape).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from agent.tools import TOOLS, ToolExecutor, tool_result_message

log = logging.getLogger("sampark.agent")

TOOL_NAMES = {t["function"]["name"] for t in TOOLS}

# Fixed, guaranteed-in-language opening line (production voice agents use a scripted
# greeting; it also guarantees the call opens in the right language and saves an API call).
GREETINGS = {
    "hi-IN": "नमस्ते {name} जी, मैं रिवायत से मीरा बोल रही हूँ। आपका ऑर्डर आज डिलीवरी के लिए निकला है — क्या आप डिलीवरी के लिए उपलब्ध रहेंगे?",
    "ta-IN": "வணக்கம் {name}, நான் ரிவாயத்-ல் இருந்து மீரா பேசுறேன். உங்க ஆர்டர் இன்னைக்கு டெலிவரிக்கு வந்துருக்கு — நீங்க வீட்ல இருப்பீங்களா?",
    "en-IN": "Hello {name}, this is Meera from Rivaayat. Your order is out for delivery today — will you be available to receive it?",
}


class RTOAgent:
    def __init__(self, client, order: dict[str, Any]):
        self.client = client
        self.order = order
        self.executor = ToolExecutor(order)
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": self._system_prompt()}]
        self.transcript: list[tuple[str, str]] = []  # (speaker, text)
        self.disposition = "IN_PROGRESS"
        self.tool_log: list[dict[str, Any]] = []

    # ---- public API --------------------------------------------------------------
    def greeting(self) -> str:
        """First thing the agent says when the call connects — a fixed, in-language line."""
        lang = self.order.get("language_code", "en-IN")
        name = (self.order.get("customer_name") or "").split()[0]
        template = GREETINGS.get(lang, GREETINGS["en-IN"])
        text = template.format(name=name)
        self.messages.append({"role": "assistant", "content": text})
        self.transcript.append(("agent", text))
        return text

    def respond(self, customer_text: str) -> str:
        """Feed a customer utterance, return the agent's spoken reply."""
        self.messages.append({"role": "user", "content": customer_text})
        self.transcript.append(("customer", customer_text))
        return self._next_assistant_turn()

    @property
    def is_done(self) -> bool:
        return self.disposition not in ("IN_PROGRESS", "CALLBACK_SCHEDULED")

    def outcome(self) -> dict[str, Any]:
        """Structured disposition handed back to n8n for downstream fan-out."""
        return {
            "order_id": self.order.get("order_id"),
            "language": self.order.get("language_code"),
            "disposition": self.disposition,
            "tools_called": self.tool_log,
            "transcript": [{"speaker": s, "text": t} for s, t in self.transcript],
        }

    def finalize(self) -> str:
        """End-of-call safety net: if the call is ending unresolved, force the model to
        classify the outcome into exactly one tool. This is a legitimate production
        pattern (always record a disposition) and makes the demo robust to a model that
        chatted without committing."""
        if self.is_done:
            return ""
        self.messages.append({
            "role": "user",
            "content": "(The call is ending. Based on what the customer agreed to, call the "
                       "single matching tool now to record the outcome. If nothing was resolved, "
                       "call schedule_callback.)",
        })
        try:
            resp = self.client.chat(self.messages, tools=TOOLS, tool_choice="required", temperature=0.0)
            msg = resp.choices[0].message
            if getattr(msg, "tool_calls", None):
                self.messages.append(self._assistant_with_tools(msg))
                for tc in msg.tool_calls:
                    self._run_tool(tc)
        except Exception as e:  # never let finalize crash the demo
            log.warning("finalize failed: %s", e)
        return ""

    # ---- internals ---------------------------------------------------------------
    def _next_assistant_turn(self) -> str:
        """Run chat; if the model calls tools, execute them and get the verbal follow-up."""
        spoken: list[str] = []
        for _ in range(5):  # guard against runaway tool loops
            resp = self.client.chat(self.messages, tools=TOOLS, temperature=0.0)
            msg = resp.choices[0].message
            tool_calls = getattr(msg, "tool_calls", None)

            if tool_calls:
                self.messages.append(self._assistant_with_tools(msg))
                if msg.content:
                    spoken.append(msg.content)
                    self.transcript.append(("agent", msg.content))
                for tc in tool_calls:
                    self._run_tool(tc)
                continue  # loop again for the closing confirmation

            text = (msg.content or "").strip()

            # Fallback: some models emit the tool as TEXT (a bare name or JSON) instead of a
            # proper tool call. Detect it and force a real, structured tool call.
            forced = self._detect_text_tool(text)
            if forced and not self.is_done:
                if self._force_tool(forced):
                    continue  # loop for the spoken confirmation; suppress the leaked text

            self.messages.append({"role": "assistant", "content": text})
            if text:
                spoken.append(text)
                self.transcript.append(("agent", text))
            break
        return "\n".join(spoken)

    @staticmethod
    def _detect_text_tool(content: str) -> str | None:
        """Return a tool name if the model leaked one into its text reply, else None."""
        c = (content or "").strip()
        if not c:
            return None
        if c in TOOL_NAMES:
            return c
        for n in TOOL_NAMES:  # e.g. "update_address(...)" or "update_address {...}"
            if re.match(rf"^{n}\b", c):
                return n
        if c.startswith("{"):  # a JSON tool call dumped into content
            try:
                obj = json.loads(c)
                nm = obj.get("name") or obj.get("tool") or obj.get("function")
                if nm in TOOL_NAMES:
                    return nm
            except json.JSONDecodeError:
                pass
        return None

    def _force_tool(self, name: str) -> bool:
        """Force one specific structured tool call so we get proper arguments."""
        try:
            resp = self.client.chat(
                self.messages,
                tools=TOOLS,
                tool_choice={"type": "function", "function": {"name": name}},
                temperature=0.0,
            )
            msg = resp.choices[0].message
            if getattr(msg, "tool_calls", None):
                self.messages.append(self._assistant_with_tools(msg))
                for tc in msg.tool_calls:
                    self._run_tool(tc)
                return True
        except Exception as e:
            log.warning("_force_tool(%s) failed: %s", name, e)
        return False

    def _run_tool(self, tc) -> None:
        try:
            args = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        args.setdefault("order_id", self.order.get("order_id"))
        result = self.executor.execute(tc.function.name, args)
        self.disposition = result["disposition"]
        self.tool_log.append({"tool": tc.function.name, "args": args, "result": result})
        self.messages.append(tool_result_message(tc.id, result))

    @staticmethod
    def _assistant_with_tools(msg) -> dict[str, Any]:
        return {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        }

    def _system_prompt(self) -> str:
        o = self.order
        return (
            "You are Meera, an outbound delivery-confirmation agent calling on behalf of "
            "Rivaayat, a D2C ethnic-wear brand.\n\n"
            "CALL CONTEXT (never invent details — use only these):\n"
            f"- order_id={o['order_id']}\n"
            f"- Customer: {o['customer_name']}\n"
            f"- Language: speak ONLY in {o['language_code']} ({o.get('language_name','')}). "
            "Code-mixing (Hinglish/Tanglish) is fine if it sounds natural.\n"
            f"- Item: {o['item']}\n"
            f"- COD amount: Rs {o['cod_amount']}\n"
            f"- Address on file: {o['address']}\n"
            f"- Status: {o['status']}\n\n"
            "YOUR GOAL: make this delivery succeed and prevent an RTO (return-to-origin). Greet briefly, "
            "then listen for the ONE issue the customer raises and resolve it fast. The four common "
            "issues and the EXACT tool to call for each:\n"
            "- No cash / wants to pay online / asks for UPI  ->  call convert_to_prepaid (you send a UPI link on WhatsApp).\n"
            "- Won't be available / gives another day or time ->  call reschedule_delivery with that slot.\n"
            "- Address is wrong or incomplete                 ->  call update_address with the correction.\n"
            "- Doesn't want the order anymore                 ->  call cancel_order with the reason.\n\n"
            "TOOL-CALLING — THE MOST IMPORTANT RULE: the MOMENT the customer agrees to a resolution, "
            "CALL THE MATCHING TOOL in that same turn. Actually invoke the tool — do NOT just describe "
            "the action in words, and NEVER write JSON or a function call into your spoken reply. After "
            "the tool runs you'll give ONE short spoken confirmation. Don't keep asking extra questions "
            "once the issue is resolved.\n\n"
            "STYLE — CRITICAL (your reply is spoken aloud by a text-to-speech engine):\n"
            f"- Speak ONLY in {o['language_code']} ({o.get('language_name','')}). Your VERY FIRST "
            "line and EVERY line must be in this language. Never reply in English. (Loanwords "
            "people actually say out loud — 'UPI', 'WhatsApp', 'link', 'COD', 'order' — are fine inline.)\n"
            "- Output ONLY the words to be spoken. NO markdown, NO bullet points, NO asterisks (*), "
            "NO emojis, NO 'Meera:' or any name prefix, NO headings. Plain spoken sentences only.\n"
            "- Keep each turn to ONE or TWO short sentences, and ask ONE thing at a time. "
            "This is a quick phone call, not an email.\n\n"
            "RULES:\n"
            "- Be warm, respectful, efficient.\n"
            "- The moment a resolution is clear, CALL THE MATCHING TOOL, then give one short spoken confirmation.\n"
            f"- Always pass order_id={o['order_id']} to tools.\n"
            "- Never invent order details — use only the context above.\n"
            "- If the customer is angry, confused, or it's a high-value edge case, call escalate_to_human."
        )
