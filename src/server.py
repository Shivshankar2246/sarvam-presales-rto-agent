"""FastAPI voice service — the endpoint the n8n agentic backend triggers.

Production flow:  n8n (OUT_FOR_DELIVERY webhook) -> POST /trigger-call -> this service
places the outbound call, runs the in-language conversation, and returns the structured
disposition, which n8n then fans out (OMS / 3PL / WhatsApp / CRM).

For the PoC, /trigger-call accepts optional `customer_lines` so the whole contract can
be exercised over HTTP without live telephony. Run:
    uvicorn server:app --reload --port 8000   (from the src/ directory)
    curl -X POST localhost:8000/trigger-call -H 'content-type: application/json' \
         -d @../samples/trigger_cod_prepaid.json
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any, Optional  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from agent.rto_agent import RTOAgent  # noqa: E402
from config import CHAT_MODEL, settings  # noqa: E402
from sarvam_client import get_client  # noqa: E402

app = FastAPI(title="Project Sampark — Voice Service", version="1.0.0")


class Order(BaseModel):
    order_id: str
    customer_name: str
    language_code: str = "hi-IN"
    language_name: str = "Hindi"
    item: str = ""
    cod_amount: int = 0
    address: str = ""
    status: str = "OUT_FOR_DELIVERY"


class TriggerCall(BaseModel):
    order: Order
    # For the PoC: scripted customer turns to simulate the call without telephony.
    customer_lines: Optional[list[str]] = None


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "backend": "mock" if settings.use_mock else "sarvam",
        "chat_model": CHAT_MODEL,
        "n8n_configured": bool(settings.n8n_webhook_url),
    }


@app.post("/trigger-call")
def trigger_call(req: TriggerCall) -> dict[str, Any]:
    """Run the conversation and return the disposition n8n will fan out on."""
    client = get_client()
    agent = RTOAgent(client, req.order.model_dump())

    agent.greeting()
    for line in (req.customer_lines or []):
        if agent.is_done:
            break
        agent.respond(line)

    if not agent.is_done:
        agent.finalize()

    outcome = agent.outcome()
    # n8n reads `disposition` + `tools_called` to drive the downstream branch.
    return outcome
