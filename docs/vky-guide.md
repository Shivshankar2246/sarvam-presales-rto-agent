# 🎥 VKY Guide — How to Record the Project Sampark Demo

*For Vignesh. You didn't build this — that's fine. This guide walks you through it click by click.
The demo has two halves: a **dashboard** (click buttons, watch saves) for the story, and **one real
live call** where you actually talk to the AI in Tamil and watch it update the delivery systems by
itself. That live call is the moment that wins it.*

## What you're recording
A **~3-minute screen recording** with your voice over it. You'll:
1. Say the business problem (the RTO numbers)
2. Show the **three customers** in the Call Console and point out their **languages**; pick **Lakshmi (Tamil)**
3. **Make ONE real live call** in Tamil and just **talk to the agent** — no script (this is the star)
4. Show **n8n** (one sentence: it updates the systems) and **webhook.site** (the outcome is saved) — the proof
5. Read the closing line

Keep [`demo-script.md`](demo-script.md) open on your phone or a second screen — read the **Voiceover** (framing) lines. **Don't script the call — just talk.**

---

## PART 0 — Start everything (do this once, ~3 min)

> Easiest: ask **Shiv** to start these before you record, or run them yourself. You need the **bot
> + Console running** + an **n8n browser check**. Open **Terminal** for each.

**1) The dashboard — OPTIONAL** (Terminal 1, only if you want the numbers on screen for the opening):
```
cd ~/Documents/sarvam-presales-rto-agent
source .venv/bin/activate
streamlit run src/dashboard.py
```
→ browser opens to `http://localhost:8501`. (Skip this if you'll just narrate the numbers.)

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

## PART 2 — Record the demo (~3 min)

> Read the matching **Voiceover** (framing) lines from `demo-script.md`. Speak slowly. **The call
> itself is NOT scripted — just talk.** Pause while the agent speaks so the reviewer hears the quality.

### 🎬 Scene 1 — The problem (0:00–1:00)
- Show the RTO numbers (dashboard if you started it, or just talk). **Say** the PROBLEM + AGITATE lines.

### 🎬 Scene 2 — Meet the customers (1:00–1:20)
- On the **Call Console** (`localhost:5500`), point at the **three customer cards** — each shows its
  **language** (Rakesh = Hindi, Lakshmi = Tamil, Priya = Hinglish).
- **Say** the MEET-THE-CUSTOMERS line: *"…for this demo I'll call Lakshmi, she speaks Tamil."*
- Click **📞 Call Lakshmi** → allow the mic if asked.

### 🎬 Scene 3 — ⭐ THE LIVE CALL (1:20–2:20)  ← the star, don't script it
1. Wait for the agent to greet you in **Tamil**.
2. **Just talk to her in Tamil** — about any delivery issue (you're travelling, wrong address, etc.).
   **No script.** Speak clearly and unhurried.
3. *(Nice flourish: interrupt her mid-sentence once to show barge-in.)*
4. When the **"Captured on this call"** card appears (showing **"→ n8n: delivery systems updated ✓"**),
   **pause on it** — that's the outcome being captured.

> This is the whole product being real — a live Tamil conversation. Let it breathe; don't narrate over it.

### 🎬 Scene 4 — ⭐ The proof: n8n + webhook.site (2:20–2:55)
1. **Switch to your n8n canvas.** **Say** the one-liner: *"This is the automation engine — the second
   the call ends, it updates every delivery system automatically."* (Point at the workflow.)
2. **Switch to your webhook.site tab.** Point at the newest entry. **Say:** *"And here's the proof —
   the outcome of that call is saved right here, nobody touched anything."*

### 🎬 Scene 5 — Benefits + close (2:55–3:15)
- **Say** the BENEFITS line, then close: *"That's Project Sampark. Thank you."*

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
