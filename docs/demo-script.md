# 🎬 Demo Video Script — Project Sampark

> 3-minute walkthrough for a **business audience (COO / VP Ops / CEO)** — driven entirely by
> the **Delivery Rescue Console** (Streamlit dashboard). No terminal, no code on screen.
> Pre-Sales Engineer Assignment · **Vignesh Srinivasan** · Target runtime: **~3:00**

---

## Setup before you hit record

- Start the dashboard: `streamlit run src/dashboard.py` → it opens in your browser
- Confirm `.env` has a real `SARVAM_API_KEY` (needed so you HEAR the AI voice, not just read it)
- The header should say **"Live · Sarvam AI"** (not "Demo mode")
- Record with **Loom** (desktop) with **System/Tab audio ON** so the AI voice is captured
- Do a 10-second test recording and play it back — confirm screen + your voice + the AI voice

*(Full presenter walkthrough: [`vky-guide.md`](vky-guide.md).)*

---

## The script

| Time | On screen | Voiceover (read this aloud) |
|---|---|---|
| **0:00–0:25** | Dashboard loaded — header + KPI strip (**₹5.5 Cr**, **342 orders at risk**) | "This is a live console for an Indian D2C brand. Right now, **342 cash-on-delivery orders** are at risk of coming back — and over a year, returns like these cost a brand this size **five and a half crore rupees**. Watch what happens when the AI steps in." |
| **0:25–1:05** | Click **"Call Rakesh now"** → let the Hindi conversation play with audio → resolution + the 3 auto-action cards appear | "Rakesh's order is out for delivery — but he has no cash. I'll let the agent call him." *(click; let the audio play)* "It's speaking **Hindi**. He has no cash, so the agent offers a **UPI link** — and he pays on the spot. That one move drops this order's return risk from **30% to under 2**. And look — the order system, WhatsApp, and the CRM all update **themselves**. No human touched anything." |
| **1:05–1:35** | Click **"Call Lakshmi now"** → Tamil conversation → "Rescheduled" | "Different customer, different city — and now it's **Tamil**. Same agent, no changes. She's travelling, so it **reschedules** to a slot she confirms out loud, and tells the courier." |
| **1:35–2:10** | Click **"Call Priya now"** → Hinglish conversation → "Address Corrected" | "And here's the hard one — real Indian phone speech **mixes languages**. Priya answers in Hinglish: *'ground floor likha hai, but actually second floor hai.'* The agent catches it, **fixes the address**, and re-routes the parcel for today. This is exactly where a generic, English-first system breaks — and where **Sarvam** wins." |
| **2:10–2:40** | Point at the KPI **"Rescued this session: 3"** + the **₹5.5 Cr** projection | "Three calls, three saves — in **three languages**, in under two minutes. At this brand's volume, that's **five and a half crore rupees a year, recovered**. Conservatively, the system **pays for itself 2.5 times over in month one**." |
| **2:40–2:55** *(optional — for the technical reviewer)* | Brief flash of the n8n canvas or the GitHub repo | "And this isn't a mockup. Every call runs on **real Sarvam APIs**, and an automation engine fires those system updates end-to-end. The full build is on GitHub." |
| **2:55–3:00** | Back to the console | "That's **Project Sampark**. Thank you." |

---

## Alternate opening hooks (pick the one you'll deliver best)
- **A (recommended):** "This is a live console for an Indian D2C brand. Right now, 342 orders are at risk of coming back…"
- **B (money-first):** "Indian D2C brands lose crores a year to one thing — deliveries that come back. Let me show you a console that stops it, one call at a time."
- **C (rhetorical):** "What if you could save a failing delivery with a single phone call — in the customer's own language, with no staff involved? Watch."

## Alternate closing lines
- **A (recommended):** "…That's Project Sampark. Thank you."
- **B (forward-looking):** "…It's a proof-of-concept today, but the full production plan is in the repo. That's Project Sampark."

---

## Delivery notes
- **~150 words/min** lands this at 3:00. Let the AI voice **breathe** — pause your narration while it speaks so the reviewer hears the voice quality.
- The dashboard does the work — you just **click 3 buttons and talk**. Point at the **auto-action cards** and the **KPI counter** as they update; that's the "no humans in the loop" story landing visually.
- The optional "under the hood" beat (2:40) is worth including — the reviewer is Sarvam's technical team, and it proves it's real, not a slideshow.
- Aim for **2:45–3:00**. Tighter beats padded.
