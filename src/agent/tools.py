"""Agent tools — the actions Sampark can take on a call.

Two halves:
1. TOOLS — OpenAI-style function schemas handed to sarvam-30b so it can decide
   *when* to act (reschedule / fix address / convert to prepaid / cancel / etc.).
2. ToolExecutor — runs the chosen action. In production each call POSTs to the n8n
   agentic backend, which fans out to OMS / 3PL / WhatsApp / CRM. Without an n8n
   webhook configured it logs and returns a mock success, so the flow still runs.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import requests

from config import settings

log = logging.getLogger("sampark.tools")

# tool name -> the disposition it resolves the call to
DISPOSITION = {
    "reschedule_delivery": "RESCHEDULED",
    "update_address": "ADDRESS_FIXED",
    "convert_to_prepaid": "CONVERTED_PREPAID",
    "cancel_order": "CANCELLED",
    "schedule_callback": "CALLBACK_SCHEDULED",
    "escalate_to_human": "ESCALATED",
}

# Terminal tools end the call; non-terminal ones (callback) keep the queue alive.
TERMINAL_TOOLS = {
    "reschedule_delivery", "update_address", "convert_to_prepaid",
    "cancel_order", "escalate_to_human",
}

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "reschedule_delivery",
            "description": "Reschedule the delivery to a slot the customer confirmed they'll be available for.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "preferred_slot": {
                        "type": "string",
                        "description": "Natural-language slot the customer agreed to, e.g. 'tomorrow 12-3pm'.",
                    },
                },
                "required": ["order_id", "preferred_slot"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_address",
            "description": "Correct an incomplete or wrong delivery address captured on the call.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "corrected_address": {"type": "string"},
                    "landmark": {"type": "string"},
                },
                "required": ["order_id", "corrected_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_to_prepaid",
            "description": "Lock the order as prepaid by sending a UPI payment link on WhatsApp, sweetened with a small incentive (free shipping) so the customer pays now and the order ships today. A COD order's ~30-40% return rate collapses to ~5% once it is prepaid — the single biggest RTO reducer.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Cancel the order when the customer no longer wants it — avoids dispatching a guaranteed return.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["order_id", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": "Re-queue this customer for a later call (e.g. they're busy right now).",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "callback_time": {"type": "string"},
                },
                "required": ["order_id", "callback_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Hand off to a human agent for angry, confused, fraud-suspect, or high-value edge cases.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["order_id", "reason"],
            },
        },
    },
]


class ToolExecutor:
    """Executes a tool call and fans it out to the n8n agentic backend."""

    def __init__(self, order: dict[str, Any] | None = None):
        self.order = order or {}
        self.webhook = settings.n8n_webhook_url

    def execute(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        disposition = DISPOSITION.get(name, "UNKNOWN")
        payload = {
            "tool": name,
            "args": args,
            "order_id": args.get("order_id") or self.order.get("order_id"),
            "disposition": disposition,
        }

        downstream = self._fan_out(payload)
        log.info("tool=%s disposition=%s downstream=%s", name, disposition, downstream)
        return {
            "status": "ok",
            "disposition": disposition,
            "terminal": name in TERMINAL_TOOLS,
            "downstream": downstream,
            **payload,
        }

    def _fan_out(self, payload: dict[str, Any]) -> str:
        """POST to n8n if configured; otherwise simulate (keeps the PoC runnable)."""
        if not self.webhook:
            return "simulated (no N8N_WEBHOOK_URL set — set it to fan out to OMS/3PL/WhatsApp)"
        try:
            r = requests.post(self.webhook, json=payload, timeout=10)
            r.raise_for_status()
            return f"n8n accepted ({r.status_code})"
        except Exception as e:  # never let a downstream hiccup break the live call
            log.warning("n8n fan-out failed: %s", e)
            return f"n8n fan-out failed: {e}"


def tool_result_message(tool_call_id: str, result: dict[str, Any]) -> dict[str, Any]:
    """Format a tool result as an OpenAI 'tool' role message for the next turn."""
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": json.dumps(result, ensure_ascii=False),
    }
