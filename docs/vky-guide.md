# 🎥 VKY Guide — How to Record the Project Sampark Demo

*For Vignesh. You didn't build this — that's fine. This guide walks you through it click by click.
The demo has two halves: a **dashboard** (click buttons, watch saves) for the story, and **one real
live call** where you actually talk to the AI in Tamil and watch it update the delivery systems by
itself. That live call is the moment that wins it.*

## What you're recording
A **~3.5-minute screen recording** with your voice over it. You'll:
1. Show the business problem (the numbers on the dashboard)
2. Click **"Call now"** on three orders — Hindi, Tamil, Hinglish saves (the breadth)
3. **Make ONE real live call** in Tamil, talk to Meera, and show **n8n updating every system** from that call (the proof)
4. Read the closing line

Keep [`demo-script.md`](demo-script.md) open on your phone or a second screen — read the **Voiceover** column.

---

## PART 0 — Start everything (do this once, ~3 min)

> Easiest: ask **Shiv** to start these before you record, or run them yourself. You need **three
> things running** + **one browser check**. Open **Terminal** for each.

**1) The dashboard** (Terminal 1):
```
cd ~/Documents/sarvam-presales-rto-agent
source .venv/bin/activate
streamlit run src/dashboard.py
```
→ browser opens to `http://localhost:8501`. ✅ Header must say **"Live · Sarvam AI"** (not "Demo mode").

**2) The live voice bot** (Terminal 2):
```
cd ~/Documents/sarvam-presales-rto-agent/realtime
source .venv/bin/activate
python bot.py -t webrtc
```
→ leave it running. (First start takes ~20s.)

**3) The Call Console** (Terminal 3):
```
cd ~/Documents/sarvam-presales-rto-agent/realtime/console
python3 -m http.server 5500
```
→ open **http://localhost:5500** in your browser.

**4) n8n check (in the browser):** open your n8n → the **"Sampark — Live Resolve"** workflow →
confirm the toggle top-right is **green (Active)**. Also open your **webhook.site** tab — that's
where you'll *see* the systems update. (Shiv has both links.)

> If any of this feels like a lot — that's Shiv's job. Once it's all running, you only touch the
> **browser** to record.

---

## PART 1 — Set up screen recording (with audio!)

⚠️ To capture the AI **voice**, use **Loom** (free desktop app) and turn on **"System audio"**.
Plain QuickTime records your mic only, so the AI voice won't be captured.

1. Install/open **Loom desktop** → choose **Screen + Mic + System audio**.
2. Turn your Mac volume up to about 60–70%.
3. **10-second test:** hit record, click one "Call now" button, say a word, stop, play it back.
   Confirm you can see the screen AND hear both **your voice** and the **AI voice**.
4. Delete the test. You're ready.

---

## PART 2 — Record the demo (~3.5 min)

> Read the matching **Voiceover** line from `demo-script.md`. Speak slowly. **Pause while the AI
> talks** so the reviewer hears the quality.

### 🎬 Scene 1 — The problem (0:00–0:25)
- Dashboard on screen. Point at the top numbers: **"342 orders at risk"** and **"₹5.5 Cr"**.
- **Say** the opening (PROBLEM) line.

### 🎬 Scene 2 — The breadth: 3 quick saves (0:25–1:50)
- On the dashboard, click **Call Rakesh** (Hindi) → let it play → **Call Lakshmi** (Tamil) → **Call Priya** (Hinglish).
- Let each short rescue play (don't talk over the AI voice). **Say** the SOLVE line as they land.
- This shows range: three languages, three saves. Keep it brisk.

### 🎬 Scene 3 — ⭐ PROVE IT LIVE: the real call + n8n (1:50–2:50)  ← the moment that wins it
1. **Switch to the Call Console tab** (`localhost:5500`).
2. Click **📞 Call Lakshmi** → allow the mic if asked.
3. Wait for Meera to greet you in **Tamil**, then **speak your Tamil line** clearly, e.g.
   *"நான் ஊருக்கு போறேன், நாளைக்கு டெலிவரி பண்ணுங்க"* ("I'm travelling, deliver tomorrow").
4. Let her reply. *(Optional flourish: interrupt her mid-sentence to show barge-in.)*
5. Watch the **"Captured on this call"** card appear on the right — it will show
   **"→ n8n: delivery systems updated ✓"**. Point at it.
6. **Switch to your n8n canvas (or webhook.site tab)** — show the workflow lit up / the payload that
   just landed. **Say** the PROVE-IT-LIVE line: *"…from a live phone call, with nobody touching anything."*

> This is the whole product working end to end — a live Tamil call updating real systems. Linger here.

### 🎬 Scene 4 — Benefits + close (2:50–3:35)
- Back to the dashboard. Point at **"Rescued this session: 3"** and the **₹5.5 Cr** number.
- **Say** the BENEFITS line, then the **HOW IT WORKS** deep-dive, then: *"That's Project Sampark. Thank you."*

---

## PART 3 — After recording
1. **Stop** the recording. Watch it back once — check you can hear the AI voice, and that Scene 3
   clearly shows the live call **and** the n8n/webhook.site update.
2. **Get the link:** Loom gives one automatically. (Or upload to **YouTube → Unlisted**, or **Google Drive → "anyone with link"**.)
3. **Send the link to Shiv** — or paste it into the README yourself, replacing `[▶ 3-min walkthrough — LINK TO BE ADDED]`.

---

## 🆘 Troubleshooting
- **"command not found: streamlit / python"** → you skipped `source .venv/bin/activate`. Run it first.
- **Dashboard header says "Demo mode"** → no API key. Ask Shiv to add `SARVAM_API_KEY` to `.env`, restart the dashboard.
- **Call Console won't connect / "is the bot running?"** → Terminal 2 (`python bot.py -t webrtc`) isn't running, or still warming up (~20s). Start it, wait, click Call again.
- **Live call: Meera mis-hears your Tamil** → speak one clear, unhurried sentence; end the call and re-call. It only takes a few seconds. Practise 2–3 times before the real take.
- **Captured card shows "→ n8n unreachable" or an error** → the **Sampark — Live Resolve** workflow isn't **Active** in n8n. Toggle it on (top-right) and re-call. (If it still fails, tell Shiv — the webhook URL may need updating.)
- **Nothing appears on webhook.site** → make sure you opened the *same* webhook.site tab whose URL is wired into n8n (ask Shiv), and that the workflow is Active.
- **No AI voice in the recording** → Loom isn't capturing System audio, or the dashboard is in Demo mode. Fix whichever, or narrate over the on-screen text.
- **Fumbled a line?** → pause, re-click that order (or re-call), or re-record the whole thing — it's short.
