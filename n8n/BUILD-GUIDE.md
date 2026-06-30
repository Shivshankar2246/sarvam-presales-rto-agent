# n8n Agentic Backend — Step-by-Step Build Guide

This is the **"B" (agentic workflow)** half of Project Sampark. It receives the delivery
event, calls the voice agent, and **fans the result out** to the brand's systems
(OMS · 3PL · WhatsApp · CRM · human queue).

> You'll build this by hand in the n8n editor. Every node, every field, every expression is
> spelled out below. An importable reference copy lives at
> `n8n/sampark-workflow.json` — use it only to cross-check your manual build.

**What you're building (the flow):**

```
Webhook (order event)
   → Enrich Order Context (Set)
   → Call Voice Agent (HTTP → FastAPI /trigger-call)        ← runs the Sarvam voice call, returns disposition
   → Route on Disposition (Switch)
        ├─ CONVERTED_PREPAID → OMS: mark prepaid   → WhatsApp: payment confirmation
        ├─ RESCHEDULED       → 3PL: reschedule     → WhatsApp: new slot
        ├─ ADDRESS_FIXED     → OMS: update address → 3PL: re-route
        ├─ CANCELLED         → OMS: cancel + 3PL hold
        └─ (fallback) ESCALATED/UNREACHABLE → Slack: human queue
   → Log to CRM (HTTP)  ← every branch lands here
   → Respond to Webhook
```

Downstream targets (OMS/3PL/WhatsApp/Slack/CRM) are **HTTP Request nodes pointed at mock URLs**
for the PoC — swap them for the real integrations in production. Mock data is fine; the *flow*
is the deliverable.

---

## Prerequisites (2 min)

1. **n8n running.** Either:
   - Desktop/Docker: `docker run -it --rm -p 5678:5678 n8nio/n8n` → open `http://localhost:5678`, or
   - `npx n8n` (needs Node 18+).
2. **The voice service running** so n8n has something to call:
   ```bash
   cd src && uvicorn server:app --port 8000
   # health check: curl http://localhost:8000/health
   ```
   > If n8n is in Docker and the voice service is on your host, use
   > `http://host.docker.internal:8000` instead of `http://localhost:8000` in the HTTP node.
3. A free **webhook.site** tab open (we'll paste its URL into the mock downstream nodes so you
   can *see* the fan-out fire). Optional but great for the demo video.

---

## Node 1 — Webhook (the trigger)

1. New workflow → name it **`Sampark — Trigger & Resolve`**.
2. Add node → search **Webhook** → add it.
3. Set:
   - **HTTP Method:** `POST`
   - **Path:** `sampark-trigger`
   - **Respond:** `Using 'Respond to Webhook' node`
4. Copy the **Test URL** it shows (e.g. `http://localhost:5678/webhook-test/sampark-trigger`).

This is the endpoint your OMS/3PL would call when an order goes *Out for Delivery* or a delivery
attempt fails (NDR). For the demo you'll fire it with curl (see "Run it" at the bottom).

---

## Node 2 — Set: "Enrich Order Context"

In production this is where you'd hit your order DB / OMS to fetch the customer's language,
phone, address, and COD amount. For the PoC we just pass the incoming order through and attach
the scripted `customer_lines`.

1. Add node → **Edit Fields (Set)** → rename to **`Enrich Order Context`**.
2. Mode: **Manual Mapping**, **Keep Only Set: OFF** (so the order passes through).
3. Add field → Name `enriched` → Type Boolean → Value `true` (just a marker).
4. Connect: **Webhook → Enrich Order Context**.

> Real version: replace this with a **Postgres**/**HTTP** node that does
> `SELECT language_pref, phone, address, cod_amount FROM orders WHERE id = {{$json.body.order.order_id}}`.

---

## Node 3 — HTTP Request: "Call Voice Agent"

This is the bridge into the voice bot. It POSTs the order to the FastAPI service, which runs the
in-language Sarvam conversation and returns the **disposition** + **tools_called**.

1. Add node → **HTTP Request** → rename **`Call Voice Agent`**.
2. Set:
   - **Method:** `POST`
   - **URL:** `http://localhost:8000/trigger-call`  *(or `http://host.docker.internal:8000/...` if n8n is in Docker)*
   - **Send Body:** ON → **Body Content Type:** `JSON`
   - **Specify Body:** `Using JSON` → paste this expression:
     ```
     ={{ { "order": $json.body.order, "customer_lines": $json.body.customer_lines } }}
     ```
3. Connect: **Enrich Order Context → Call Voice Agent**.

The response body now contains:
```json
{ "order_id": "...", "disposition": "CONVERTED_PREPAID", "tools_called": [...], "transcript": [...] }
```

---

## Node 4 — Switch: "Route on Disposition"

1. Add node → **Switch** → rename **`Route on Disposition`**.
2. **Mode:** Rules. **Value to match (Value 1):**  `={{ $json.disposition }}`
3. Add these routing rules (String → equals):
   | Output | Value 2 |
   |---|---|
   | 0 | `CONVERTED_PREPAID` |
   | 1 | `RESCHEDULED` |
   | 2 | `ADDRESS_FIXED` |
   | 3 | `CANCELLED` |
4. **Fallback Output:** ON (this catches `ESCALATED`, `UNREACHABLE`, `CALLBACK_SCHEDULED`).
5. Connect: **Call Voice Agent → Route on Disposition**.

---

## Node 5–9 — Downstream actions (HTTP Request nodes)

For each branch, add an **HTTP Request** node. For the PoC, set every URL to your
**webhook.site** URL (so you can watch them fire); in production these become real OMS/3PL/
WhatsApp APIs. For all of them: Method `POST`, Send Body `JSON`.

| Node name | Wire from Switch output | JSON body expression |
|---|---|---|
| **OMS: mark prepaid** | 0 (CONVERTED_PREPAID) | `={{ { "action":"mark_prepaid", "order_id":$json.order_id } }}` |
| **WhatsApp: payment confirmation** | after "OMS: mark prepaid" | `={{ { "to":$json.order_id, "template":"prepaid_confirmed" } }}` |
| **3PL: reschedule** | 1 (RESCHEDULED) | `={{ { "action":"reschedule", "order_id":$json.order_id, "slot":$json.tools_called[0].args.preferred_slot } }}` |
| **OMS: update address** | 2 (ADDRESS_FIXED) | `={{ { "action":"update_address", "order_id":$json.order_id, "address":$json.tools_called[0].args.corrected_address, "landmark":$json.tools_called[0].args.landmark } }}` |
| **OMS: cancel + 3PL hold** | 3 (CANCELLED) | `={{ { "action":"cancel_and_hold", "order_id":$json.order_id, "reason":$json.tools_called[0].args.reason } }}` |
| **Slack: human queue** | fallback (ESCALATED/UNREACHABLE) | `={{ { "channel":"#ndr-escalations", "text":"Manual follow-up needed for " + $json.order_id } }}` |

> Tip: you only *need* one branch wired to make the demo land (the COD→prepaid path is the money
> shot). Build that branch fully first, then clone the HTTP node for the others.

---

## Node 10 — HTTP Request: "Log to CRM" (every branch lands here)

1. Add node → **HTTP Request** → rename **`Log to CRM`**.
2. Method `POST`, URL = your webhook.site URL, Body JSON:
   ```
   ={{ { "order_id":$json.order_id, "disposition":$json.disposition, "language":$json.language, "logged_at":$now } }}
   ```
3. Connect **every** downstream node's output into **Log to CRM** (n8n allows many→one).

> Real version: swap for a **Google Sheets → Append Row** node (the ops dashboard) or your CRM
> node. It's an HTTP node here so the workflow imports with zero credential setup.

---

## Node 11 — Respond to Webhook

1. Add node → **Respond to Webhook** → rename **`Done`**.
2. **Respond With:** `JSON` → Body: `={{ { "ok": true, "disposition": $json.disposition } }}`
3. Connect **Log to CRM → Done**.

---

## Run it (the demo)

1. Make sure the voice service is up: `cd src && uvicorn server:app --port 8000`.
2. In n8n, click **Execute Workflow** (listens for one test call).
3. Fire the trigger with the sample payload:
   ```bash
   curl -X POST http://localhost:5678/webhook-test/sampark-trigger \
     -H 'content-type: application/json' \
     -d '{
       "order": {
         "order_id": "RVT-48217", "customer_name": "Rakesh Kumar",
         "language_code": "hi-IN", "language_name": "Hindi",
         "item": "Men'\''s Kurta Set", "cod_amount": 1450,
         "address": "Indira Nagar, Lucknow", "status": "OUT_FOR_DELIVERY"
       },
       "customer_lines": [
         "हाँ रहूँगा घर पे, लेकिन अभी मेरे पास कैश नहीं है।",
         "हाँ भेज दो UPI लिंक, मैं अभी पे कर देता हूँ।"
       ]
     }'
   ```
4. Watch n8n light up: Webhook → Enrich → Call Voice Agent (disposition `CONVERTED_PREPAID`) →
   Switch routes to output 0 → OMS + WhatsApp nodes fire → Log to CRM. Check your webhook.site
   tab to see the downstream payloads land.

That's the full **event → reason → tool → downstream** loop the assignment asks for.

---

## What to say about this in the demo video (15 seconds)

> "The voice bot is only half of it. Every call ends in a structured disposition that n8n fans
> out automatically — here a COD order just converted to prepaid, so n8n flips the OMS to
> prepaid and fires the WhatsApp payment link, with no human in the loop. That's the difference
> between a chatbot and an enterprise system."
