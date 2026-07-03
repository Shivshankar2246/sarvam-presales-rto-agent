# 🎥 VKY Guide — How to Record the Project Sampark Demo

*For Vignesh. You didn't build this — that's fine. Follow these steps exactly and you'll have a clean 3-minute demo.*

## What you're recording
A **3-minute screen recording** with your voice over it, showing two things:
1. An **AI voice agent** handling delivery calls in **Hindi, Tamil, and Hinglish** (in a terminal)
2. An **n8n automation** reacting to those calls (in the browser)

You'll **read the narration** from [`demo-script.md`](demo-script.md) while you click through. Keep that file open on your phone or a second screen.

---

## PART 0 — Get the environment ready (do this before recording)

> Everything is already set up on this machine. You just need to start 2 things and open 2 browser tabs. If Shiv already has these running, just confirm and skip to Part 1.

**① Terminal window — start the "brain" (only needed for the n8n part):**
```
cd ~/Documents/sarvam-presales-rto-agent
source .venv/bin/activate
cd src
uvicorn server:app --port 8000
```
✅ Success looks like: `Application startup complete.` → **leave this window open, don't touch it.**

**② A SECOND terminal window** (Cmd+N) — this is where you'll type the demo commands:
```
cd ~/Documents/sarvam-presales-rto-agent
source .venv/bin/activate
```

**③ Browser tab — n8n:** open your **"Sampark — Trigger & Resolve"** workflow.

**④ Browser tab — webhook.site:** open the webhook.site tab (the one whose URL is in your n8n nodes).

---

## PART 1 — Set up screen recording (with audio!)

⚠️ **Important:** to capture the Hindi/Tamil **voice** in the recording, use **Loom** (free desktop app) and turn on **"System audio."** Plain QuickTime records your mic only, so the AI voice won't be captured.

- **Recommended:** Loom desktop → record **Screen + Mic + System audio**.
- **No Loom?** Use QuickTime (File → New Screen Recording) and run the demo commands **without `--speak`** — the reviewer will read the conversation on screen instead of hearing it. Still works great.
- **Do a 10-second test recording first.** Play it back. Confirm you can see the screen AND hear both your voice and (if using Loom) the AI voice.

---

## PART 2 — Record the demo (5 scenes, ~3 min)

> Read the matching **Voiceover** line from [`demo-script.md`](demo-script.md) as you do each step.

### 🎬 Scene 1 — The problem (0:00–0:30)
- **Show:** open `docs/business-writeup.md`, scroll to the problem/ROI numbers.
- **Say:** the opening hook from the script (the "₹5.5 crore / Return to Origin" line).

### 🎬 Scene 2 — What it is (0:30–0:47)
- **Show:** open `docs/architecture.md` and press **Cmd+Shift+V** to see the diagram.
- **Say:** the architecture line ("Two halves… Saaras… sarvam-30b… Bulbul…").

### 🎬 Scene 3 — The voice agent, 3 languages (0:47–2:00) — *the star of the show*
In your **second terminal**, run these one at a time. Wait for each to finish (and the voice to play) before the next:

**Hindi (COD → prepaid):**
```
python src/run_demo.py --scenario cod_prepaid --mode auto --speak
```
→ **Say** the Hindi-save narration. Point out the **`convert_to_prepaid`** tool firing.

**Tamil (reschedule):**
```
python src/run_demo.py --scenario reschedule --mode auto --speak
```
→ **Say** the Tamil-save line.

**Hinglish (address fix):**
```
python src/run_demo.py --scenario address --mode auto
```
→ **Say** the code-mixing line. Point at the transcript.

> If you're NOT using Loom/system-audio, drop `--speak` from all three — the conversation still prints on screen.

### 🎬 Scene 4 — The n8n automation (2:00–2:35)
1. Switch to the **n8n** browser tab.
2. Click the big **"Execute workflow"** button (bottom center). It starts listening.
3. Switch to your **second terminal** and paste this (ask Shiv for the exact n8n webhook URL — it's your hosted n8n's "Test URL"):
   ```
   curl -X POST '<YOUR-N8N-WEBHOOK-TEST-URL>' -H 'content-type: application/json' -d @samples/trigger_cod_prepaid.json
   ```
4. Switch back to **n8n** — watch the nodes turn **green** left to right (wait ~10 seconds, it's calling the real AI).
5. Switch to the **webhook.site** tab — show the **3 new payloads** that landed (`mark_prepaid`, `prepaid_confirmed`, the CRM log).
- **Say:** the n8n narration ("Event in, systems updated, no human in the loop").

### 🎬 Scene 5 — ROI + close (2:35–3:00)
- **Show:** the ROI table in `docs/business-writeup.md`.
- **Say:** the closing line ("pays for itself 2.5x in month one… only works on Sarvam… That's Project Sampark").

---

## PART 3 — After recording
1. **Stop** the recording. Watch it back once — check audio + that the tools/payloads are visible.
2. **Upload:** Loom gives a link automatically; or upload the file to **YouTube (set to Unlisted)** or **Google Drive (set to "anyone with link")**.
3. **Copy the share link** and send it to Shiv (he'll put it in the README) — or paste it into the README yourself, replacing `[▶ 3-min walkthrough — LINK TO BE ADDED]`.

---

## 🆘 Troubleshooting
- **"command not found: uvicorn/python"** → you forgot `source .venv/bin/activate`. Run it first.
- **No sound in the recording** → you're on QuickTime (mic only). Either switch to Loom + System audio, or run the demos without `--speak`.
- **n8n nodes turn red** → the voice service (window ①) probably stopped, or the tunnel changed. Ask Shiv — this is the one part that needs the setup intact. *(Safe fallback: if n8n has pinned data, just click "Execute workflow" with no curl — it replays the last result instantly.)*
- **Fumbled a line?** → just pause, and re-do that one scene. You can trim/stitch later, or re-record the whole 3 min — it's short.
