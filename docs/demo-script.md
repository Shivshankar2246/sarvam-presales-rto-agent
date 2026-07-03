# 🎬 Demo Video Script — Project Sampark

> 3-minute walkthrough voiceover, mapped beat-by-beat to on-screen actions.
> Pre-Sales Engineer Assignment · **Vignesh Srinivasan** · Target runtime: **~3:00**

---

## Setup before you hit record

- **Voice service** running with a real key: `cd src && uvicorn server:app --port 8000`
  (if n8n is remote, expose it: `cloudflared tunnel --url http://localhost:8000`)
- **n8n** open with the workflow built + a **webhook.site** tab visible
- **`docs/business-writeup.md`** (ROI table) and **`docs/architecture.md`** (diagram) open in tabs
- Audio **on** — so the Sarvam TTS voice is audible
- Record with Loom or QuickTime · export to Loom / YouTube (unlisted) / Google Drive

---

## The script

| Time | On screen | Voiceover (read this aloud) |
|---|---|---|
| **0:00–0:15** | Bold number: **₹5.5 crore / year** (or the write-up's problem table) | "Every year, Indian D2C brands burn crores on one silent leak: **Return to Origin**. Cash-on-delivery orders come back at **26%** — versus under 2 for prepaid. For a brand shipping a lakh orders a month, that's **five and a half crore rupees, gone.**" |
| **0:15–0:32** | Highlight "Tier 2/3 · regional-language · COD" → title card **"Project Sampark"** | "And the customers who return the most are the ones your call-center **can't reach** — small-town, cash-first, regional-language buyers. So I built **Sampark**: a voice agent that calls them in **their own language** the moment a delivery is at risk, and fixes the order before it fails. It runs on **Sarvam**." |
| **0:32–0:47** | `docs/architecture.md` diagram | "Two halves. A **voice bot** — Sarvam listens with **Saaras**, reasons with **sarvam-30b**, and speaks with **Bulbul**. And an **agentic backend** in n8n that turns every call into real action across your systems. Let me show you." |
| **0:47–1:15** | Terminal: `run_demo.py --scenario cod_prepaid --speak` — *let the Hindi TTS play ~5s* | "Order out for delivery, ₹1,450 in cash. Listen — the agent speaks **Hindi**." *(pause for audio)* "The customer has no cash. So the agent offers a **UPI link** and fires the **convert-to-prepaid** tool. That one move drops this order's return-risk from 30% to under 2." |
| **1:15–1:35** | Terminal: `--scenario reschedule --speak` (Tamil audio) | "Different customer — **Tamil** now. Same agent, zero code change. He's travelling, so it **reschedules** to a slot he confirms out loud." |
| **1:35–2:00** | Terminal: `--scenario address` (Hinglish) — highlight the transcript line | "And here's **Sarvam's edge — code-mixing**. The customer answers in **Hinglish**: *'ground floor likha hai, but actually second floor hai.'* Saaras catches it, the agent **fixes the address**. A generic transcriber mangles that line — this is exactly where a US voice stack breaks." |
| **2:00–2:35** | n8n canvas → fire the `curl` → nodes go green → webhook.site payloads land | "Now the **other half**. An order-management webhook fires 'out for delivery' into **n8n**. n8n runs the call, the outcome comes back as **converted-to-prepaid**, and n8n **routes on it** — flipping the OMS to prepaid and sending the WhatsApp payment link. Event in, systems updated, **no human in the loop.**" |
| **2:35–2:55** | ROI table from `business-writeup.md` | "The math is simple. Conservatively, this **pays for itself 2.5 times over in month one**. And it only works on **Sarvam** — the whole value is a low-latency, regional-language, code-mixing call, with the customer's data **staying in India**. A generic stack can't follow. That's **Project Sampark**. Thanks for watching." |

---

## Alternate opening hooks (pick the one you'll deliver best)

- **A (money-first — recommended):** "Every year, Indian D2C brands burn crores on one silent leak: Return to Origin…" — leads with the number, hardest-hitting.
- **B (rhetorical):** "What if the customers who return the most are the exact ones your call-center can never reach? In Indian e-commerce, they are — and it costs brands crores."
- **C (cold-cut to the demo):** "This is an AI agent calling a customer in Hindi to save a delivery that was about to fail. Let me show you why that's a five-crore problem."

## Alternate closing lines

- **A (recommended):** "…A generic stack can't follow. That's Project Sampark. Thanks for watching."
- **B (forward-looking):** "…It's a proof-of-concept today — but every piece a production rollout needs is mapped in the repo. That's Project Sampark."

---

## Delivery notes

- **~150 words/min** pace lands this right at 3:00. Don't rush the Hindi/Tamil audio — let it breathe so the reviewer hears the voice quality.
- Record the three `--speak` runs as your **safe takes** (reproducible); keep one live `--mode voice` take as a bonus if it works on the day.
- Show the **disposition JSON** and the **webhook.site payloads** on screen at least once — reviewers want to see structured output, not just chat.
- Before recording: **unpin** the n8n data and **restart the voice service** so the run is fully live.
- Aim for **2:45–3:00**. Tighter beats padded.
