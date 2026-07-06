# Project Sampark — Business Case

**Prepared for:** VP Operations / CTO, a high-growth D2C brand
**Prepared by:** Pre-Sales Engineering, Sarvam AI *(assignment submission by Vignesh Srinivasan)*
**Subject:** Cutting Return-to-Origin (RTO) losses with a regional-language voice agent

> A one-line version for the busy exec: *Your highest-RTO customers are the ones your current
> process can't reach — because of language, capacity, and timing. Sampark calls every one of
> them, in their own language, the moment an order is at risk — and writes the fix back into your
> systems automatically. Conservative case: it pays for itself ~2.5x in month one.*

---

## 1. The Problem

For a D2C brand in India, **Return-to-Origin (RTO) is the single largest controllable leak in
the P&L** — and it is concentrated almost entirely in Cash-on-Delivery (COD) orders.

The hard numbers:

- **COD orders come back 30–40% of the time, versus 5–7% for prepaid — up to 8× worse.**
  *(Snapmint 2024; Shiprocket puts it at COD 20–30% / prepaid 10–15%; Shipway's hard-sampled
  cross-category number is 26% COD.)* Fashion/apparel — the COD-heaviest category — sits at the
  top of that range.
- A single RTO costs **₹300–700 fully loaded** — freight both ways + packaging + the wasted
  customer-acquisition spend on an order that earns nothing — which **wipes out the profit of
  roughly 3 delivered orders.** *(Shiprocket / Base.com unit-economics synthesis, 2024. Logistics
  only, it's ~₹125–230.)*
- **~50% of all Indian online orders are still COD**, rising to **60–80% in Tier 2/3 cities.**
  COD isn't fading — for first-time and small-town buyers, **trust, not payment rails, is the
  bottleneck.**
- **Tier 2/3 cities drove ~65% of festive orders (Tier 3 alone ~46%)** *(Fynd Festive Report
  2025)* — i.e. the RTO problem is growing fastest in exactly the low-English, high-COD cohort.

**For a representative brand — "Zivaa", 1.2 lakh orders/month, 64% COD, apparel:**

| | |
|---|---|
| COD orders / month | 76,800 |
| COD RTO rate (apparel) | ~30% |
| COD RTOs / month | ~23,000 |
| Cost per RTO (logistics-only, conservative) | ₹200 |
| **Monthly RTO bleed** | **~₹46 lakh** |
| **Annualised** | **~₹5.5 crore** *(₹11 cr+ at all-in cost)* |

And here's the part that makes it solvable: **~42% of failed deliveries are "customer refused" +
"customer unavailable", and another ~14% are "incomplete/wrong address"** *(Goswift NDR
breakdown)* — i.e. **the majority of RTOs are caused by things a 90-second phone call can fix
before the courier ever knocks.**

---

## 2. Why AI (and why voice, not SMS)

**The current playbook doesn't reach the people who RTO the most.** Brands run a small in-house
or BPO tele-calling team. It hits a wall on three axes at once:

1. **Capacity.** Covering 76,800 COD orders/month means ~3,000 calls/day. At 80–150 calls per
   agent per day that's a **~30-person team** — most brands staff a fraction of that and reach
   only ~40% of at-risk orders.
2. **Language.** The teams operate in Hindi/English. But **9 of 10 new Indian internet users are
   regional-language speakers, only ~6–10% of India speaks English, and ~98% consume content in
   Indic languages** *(KPMG-Google; IAMAI-Kantar)*. The uncontacted 60% skews Tier 2/3 and
   regional-language — the highest-RTO cohort.
3. **Timing.** Teams work 10am–7pm. A confirmation that lands **within 6 hours has ~2x the
   re-attempt success** of one after 48 hours *(Shipway)*. Coverage gaps = lost saves.

**Why voice, not just SMS/WhatsApp?** SMS sees ~98% opens but only **3–5% action** — one-way text
doesn't carry a *high-friction* action like "confirm you'll be home and have ₹1,450 ready, or pay
by UPI now." A short call in the customer's language does. (WhatsApp is a strong *fallback* — and
Sampark uses it to deliver the payment link — but the conversation is what converts.)

**Who is the end user?** A COD buyer in Lucknow, Patna, or Coimbatore. Moderate digital literacy,
answers a phone call in their mother tongue, ignores an English SMS, won't fill a web form. **Voice
in their language is not a nice-to-have — it's the only channel that reliably converts them.**

AI makes it economic: **automated NDR resolution converts 40–60% of cases vs 10–20% for manual**
*(Clickpost)*, at a fraction of the per-call cost, in every language, around the clock.

---

## 3. Why Sarvam

This use case is, frankly, a near-perfect fit for Sarvam's specific strengths — and a poor fit
for generic US voice stacks.

| What the problem demands | Sarvam | Generic alternative (OpenAI / ElevenLabs / Twilio AI) |
|---|---|---|
| **Natural speech in 10+ Indian languages** | Saaras STT (22 Indic + En) · Bulbul TTS (39 Indian voices) — purpose-built | Limited, often accented/robotic Indian-language coverage; Tamil/Bhojpuri quality drops off |
| **Code-mixing** ("cash nahi hai", "blue gate ke saamne") | Native code-mix mode in Saaras | Mis-transcribes code-switched speech — the most common real-world failure |
| **Low latency on a live call** | India-hosted, low-latency stack | Trans-Pacific round-trips add lag; >1s and the customer hangs up |
| **Data sovereignty (DPDP)** | India-resident data, on-prem options | Names, addresses, phone, COD amounts leaving India raises DPDP/residency flags |
| **Indian-commerce reasoning** | sarvam-30b understands COD, UPI, address norms natively | Needs heavy prompt-engineering to handle Indian commerce context |

The decisive point for a pre-sales conversation: **the moat is load-bearing here.** Sampark's value
*comes from* the regional-language, code-mixing, low-latency call. Strip that out and the product
doesn't work. That is exactly the kind of India-specific problem Sarvam is built to win — and where
a generic stack structurally cannot follow.

**Competitive note:** the category leader by network (GoKwik, 15,000+ brands) confirms COD via
**OTP/WhatsApp, not conversational voice**; Shipway uses **IVR robocalls**, not natural-language
AI. The clearest whitespace is a genuine **regional-language conversational voice agent** — which
is precisely what Sarvam's stack uniquely enables.

---

## 4. Architecture Summary (for a business audience)

Sampark is a **voice bot with an agentic backend** — two halves that make it an enterprise system,
not a chatbot.

```
  Order goes "Out for Delivery"
            │
            ▼
   ┌──────────────────┐     calls the customer, in their language
   │   VOICE AGENT     │  ── Sarvam: listens (STT) → reasons (LLM) → speaks (TTS) ──┐
   │   "Meera"         │                                                            │
   └──────────────────┘                                                            │
            │  decides the fix on the call:                                        │
            │  reschedule · fix address · switch to UPI prepaid · cancel           │
            ▼                                                                       ▼
   ┌──────────────────┐     writes the fix back, automatically            (customer's phone)
   │  AGENTIC BACKEND │  ── n8n → updates OMS · instructs courier (3PL) ──
   │  (n8n)           │       · sends WhatsApp confirmation · logs to CRM
   └──────────────────┘       · escalates edge cases to a human
```

In plain terms: **the call doesn't end in a note for someone to action later — it ends in the
system already being updated.** A COD order that converts to prepaid on the call is flipped to
prepaid in the OMS and the UPI link is on the customer's WhatsApp before they've hung up. *(Full
technical diagram: `docs/architecture.md`.)*

The voice agent runs as a **genuine real-time, streaming call** — the customer speaks, Meera
listens, understands their code-mixed speech, and replies in the same breath, with natural
interruption (barge-in). It's the same experience as a human tele-caller, at software cost and
scale. *(Live demo: the Call Console in `realtime/`.)*

---

## 5. ROI / Business Case

**Assumptions (all stated, conservative):** 76,800 COD orders/month · ₹200 cost per RTO
(logistics-only; all-in is ₹400+) · current COD RTO 30% (~23,000 RTOs/month) · Sampark calls
**100%** of COD orders · **25% relative RTO reduction** (deliberately below the 20–40% industry
band and well below Unicommerce's documented 39%→21% ≈ 46%) · all-in cost ~₹6/call (Sarvam
STT+TTS+LLM ≈ ₹3–4, telephony + infra ≈ ₹2).

| | Conservative case | Upside case |
|---|---|---|
| RTO reduction (relative) | 25% | 35% |
| Cost per RTO | ₹200 (logistics-only) | ₹400 (all-in) |
| RTOs prevented / month | ~5,760 | ~8,060 |
| **Gross monthly saving** | **~₹11.5 lakh** | **~₹32.3 lakh** |
| Sampark cost / month (76,800 calls × ₹6) | ~₹4.6 lakh | ~₹4.6 lakh |
| **Net monthly benefit** | **~₹6.9 lakh** | **~₹27.7 lakh** |
| **ROI on spend** | **~2.5x** | **~7x** |
| **Annualised net benefit** | **~₹83 lakh** | **~₹3.3 crore** |

**Two more sources of value not even counted above:**

- **Prepaid conversion.** Every COD order Sampark switches to UPI prepaid drops that order's RTO
  risk from ~30% to <2%. GoKwik's Pepe Jeans case saw a **20% prepaid uplift**; even a modest
  conversion rate compounds the savings well beyond the table.
- **Labour avoided.** Achieving 100% COD coverage manually would need a **~30-seat, 10-language,
  24/7 team — ₹15–38 lakh/month** fully loaded. Sampark delivers that coverage as software.

**Payback: month one.** The conservative case is net-positive from the first month; there is no
multi-quarter ramp to value.

> Sourcing honesty (the pre-sales credibility move): the RTO-reduction % and cost-per-RTO inputs
> are industry/vendor estimates, not audited studies — so the model leads with the *primary*
> anchors (Shipway's 26% COD RTO; Unicommerce's 39%→21%) and deliberately discounts below them. We
> recommend validating the exact RTO baseline and cost-per-RTO against your own shipping data in a
> 2-week paid pilot before committing to an annual number.

---

## 6. Limitations & Next Steps

**What the PoC is — and isn't.** The proof-of-concept runs the full loop end-to-end on **mock
order data**: an event triggers the call, the agent converses in-language using real Sarvam
STT/LLM/TTS, calls a tool, and n8n fans the result out. The conversation runs as a **real-time,
streaming, barge-in call** (Pipecat + Sarvam over WebRTC — see `realtime/`). What's **not** yet
wired: **PSTN telephony at scale** (a real phone number via Plivo/Exotel, concurrency) and
production OMS/3PL APIs — by design, to keep the demo runnable and reviewable.

**For a production rollout, the gaps to close:**

- **Telephony at scale** — Plivo/Exotel integration, concurrency, retry & voicemail logic, DTMF
  fallback.
- **System integrations** — real OMS (Unicommerce/Increff) and 3PL (Delhivery/Shadowfax) APIs in
  place of the mock endpoints.
- **Compliance** — DPDP-compliant consent capture, DND/TRAI handling, call recording governance,
  PII handling and retention.
- **Quality & control** — warm human handoff for edge cases, guardrails against over-promising,
  and an A/B holdout against the existing team to measure true incremental RTO reduction.
- **Learning loop** — the post-call analytics pipeline (batch STT + diarization + LLM disposition
  tagging) feeding objection patterns back into the agent.

**Suggested 90-day enterprise rollout:**

| Phase | Weeks | Outcome |
|---|---|---|
| **1 — Pilot** | 1–3 | Live on one 3PL + one language (Hindi), 5–10% of COD volume, measured against a holdout. Validate the RTO-reduction % on *your* data. |
| **2 — Expand** | 4–8 | Add Tamil/Telugu/Bengali + WhatsApp prepaid link + OMS write-back. Scale to 50% of COD volume. Tune the prepaid-conversion flow (the highest-ROI lever). |
| **3 — Production** | 9–12 | 100% COD coverage, 8–10 languages, 24/7, full DPDP compliance, human-handoff queue, and the analytics loop live. Lock the annual ROI number from measured pilot data. |

**The recommended next step:** a **2-week paid pilot** on a single language and 3PL, with a holdout
group, to establish your real RTO baseline and the measured reduction — turning every estimate in
section 5 into a number from your own shipping data.
