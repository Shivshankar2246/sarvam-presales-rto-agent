# Demo Video Script — Project Sampark (3–5 min)

> Goal: in 3–5 minutes, prove all four scoring criteria — real enterprise problem, working
> multilingual demo, meaningful Sarvam usage, clear business value. Record with Loom or QuickTime.
> Keep energy high; you're a pre-sales engineer walking a CTO through a solution, not a coder
> reading code.

**Setup before you hit record:**
- Terminal open in the repo, `.env` with a real `SARVAM_API_KEY` set (for the `--speak` audio).
- The business write-up (`docs/business-writeup.md`) and architecture diagram open in tabs.
- n8n open with the workflow built, and a webhook.site tab visible.
- Audio on (so the Sarvam TTS voice is audible).

---

### [0:00–0:30] The hook — the problem, in money

*(On camera or voiceover over the business write-up's problem table.)*

> "Indian e-commerce has a ₹5-crore-a-year leak called RTO — return to origin. COD orders come
> back at 26%, prepaid at under 2%. And here's the trap: the customers who return the most are
> Tier-2 and Tier-3, regional-language, cash-on-delivery buyers — exactly the people a Hindi-English
> call-center team can't reach. So I built **Sampark**: a voice agent that calls them in *their*
> language, the moment a delivery is at risk, and fixes the order before it fails."

*Why it scores: real enterprise problem + real numbers in the first 30 seconds.*

---

### [0:30–1:00] What it is — the architecture, 20 seconds

*(Show `docs/architecture.md` diagram.)*

> "It's a voice bot plus an agentic backend. The voice agent runs entirely on Sarvam — Saaras for
> speech-to-text, sarvam-30b to reason and decide, Bulbul to speak. When it resolves the call, an
> n8n workflow fans the result out to the OMS, the courier, WhatsApp, and the CRM — automatically.
> That's the difference between a chatbot and an enterprise system."

---

### [1:00–2:30] The demo — three languages, three saves *(the core 90 seconds)*

**Save 1 — Hindi, COD → prepaid (the money shot).** Run with audio:
```bash
python src/run_demo.py --scenario cod_prepaid --mode auto --speak
```
> "Order's out for delivery, ₹1,450 COD. Listen — the agent speaks Hindi." *(let the TTS play)*
> "Customer says he has no cash. Watch: the agent offers a UPI link, and **fires the
> `convert_to_prepaid` tool** — that COD order just became prepaid, and its return-risk dropped
> from 30% to under 2%. That's the single highest-ROI move in the whole system."

**Save 2 — Tamil, reschedule.** 
```bash
python src/run_demo.py --scenario reschedule --mode auto --speak
```
> "Different customer, **Tamil** this time — same agent, no code change. He's travelling, so the
> agent reschedules to tomorrow. `reschedule_delivery` fires."

**Save 3 — Hinglish, address fix.**
```bash
python src/run_demo.py --scenario address --mode auto
```
> "And here's the Sarvam superpower — **code-mixing**. The customer answers in Hinglish:
> *'ground floor likha hai but actually second floor hai, blue gate ke saamne.'* The agent catches
> the correction and fires `update_address`. A generic STT mis-transcribes that line — Saaras
> handles it natively."

*Why it scores: 2+ Indian languages ✓, code-mixing ✓, meaningful Sarvam usage ✓, working demo ✓.*

*(Optional, if you have a mic and want to show live STT: run `--mode voice` and actually speak a
line in Hindi. Powerful if it works on the day — but the scripted `--speak` runs are your safe
take.)*

---

### [2:30–3:30] The agentic backend — n8n fan-out

*(Switch to n8n + the voice service running.)*

```bash
# voice service already running on :8000
curl -X POST http://localhost:5678/webhook-test/sampark-trigger \
     -H 'content-type: application/json' -d @samples/trigger_cod_prepaid.json
```

> "Now the full pipeline. An OMS webhook fires 'out for delivery' into n8n. n8n calls the voice
> agent, the call resolves as `CONVERTED_PREPAID`, and n8n routes on that disposition —
> flipping the OMS to prepaid and firing the WhatsApp payment link." *(show the webhook.site
> payloads landing)* "Event in, systems updated, zero humans. That's the agentic loop."

---

### [3:30–4:30] The business case — why Sarvam, and the ROI

*(Show the ROI table in `docs/business-writeup.md`.)*

> "Conservative case — and I deliberately discounted every number below the industry band — this
> pays back in month one: ~₹11.5 lakh saved against ~₹4.6 lakh in cost, about 2.5x. Upside case,
> 7x. And to cover 100% of COD orders manually you'd need a 30-seat, 10-language, 24/7 team —
> ₹15-to-38 lakh a month. Sampark does it as software.
>
> The reason this *has* to be Sarvam: the entire value is the regional-language, code-mixing,
> low-latency call. That's Sarvam's home turf and a generic US voice stack structurally can't
> follow — wrong languages, broken code-mixing, too much latency, and a DPDP data-residency
> problem on every customer's address and phone number."

---

### [4:30–5:00] Close

> "So that's Sampark — a real enterprise problem, a working multilingual voice agent on Sarvam's
> stack, an agentic backend that closes the loop, and a business case that pays for itself in
> month one. Everything's in the repo — runnable in 30 seconds with the mock, or live with a
> Sarvam key. Thanks for watching."

---

## Recording tips
- **Do the scripted `--speak` runs, not live voice**, as your primary takes — they're reproducible
  and the audio is clean. Keep one live-voice take as a bonus if it works.
- If a TTS call is slow on the day, pre-record the three scenario runs once and keep the clips.
- Show the **disposition JSON** scrolling by at least once — reviewers want to see the structured
  output, not just the chat.
- Total: aim for **3:30–4:00**. Tighter is better than padded.
