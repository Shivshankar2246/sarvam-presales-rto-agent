# 🎬 Demo Video Script — Project Sampark

> A **Problem-Agitate-Solve** pitch for a business audience (COO / VP Ops / CEO). It opens on the
> **Delivery Rescue Console** (dashboard) for the business story, then **climaxes on a real live call
> that drives the backend** — a live Tamil conversation → n8n updates every delivery system on screen.
> "How it works" is a short, opt-in deep-dive at the end.
> Pre-Sales Engineer Assignment · **Vignesh Srinivasan** · Target runtime: **~3:30**

---

## Setup before you hit record
- **Dashboard:** `streamlit run src/dashboard.py` → header should say **"Live · Sarvam AI"**
- **Live call:** `cd realtime && python bot.py -t webrtc` (bot) + `cd realtime/console && python3 -m http.server 5500` (Console at localhost:5500)
- **n8n:** the **Sampark — Live Resolve** workflow is **Activated**; keep the n8n canvas (or your webhook.site tab) visible for the fan-out beat
- `.env` has a real `SARVAM_API_KEY` (so you HEAR the voice); `realtime/.env` → `REALTIME_LANG=ta-IN`
- Record with **Loom** + **System audio ON**; do a 10-sec test first
- Full presenter walkthrough: [`vky-guide.md`](vky-guide.md)

---

## The script (Problem → Agitate → Solve → Prove-it-live → Benefits → How it works)

| Section | On screen | Voiceover |
|---|---|---|
| **PROBLEM** (0:00–0:25) | Dashboard header; "Return-to-Origin" | "If you sell to India, you already know this pain. Most of your customers pay **Cash-on-Delivery** — and COD orders don't always get delivered. They come **back**. It's called **Return-to-Origin**, and it's the quiet tax on every D2C brand in the country." |
| **AGITATE** (0:25–1:05) | Contrast numbers: **30–40% vs 5–7%**, then **₹300–700/return** and **₹5 Cr+/yr** | "Here's how bad it is. A **prepaid** order comes back 5 to 7% of the time. A **COD fashion** order? **30 to 40%** — up to **eight times worse**. And each return costs **₹300 to ₹700** — freight out, freight back, packaging, and the marketing money you spent to win a customer who never gets the order. One return wipes out the profit of **three successful orders**. For a brand shipping a lakh orders a month, that's **over ₹5 crore a year** in logistics alone — and closer to **₹11 crore** once you count the wasted ad spend. And it's getting **worse**: two-thirds of new growth is **Tier-2 and Tier-3 India**, where customers speak their own language and won't answer an English text — the exact orders your call team **can't reach**." |
| **SOLVE — the breadth** (1:05–1:50) | Dashboard: click Rakesh → Lakshmi → Priya, let each rescue play with audio | "So here's the fix. This is **Sampark** — an AI agent that calls those at-risk customers **in their own language** and saves the order before it fails. Watch. *(click Rakesh)* **Hindi** — no cash, so it offers **free shipping and a UPI link**, he pays on the call, return risk drops from 30% to under 2. *(click Lakshmi)* **Tamil** — she's travelling, so it **reschedules**. *(click Priya)* **Hinglish** — messy address, **fixed on the call**. Three languages, three saves." |
| **PROVE IT LIVE** (1:50–2:50) | **Switch to the Call Console.** Click **Call Lakshmi** → speak Tamil → let Meera reply → the **"Captured"** panel fills → then show the **n8n canvas / webhook.site** lighting up | "But this isn't a slideshow — let me actually **talk to it.** *(Call Lakshmi, speak in Tamil: 'I'm travelling, deliver tomorrow')* Notice she understood my **Tamil**, replied live, and I could even **interrupt her**. And here's the part that matters — the moment she captured the outcome, watch: *(point at the card)* **it fired straight into our systems.** *(switch to n8n / webhook.site)* The order system, the courier, the CRM — **all updated automatically**, from a live phone call, with **nobody on the team touching anything.** That's the whole thing working end to end." |
| **BENEFITS** (2:50–3:10) | KPI "Rescued: 3" + ₹5.5 Cr projection | "That's the outcome: **fewer returns, more delivered orders, recovered margin** — 24/7, in **every Indian language**, with **zero extra headcount**. Confirmation calls like these cut returns by **15 to 40%** — and conservatively, this **pays for itself 2.5× in the first month**." |
| **HOW IT WORKS** *(opt-in deep-dive)* (3:10–3:35) | Brief architecture diagram | "And if you're curious **how it works** — the 30-second version. Sampark runs a real streaming call on **Sarvam's Indian-language AI**: it listens, understands code-mixed speech, and speaks in the customer's language, decides the fix, and an **automation engine (n8n)** updates every system — with all customer data **staying in India**. That's **Project Sampark**. Thank you." |

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
- **~150 words/min** → this lands at ~3:30. **Pause while the AI voice speaks** so the reviewer hears the quality.
- The AGITATE section is where the pitch lives — slow down, let each number land.
- **PROVE IT LIVE is the moment that wins it.** The dashboard shows breadth; the live call shows it's *real*. Speak your Tamil line clearly, wait for Meera, then **switch windows to n8n/webhook.site** so the reviewer sees the systems update from your live call. This is the A+B proof.
- Practise the live call 2–3 times before recording (STT does best with a clear, unhurried line). If a live call ever mis-hears on the take, just re-call — it's a few seconds.
- Keep the "how it works" beat — the reviewer is Sarvam's technical team, and the live n8n fan-out already proved it's not a slideshow.

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
