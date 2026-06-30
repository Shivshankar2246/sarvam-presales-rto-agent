# Project Sampark 📞 — RTO-Reduction Voice Agent

> **A regional-language voice agent that calls your COD customers before delivery — confirms
> availability, fixes the address, or switches them to UPI prepaid — and writes the fix back
> into your systems automatically. Built on Sarvam AI.**
>
> Sarvam AI — Pre-Sales Engineer Assignment · Use case: **Reducing Return-to-Origin (RTO) for
> Indian D2C e-commerce** (not from the inspiration list — chosen to show where Sarvam's stack
> wins decisively).

**Sampark** (संपर्क, "to connect") reconnects the brand with the customer in the 30-minute window
before a delivery fails — the moment that decides whether an order is delivered or becomes an
expensive Return-to-Origin.

---

## Why this use case

Indian e-commerce runs on COD, and **COD orders return-to-origin at ~26% vs <2% for prepaid —
~13x worse** *(Shipway ShipNotes FY25, the one primary hard-sampled RTO benchmark)*. For a brand
shipping 1.2 lakh orders/month, that's **~₹5.5 crore/year** leaking out the bottom of the P&L.

The customers who RTO the most — Tier 2/3, COD, regional-language buyers — are exactly the ones
the current Hindi/English tele-calling team **can't reach**. **Voice in their own language is the
only channel that converts them**, and that is precisely where Sarvam's 22-language, code-mixing,
low-latency stack wins and a generic US voice stack structurally can't follow.

Full business case with the ROI model: **[`docs/business-writeup.md`](docs/business-writeup.md)**.

---

## 🚀 Quickstart (runs in 30 seconds, no API key)

The repo ships an offline **mock** so a reviewer can see the whole flow before adding any key.

```bash
git clone <this-repo> && cd sarvam-presales-rto-agent
pip install -r requirements.txt          # or just: pip install requests python-dotenv
python src/run_demo.py --scenario cod_prepaid --mode auto
```

You'll see a full **Hindi COD → prepaid** call: greeting → customer says they have no cash → agent
offers a UPI link → `convert_to_prepaid` tool fires → structured disposition returned for n8n.

Try the other two scenarios:

```bash
python src/run_demo.py --scenario reschedule --mode auto   # Tamil — not available → reschedule
python src/run_demo.py --scenario address    --mode auto   # Hinglish — wrong address → fix
```

| Scenario | Language | RTO cause resolved | Tool fired | Disposition |
|---|---|---|---|---|
| `cod_prepaid` | Hindi | No cash for COD | `convert_to_prepaid` | `CONVERTED_PREPAID` |
| `reschedule` | Tamil | Not available | `reschedule_delivery` | `RESCHEDULED` |
| `address` | Hinglish (code-mix) | Wrong/incomplete address | `update_address` | `ADDRESS_FIXED` |

---

## 🔊 Running with real Sarvam APIs (the live demo)

1. Get a key (₹100 free credits) at **[dashboard.sarvam.ai](https://dashboard.sarvam.ai)**.
2. `cp .env.example .env` and set `SARVAM_API_KEY=...`
3. Live voice (real STT → sarvam-30b → TTS, in-language, needs a mic):
   ```bash
   pip install sounddevice soundfile numpy        # macOS: brew install portaudio
   python src/run_demo.py --scenario cod_prepaid --mode voice
   ```
4. Or hear the agent's real Sarvam TTS voice on the scripted flow (great for the demo video):
   ```bash
   python src/run_demo.py --scenario reschedule --mode auto --speak
   ```

The moment a real `SARVAM_API_KEY` is present, the code swaps from the mock to the real Sarvam
client automatically — same code path, no flags.

---

## 🧩 The agentic backend (n8n) — full A+B

The voice bot is only half. Every call ends in a structured disposition that an **n8n** workflow
fans out to the brand's systems — OMS, 3PL courier, WhatsApp, CRM, and a human queue for edge
cases. This is what makes it an enterprise system, not a chatbot.

```bash
# 1. Run the voice service that n8n calls:
cd src && uvicorn server:app --port 8000
curl localhost:8000/health

# 2. Trigger the full pipeline (simulates an OMS "out for delivery" webhook):
curl -X POST localhost:8000/trigger-call -H 'content-type: application/json' \
     -d @samples/trigger_cod_prepaid.json
```

Build the n8n workflow by following **[`n8n/BUILD-GUIDE.md`](n8n/BUILD-GUIDE.md)** (step-by-step,
node-by-node), or import **[`n8n/sampark-workflow.json`](n8n/sampark-workflow.json)** as a
reference. The end-to-end triggered sequence:

> **event** (out for delivery) → **agent reasons** (in-language voice) → **tool called**
> (reschedule / fix address / convert to prepaid) → **downstream updated** (OMS · 3PL · WhatsApp ·
> CRM) — exactly the flow the assignment asks for.

---

## 📊 Post-call analytics (optional deliverable)

Every call can be run through a **batch analytics pipeline** — Saaras batch STT + diarization →
`sarvam-30b` disposition/objection tagging → an English summary (so one ops team reads calls
across 10 languages) → appended to `outputs/call_analytics.csv` for the dashboard.

```bash
python src/analytics/post_call_analytics.py --scenario cod_prepaid   # offline-friendly
python src/analytics/post_call_analytics.py --audio samples/call.wav --language hi-IN  # real STT
```

This surfaces aggregate objection patterns (why orders RTO) and feeds the agent's learning loop.

## Which Sarvam APIs are used, and why

| Sarvam API | Model | Where it's used | Why it's core (not an afterthought) |
|---|---|---|---|
| **Speech-to-Text** | `saaras:v3` (`mode=codemix`) | Transcribe the customer | Tier 2/3 COD buyers speak regional + Hinglish; generic STT fails on code-mix |
| **Chat / LLM** | `sarvam-30b` (tool-calling) | Reason over the 4 RTO causes, decide + call tools | Indian-commerce-native (COD, UPI, address norms); low latency for live calls |
| **Text-to-Speech** | `bulbul:v3` | Speak in the customer's language | 39 Indian voices; an English IVR gets hung up on |
| **Translate** | `mayura:v1` | Normalize transcripts → English for the ops dashboard | One ops team reads dispositions across 10 languages |

`sarvam-m` is **deprecated** and deliberately not used. Chat goes through Sarvam's
OpenAI-compatible `/v1` endpoint for robust tool-calling.

**Engineering notes (tested against live Sarvam APIs):**
- **Reliable tool-calling** at `temperature=0` via three guards: a fixed in-language greeting, a
  *structured-output fallback* (if the model ever emits a tool name as text, it's caught and
  re-issued as a proper structured call), and an *end-of-call `finalize()`* that forces a
  disposition with `tool_choice="required"` so every call is classified. Verified 9/9 across the
  three scenarios.
- **`bulbul:v3` speakers** (priya/ritu/neha…) — note v2 voices like `anushka` are not valid on v3.
- **STT** uses `mode=codemix` so Hinglish/Tanglish transcribes faithfully.

---

## 📁 Repository structure

```
sarvam-presales-rto-agent/
├── README.md                      ← you are here
├── requirements.txt · .env.example
├── src/
│   ├── config.py                  ← model ids, env, mock/real toggle
│   ├── sarvam_client.py           ← real Sarvam client (STT/TTS/LLM/Translate)
│   ├── mocks/mock_sarvam.py       ← offline mock (runs with no key)
│   ├── agent/
│   │   ├── rto_agent.py           ← the agent: sarvam-30b + tool-calling loop
│   │   ├── tools.py               ← 6 tools + n8n fan-out executor
│   │   └── scenarios.py           ← sample orders + scripted demo lines
│   ├── voice/                     ← live mic/speaker loop (voice mode)
│   ├── analytics/                 ← optional: post-call analytics pipeline
│   ├── run_demo.py                ← CLI demo (auto / text / voice)
│   └── server.py                  ← FastAPI service n8n triggers
├── n8n/
│   ├── BUILD-GUIDE.md             ← step-by-step workflow build
│   └── sampark-workflow.json      ← importable reference workflow
├── docs/
│   ├── business-writeup.md        ← the pre-sales artifact (problem → ROI → rollout)
│   ├── architecture.md            ← system diagram + data flow
│   ├── solution-design.md         ← scenario, conversation flows, agent contract
│   └── demo-script.md             ← the 3–5 min video script
└── samples/                       ← example trigger payloads
```

---

## 🎥 Demo video

**[▶ 3-min walkthrough — LINK TO BE ADDED]** · script: [`docs/demo-script.md`](docs/demo-script.md)

Shows multilingual conversations (Hindi · Tamil · Hinglish), the live tool-calling, and the n8n
fan-out firing.

---

## Limitations (honest)

This is a **proof-of-concept on mock order data** — the flow is real and end-to-end, but it's not
yet wired to live telephony at scale or production OMS/3PL APIs. The 90-day rollout plan and the
production gap list are in [`docs/business-writeup.md`](docs/business-writeup.md) §6.
