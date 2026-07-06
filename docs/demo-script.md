# 🎬 Demo Video Script — Project Sampark

> A **Problem-Agitate-Solve** pitch for a business audience (COO / VP Ops / CEO). It opens on the
> business numbers, then **the whole demo is one real live call** — pick Lakshmi (Tamil), talk to
> the agent live, then show n8n + webhook.site proving the outcome updated the systems.
> **The call itself is NOT scripted** — you just talk; only the framing lines are written here.
> Pre-Sales Engineer Assignment · **Vignesh Srinivasan** · Target runtime: **~3:10**

---

## Setup before you hit record
- **Live call (the spine):** `cd realtime && python bot.py -t webrtc` (bot) + `cd realtime/console && python3 -m http.server 5500` (Console at localhost:5500)
- **n8n:** the **Sampark — Live Resolve** workflow is **Activated**; keep the **n8n canvas** and your **webhook.site** tab open for the proof beat
- `realtime/.env` → `REALTIME_LANG=ta-IN` (so the call is in Tamil); `.env` has a real `SARVAM_API_KEY`
- *Optional* — for the opening numbers: `streamlit run src/dashboard.py` (or use a title card / just narrate)
- Record with **Loom** + **System audio ON**; do a 10-sec test first
- Full presenter walkthrough: [`vky-guide.md`](vky-guide.md)

---

## The script (Problem → Agitate → Meet the customers → LIVE call → Backend proof → Benefits → Close)

> Only the **framing** is scripted. The live call has **no script** — you just talk to the agent in
> Tamil. Read the *Voiceover* lines around it; improvise the conversation.

| Section | On screen | Voiceover (framing only) |
|---|---|---|
| **PROBLEM** (0:00–0:25) | The RTO headline numbers (dashboard, or a title card) | "If you sell to India, you already know this pain. Most of your customers pay **Cash-on-Delivery** — and COD orders don't always get delivered. They come **back**. It's called **Return-to-Origin**, and it's the quiet tax on every D2C brand in the country." |
| **AGITATE** (0:25–1:00) | Contrast numbers: **30–40% vs 5–7%**, then **₹300–700/return** and **₹5 Cr+/yr** | "Here's how bad it is. A **prepaid** order comes back 5 to 7% of the time. A **COD fashion** order? **30 to 40%** — up to **eight times worse**. And each return costs **₹300 to ₹700** — freight both ways, packaging, and the ad spend wasted on a customer who never gets the order. One return wipes out the profit of **three delivered orders**. For a brand shipping a lakh orders a month, that's **over ₹5 crore a year** — and it's growing fastest in **Tier-2 and Tier-3 India**, where customers speak their own language and won't answer an English text — the exact orders your call team **can't reach**." |
| **MEET THE CUSTOMERS** (1:00–1:20) | **Call Console** — the three customer cards, each showing its **language** | "So here's the fix — **Sampark**, an AI agent that calls those at-risk customers **in their own language**. Here are three of them — and notice each speaks a different language: **Hindi, Tamil, Hinglish**. For this demo, I'll call **Lakshmi** — she speaks **Tamil**." *(click **Call Lakshmi**)* |
| **⭐ THE LIVE CALL** (1:20–2:20) | The live call screen — you talking to the agent; the **"Captured on this call"** panel filling in | ***(NOT SCRIPTED — you just talk.)*** Have a natural Tamil conversation about a delivery issue. Let the reviewer hear the **real speech both ways**, and **interrupt her once** to show barge-in. Say nothing scripted; let the live call speak for itself. When the **"Captured"** card appears, pause on it. |
| **⭐ BACKEND — THE PROOF** (2:20–2:55) | Switch to **n8n**, then to the **webhook.site** tab | "Now here's what makes it a system, not a chatbot. *(show n8n)* This is **n8n, our automation engine — the second the call ends, it takes whatever the customer decided and updates every delivery system automatically.** *(switch to webhook.site)* And here's the proof — the outcome of that call I just had is **saved right here in our systems**, with nobody on the team touching anything." |
| **BENEFITS** (2:55–3:15) | Back to the numbers | "That's the outcome: **fewer returns, more delivered orders, recovered margin** — 24/7, in **every Indian language**, with **zero extra headcount**. Confirmation calls like these cut returns by **15 to 40%** — and conservatively, this **pays for itself 2.5× in the first month**, with every conversation and all customer data **staying in India**. That's **Project Sampark**. Thank you." |

---

## Alternate opening hooks
- **A (recommended):** "If you sell to India, you already know this pain. Most of your customers pay Cash-on-Delivery — and those orders don't always get delivered…"
- **B (money-first):** "Indian D2C brands lose crores a year to one thing: deliveries that come back. Let me show you a console that stops it, one call at a time."
- **C (rhetorical):** "What if you could save a failing delivery with one phone call — in the customer's own language, with no staff involved? Watch."

## Alternate closing lines
- **A (recommended):** "…That's Project Sampark. Thank you."
- **B (forward-looking):** "…It's a proof-of-concept today, but the full production plan is in the repo. That's Project Sampark."

---

## Delivery notes
- **The live call + the n8n/webhook.site proof are the whole demo.** Everything else is framing.
- **Don't script the call.** Just talk to the agent in Tamil about a delivery issue — travelling, wrong address, whatever. The point is the reviewer sees it's *real*, live, and in a regional language. Try interrupting her once (barge-in).
- **Practise the call 2–3 times** before recording (STT does best with clear, unhurried speech). If it mis-hears on a take, just re-call — it's a few seconds.
- **The proof beat:** after the call, switch to **n8n** (one sentence — "the automation engine updates every system"), then **webhook.site** ("and here's the outcome, saved"). That's the A+B payoff — linger there.
- **Pause while the agent speaks** so the reviewer hears the Sarvam voice quality. Slow down on the AGITATE numbers.

---

## Numbers & sources (so you can defend any figure on the call)
| Claim in script | Figure | Source (year) |
|---|---|---|
| COD vs prepaid return rate | COD **30–40%** · prepaid **5–7%** (up to 8× worse) | Snapmint (2024); Shiprocket (COD 20–30% / prepaid 10–15%) |
| Cost of one return | **₹300–700** fully loaded (freight + packaging + wasted CAC) | Shiprocket / Base.com synthesis (2024) |
| One return = profit of ~3 orders | illustrative from unit economics | Base.com (2024) |
| Confirmation / NDR calls cut RTO | **15–40%** (COD→prepaid drops that order 75–85%) | Shipeasy, Snapmint, Shiprocket (2024) |
| Tier 2/3 share of growth | **65%** of festive orders (Tier 3 alone 46%) | Fynd Festive Report (2025) |
| COD share of orders | ~**50%** nationally; **60–80%** in Tier 2/3 | industry synthesis (2024–25) |
| Regional-language preference | ~**73%** prefer Indian languages (536M vs 199M English) | KPMG "Indian Languages" |
| Human tele-caller cost | ~**₹12–15/call**; ₹15k/mo salary | Talk-Q Global Call Center Labor (2025) |
| Market size | US$125B (2024) → US$345B (2030); D2C ~US$100B | IBEF; Shiprocket; Mordor (2024–26) |

> Full sourced report: `_research/rto-deep-research-perplexity.md` (internal). Positioning honesty:
> these are industry/vendor figures with ranges — lead with the ranges, not a single cherry-picked
> number, and the credibility holds up under scrutiny.
