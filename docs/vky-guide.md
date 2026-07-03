# 🎥 VKY Guide — How to Record the Project Sampark Demo

*For Vignesh. You didn't build this — that's fine. The whole demo now runs from **one dashboard in your browser**. You just open it, click three buttons, and talk. That's it.*

## What you're recording
A **3-minute screen recording** with your voice over it, using the **Delivery Rescue Console** — a clean dashboard (no code, no terminal). You'll:
1. Show the business problem (the numbers on screen)
2. Click **"Call now"** on three at-risk orders and watch the AI rescue each one — in **Hindi, Tamil, and Hinglish**
3. Point at the results and read the closing line

Keep [`demo-script.md`](demo-script.md) open on your phone or a second screen — you'll read the **Voiceover** column.

---

## PART 0 — Start the dashboard (2 minutes, once)

Open **Terminal** and run these three lines:
```
cd ~/Documents/sarvam-presales-rto-agent
source .venv/bin/activate
streamlit run src/dashboard.py
```
Your browser opens automatically to the console (usually `http://localhost:8501`).

✅ **Check the header** — it should say **"Live · Sarvam AI"**.
❌ If it says **"Demo mode"**, the API key is missing — tell Shiv to add `SARVAM_API_KEY` to the `.env` file, then restart (Ctrl+C in the terminal, run the `streamlit` line again). *(Demo mode still works, but you won't HEAR the voice — you'll only see the text.)*

> After this, you never touch the terminal again. Everything happens in the browser.

---

## PART 1 — Set up screen recording (with audio!)

⚠️ To capture the AI **voice**, use **Loom** (free desktop app) and turn on **"System audio"** (or "Tab audio"). Plain QuickTime records your mic only, so the AI voice won't be captured.

1. Install/open **Loom desktop** → choose **Screen + Mic + System audio**.
2. Turn your Mac volume up to about 60–70%.
3. **Do a 10-second test:** hit record, click one "Call now" button, stop, play it back. Confirm you can see the screen AND hear both **your voice** and the **AI voice**.
4. Delete the test. You're ready.

---

## PART 2 — Record the demo (~3 min)

> Read the matching **Voiceover** line from `demo-script.md` as you go. Speak slowly. **Pause while the AI is talking** so the reviewer hears it.

### 🎬 Scene 1 — The problem (0:00–0:25)
- The dashboard is on screen. Point at the top numbers: **"342 orders at risk"** and **"₹5.5 Cr"**.
- **Say** the opening line.

### 🎬 Scene 2 — Rescue #1: Rakesh, Hindi (0:25–1:05)
- Click **"📞 Call Rakesh now"** (top order on the left).
- Wait — a conversation appears and you'll **hear Hindi**. Let it finish (don't talk over the voice).
- When the green **"Converted to Prepaid"** card + the three **"Systems updated"** cards appear, **say** the Hindi narration. Point at the three cards.

### 🎬 Scene 3 — Rescue #2: Lakshmi, Tamil (1:05–1:35)
- Click **"📞 Call Lakshmi now"**.
- Let the **Tamil** call play. When "Delivery Rescheduled" appears, **say** the Tamil line.

### 🎬 Scene 4 — Rescue #3: Priya, Hinglish (1:35–2:10)
- Click **"📞 Call Priya now"**.
- Let the **Hinglish** call play. When "Address Corrected" appears, **say** the code-mixing line. (This is the strongest moment — emphasize it.)

### 🎬 Scene 5 — The scoreboard + close (2:10–2:55)
- Point at the KPI **"Rescued this session: 3"** at the top (it counts up as you go).
- **Say** the ROI / closing line.
- *(Optional, for the technical reviewer):* switch to the n8n tab OR the GitHub page for ~10 seconds and say the "this isn't a mockup" line, then say "That's Project Sampark. Thank you."

---

## PART 3 — After recording
1. **Stop** the recording. Watch it back once — check you can hear the AI voice and see the green result cards.
2. **Get the link:** Loom gives one automatically. (Or upload the file to **YouTube → Unlisted**, or **Google Drive → "anyone with link"**.)
3. **Send the link to Shiv** (he'll put it in the README) — or paste it into the README yourself, replacing `[▶ 3-min walkthrough — LINK TO BE ADDED]`.

---

## 🆘 Troubleshooting
- **"command not found: streamlit / python"** → you skipped `source .venv/bin/activate`. Run it first.
- **Header says "Demo mode"** → no API key. Ask Shiv to add `SARVAM_API_KEY` to `.env`, then restart the dashboard.
- **No AI voice in the recording** → either your Loom isn't capturing System audio, or the dashboard is in Demo mode. Fix whichever it is (see above), or just narrate over the on-screen text.
- **A call seems stuck on "Connecting…"** → it's making the real AI call, give it ~5–10 seconds. If it errors, click the button once more.
- **Fumbled a line?** → just pause and re-click that order to replay it, or re-record the whole 3 minutes — it's short.
