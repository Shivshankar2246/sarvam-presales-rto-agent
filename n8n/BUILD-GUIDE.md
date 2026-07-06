# n8n Agentic Backend — Step-by-Step Build Guide

This is the **"B" (agentic workflow)** half of Project Sampark. It **fans a call outcome out**
to the brand's systems (OMS · 3PL · CRM · human queue).

Sampark ships **two entry points into the same fan-out** — pick whichever the demo needs:

| Workflow | Trigger | Voice call | Use |
|---|---|---|---|
| **Sampark — Trigger & Resolve** (`sampark-workflow.json`) | OMS/3PL fires an order event → n8n | n8n **places** the call (HTTP → `/trigger-call`) | Batch / outbound automation |
| **Sampark — Live Resolve** (`sampark-live-resolve.json`) | The **live Call Console** POSTs the captured outcome | call already happened live | The A+B live demo — conversation drives the backend |

> You'll build the first one by hand in the n8n editor (every node/field/expression is spelled out
> below). The second is **import-only** — see *"Live Resolve"* at the end. Reference copies live at
> `n8n/sampark-workflow.json` and `n8n/sampark-live-resolve.json`.

**What you're building (the flow):**

```
Webhook (order event)
   → Enrich Order Context (Set)
   → Call Voice Agent (HTTP → FastAPI /trigger-call)        ← runs the Sarvam voice call, returns disposition
   → Route on Disposition (Switch)
        ├─ CONVERTED_PREPAID → OMS: mark prepaid
        ├─ RESCHEDULED       → 3PL: reschedule
        ├─ ADDRESS_FIXED     → OMS: update address
        ├─ CANCELLED         → OMS: cancel + 3PL hold
        └─ (fallback) ESCALATED/UNREACHABLE → Slack: human queue
   → Log to CRM (HTTP)  ← every branch lands here
   → Respond to Webhook
```

Downstream targets (OMS/3PL/Slack/CRM) are **HTTP Request nodes pointed at mock URLs**
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
   >
   > **If your n8n is REMOTE (n8n Cloud, or self-hosted on a VPS like Hostinger),** it can't reach
   > your laptop's `localhost`. Expose the voice service with a tunnel that has **no interstitial
   > warning page** (Serveo's free warning breaks API calls — avoid it). Cloudflare's quick tunnel
   > works with no signup:
   > ```bash
   > brew install cloudflared
   > cloudflared tunnel --url http://localhost:8000
   > ```
   > Use the printed `https://<random>.trycloudflare.com/trigger-call` as the "Call Voice Agent"
   > URL. The URL changes each restart, so keep the tunnel running during your demo.
3. A free **webhook.site** tab open (we'll paste its URL into the mock downstream nodes so you
   can *see* the fan-out fire). Optional but great for the demo video. **Copy the URL with
   webhook.site's copy icon** — copying it from a chat/doc can paste a `[markdown](link)` that n8n
   rejects as an invalid URL.

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
   - **URL:** `http://localhost:8000/trigger-call`  *(or your Cloudflare tunnel URL if n8n is remote — see prerequisites; `http://host.docker.internal:8000/...` if n8n is in Docker)*
   - **Send Body:** ON → **Body Content Type:** `JSON`
   - **Specify Body:** `Using JSON` → paste this expression (reading the webhook body by node
     reference so it resolves regardless of what the Set node passes through):
     ```
     ={{ { "order": $('Webhook').item.json.body.order, "customer_lines": $('Webhook').item.json.body.customer_lines } }}
     ```
3. Connect: **Enrich Order Context → Call Voice Agent**.
4. **Demo hardening (recommended):** open this node's **Settings** tab → set **On Error** to
   *Continue (using error output)* (older n8n: tick **Continue On Fail**). A local network blip on
   the voice service then won't crash the whole execution mid-demo.

The response body now contains:
```json
{ "order_id": "...", "disposition": "CONVERTED_PREPAID", "tools_called": [...], "transcript": [...] }
```

> **Production note:** this PoC is *synchronous* — the OMS waits for the call to finish and gets the
> disposition back in the HTTP response. That's perfect for a demo that returns an end-to-end
> payload. In production you'd usually **respond `200 OK` at the Webhook immediately** and process
> the call asynchronously, so a carrier-side timeout can't hang the OMS. (Mention this in the demo —
> it signals you understand the production tradeoff.)

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
5. **Convert types where required:** turn this toggle **ON**. On newer n8n (v3 Switch / self-hosted
   2.4+), strict type validation can make a correct-looking string rule silently fail and send
   everything to Fallback. Turning this on fixes it. (If a rule still won't match, switch its
   operator from `is equal to` → `contains`, which is more forgiving.)
6. Connect: **Call Voice Agent → Route on Disposition**.

---

## Node 5–9 — Downstream actions (HTTP Request nodes)

For each branch, add an **HTTP Request** node. For the PoC, set every URL to your
**webhook.site** URL (so you can watch them fire); in production these become real OMS/3PL/
WhatsApp APIs. For all of them: Method `POST`, Send Body `JSON`.

> ⚠️ **CRITICAL — read the voice-service response with a NODE REFERENCE, not `$json`.**
> In n8n, `$json` is only the output of the *immediately preceding* node. So in "Log to CRM"
> (which runs after an action node like "OMS: mark prepaid"), `$json` is that action mock's reply —
> `$json.order_id` would be `undefined`. To always read the **Call Voice Agent** response no matter
> where a node sits, reference that node explicitly:
> ```
> {{ $('Call Voice Agent').item.json.order_id }}
> ```
> Use this `$('Call Voice Agent').item.json.*` form in EVERY downstream node below (and in
> Node 10 and Node 11). Don't use the deprecated `$node["..."].json` syntax.

> ⚠️ **BODY FORMAT — use literal JSON with `{{ }}` placeholders, NOT a `={{ {...} }}` object
> expression.** On self-hosted n8n (HTTP node v4.3), an object-expression body throws
> *"JSON parameter needs to be valid JSON"*. The reliable form: **Body Content Type = JSON**,
> **Specify Body = Using JSON**, and write real JSON with `{{ }}` inside the quoted values (no
> leading `=`). Examples below use this form.

**OMS: mark prepaid** (Switch output 0)
```json
{ "action": "mark_prepaid", "order_id": "{{ $('Call Voice Agent').item.json.order_id }}" }
```
> *Optional (not in the shipped workflow):* chain a **WhatsApp: payment confirmation** node after
> **OMS: mark prepaid** to send the paid-order receipt —
> `{ "to": "{{ $('Call Voice Agent').item.json.order_id }}", "template": "prepaid_confirmed" }`
**3PL: reschedule** (Switch output 1)
```json
{ "action": "reschedule", "order_id": "{{ $('Call Voice Agent').item.json.order_id }}", "slot": "{{ $('Call Voice Agent').item.json.tools_called[0].args.preferred_slot }}" }
```
**OMS: update address** (Switch output 2)
```json
{ "action": "update_address", "order_id": "{{ $('Call Voice Agent').item.json.order_id }}", "address": "{{ $('Call Voice Agent').item.json.tools_called[0].args.corrected_address }}", "landmark": "{{ $('Call Voice Agent').item.json.tools_called[0].args.landmark }}" }
```
**OMS: cancel + 3PL hold** (Switch output 3)
```json
{ "action": "cancel_and_hold", "order_id": "{{ $('Call Voice Agent').item.json.order_id }}", "reason": "{{ $('Call Voice Agent').item.json.tools_called[0].args.reason }}" }
```
**Slack: human queue** (Fallback output)
```json
{ "channel": "#ndr-escalations", "text": "Manual follow-up needed for order {{ $('Call Voice Agent').item.json.order_id }}, disposition {{ $('Call Voice Agent').item.json.disposition }}" }
```

> Tip: you only *need* the prepaid branch wired to make the demo land (COD→prepaid is the money
> shot). Build that fully first, then do the others.

---

## Node 10 — HTTP Request: "Log to CRM" (every branch lands here)

1. Add node → **HTTP Request** → rename **`Log to CRM`**.
2. Method `POST`, URL = your webhook.site URL, Body Content Type **JSON**, literal-JSON form
   (node-reference again — `$json` here would be the upstream mock's reply):
   ```json
   { "order_id": "{{ $('Call Voice Agent').item.json.order_id }}", "disposition": "{{ $('Call Voice Agent').item.json.disposition }}", "language": "{{ $('Call Voice Agent').item.json.language }}" }
   ```
3. Connect **every** downstream node's output into **Log to CRM**. Many→one is fine here: the
   branches are mutually exclusive, so only the one active path executes — no Merge node needed.

> Real version: swap for a **Google Sheets → Append Row** node (the ops dashboard) or your CRM
> node. It's an HTTP node here so the workflow imports with zero credential setup.

---

## Node 11 — Respond to Webhook

1. Add node → **Respond to Webhook** → rename **`Done`**.
2. **Respond With:** `JSON` → Body: `={{ { "ok": true, "disposition": $('Call Voice Agent').item.json.disposition } }}`
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
   Switch routes to output 0 → OMS: mark prepaid fires → Log to CRM. Check your webhook.site
   tab to see the downstream payloads land.

That's the full **event → reason → tool → downstream** loop the assignment asks for.

---

## What to say about this in the demo video (15 seconds)

> "The voice bot is only half of it. Every call ends in a structured disposition that n8n fans
> out automatically — here a COD order just converted to prepaid, so n8n flips the OMS to prepaid
> and logs it to the CRM, with no human in the loop. That's the difference between a chatbot and
> an enterprise system."

---

## Live Resolve — the A+B wiring (import-only, ~3 min)

This is what fuses the voice bot and the backend into one system: the **live Call Console** pushes
each captured outcome straight to n8n, which fans it out. No `curl`, no second voice call — the
conversation itself drives the backend.

```
Live Call Console (browser)
   → customer speaks → agent captures the outcome
   → POST /webhook/sampark-live-resolve  { order_id, customer_name, language, disposition, captured }
   → Route on Disposition (Switch on $json.body.disposition)
        ├─ CONVERTED_PREPAID → OMS: mark prepaid
        ├─ RESCHEDULED       → 3PL: reschedule
        ├─ ADDRESS_FIXED     → OMS: update address
        ├─ CANCELLED         → OMS: cancel + 3PL hold
        └─ (fallback)        → Slack: human queue
   → Log to CRM → Respond
```

**Steps**

1. **Import** — n8n → *Workflows* → *Import from File* → `n8n/sampark-live-resolve.json`.
2. **Point the mock URLs at your webhook.site** — the imported nodes use a shared mock URL; open
   each HTTP node (OMS/3PL/Slack/CRM) and paste your own `https://webhook.site/...` if you want to
   watch payloads land. (Optional — the flow runs either way.)
3. **CORS is already set** — the Webhook node ships with **Allowed Origins (CORS) = `*`** so the
   browser Console can POST to it cross-origin. Don't remove it, or the browser will block the call
   with a CORS error.
4. **Activate** the workflow (toggle top-right). The **production** URL becomes
   `https://<your-n8n>/webhook/sampark-live-resolve`. The Console already points here
   (`realtime/console/index.html` → `N8N_LIVE_URL`); override at runtime with `?n8n=<url>` if needed.
5. **Test without the browser** (proves the backend in isolation):
   ```bash
   curl -X POST https://<your-n8n>/webhook/sampark-live-resolve \
     -H "Content-Type: application/json" \
     -d '{"order_id":"RVT-48217","customer_name":"Rakesh Kumar","language":"hi-IN","disposition":"CONVERTED_PREPAID","captured":"paise abhi nahi hai"}'
   ```
   Expect `{"ok":true,"disposition":"CONVERTED_PREPAID"}` and the OMS branch firing on webhook.site.

> **Why a separate workflow (not the same one)?** The Trigger & Resolve flow *places* the call
> itself; in the live flow the call already happened, so we hand n8n the finished disposition and it
> only fans out. Two clean entry points, one shared downstream — both are real product modes.
