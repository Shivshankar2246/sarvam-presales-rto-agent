"""RTOAgent — the brain of the call.

Holds the conversation with sarvam-30b, lets the model call tools, executes them
via the n8n backend, and tracks the final disposition. Works identically against the
real Sarvam client and the offline mock (their response objects share a shape).
"""
from __future__ import annotations

import json
import logging
from typing import Any

from agent.tools import TOOLS, ToolExecutor, tool_result_message

log = logging.getLogger("sampark.agent")


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
        """First thing the agent says when the call connects."""
        return self._next_assistant_turn()

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

    # ---- internals ---------------------------------------------------------------
    def _next_assistant_turn(self) -> str:
        """Run chat; if the model calls tools, execute them and get the verbal follow-up."""
        spoken: list[str] = []
        for _ in range(5):  # guard against runaway tool loops
            resp = self.client.chat(self.messages, tools=TOOLS)
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
            self.messages.append({"role": "assistant", "content": text})
            if text:
                spoken.append(text)
                self.transcript.append(("agent", text))
            break
        return "\n".join(spoken)

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
            "YOUR GOAL: make this delivery succeed and prevent an RTO (return-to-origin). In order:\n"
            "1. Confirm the customer will be available to receive the delivery.\n"
            "2. Confirm the delivery address is correct and complete.\n"
            f"3. Confirm they have Rs {o['cod_amount']} cash ready — OR offer to switch to UPI prepaid "
            "(you send a payment link on WhatsApp).\n"
            "4. If they no longer want the order, capture the reason and cancel cleanly.\n\n"
            "RULES:\n"
            "- Keep every turn short — this is a phone call, not an email.\n"
            "- Be warm, respectful, efficient.\n"
            "- The moment a resolution is clear, CALL THE MATCHING TOOL, then give one short confirmation.\n"
            f"- Always pass order_id={o['order_id']} to tools.\n"
            "- If the customer is angry, confused, or it's a high-value edge case, call escalate_to_human."
        )
