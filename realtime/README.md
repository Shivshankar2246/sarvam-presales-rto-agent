# 🎙️ Real-Time Voice Agent (Meera) — Sarvam + Pipecat

A **live, streaming, barge-in** phone-style conversation with Meera, the RTO delivery-rescue
agent. You speak, she listens, **classifies your intent in real time**, and replies — streaming
**Saaras STT → sarvam-30b → Bulbul TTS**, fully local over WebRTC. No cloud account. ₹0 infra
(only Sarvam's free credits).

This is the "advanced" showcase — the [dashboard](../src/dashboard.py) remains the reliable
scripted demo.

## Setup (one-time)
```bash
cd realtime
python3 -m venv .venv && source .venv/bin/activate
pip install "pipecat-ai[sarvam,silero,webrtc,openai]" python-dotenv
cp .env.example .env      # then paste your SARVAM_API_KEY
```

## Run it — the Call Console (recommended, polished UI)
Two terminals:
```bash
# 1) the voice bot
source .venv/bin/activate
python bot.py -t webrtc

# 2) the Call Console web app (serves realtime/console/index.html)
cd console && python3 -m http.server 5500
```
Open **http://localhost:5500** → pick a customer → **📞 Call now** → allow mic → talk.
- Meera greets that customer **by name in their language**, live.
- Watch the **live transcript** + the **🧠 Detected intent** chip update as you speak.
- **Mute / End call** controls, a live call timer, barge-in — like a real call screen.
- Optional: set **"Agent speaks"** (top-right) to force English/Hindi/Tamil.

## Or the bare dev client
Open **http://localhost:7860/client** → **Connect** → **allow the mic** → talk. (Pipecat's generic
test UI — functional but unstyled; use the Call Console above for the demo.)
- Meera greets you and asks about today's delivery.
- Say things like *"I don't have cash right now"* / *"I'm travelling tomorrow"* / *"the address is wrong, it's second floor"* — she understands and responds live.
- **Barge-in works:** interrupt her mid-sentence and she stops and listens.
- Watch the **terminal**: it logs `🧠 CLASSIFIED: CONVERTED_PREPAID (no cash → offer prepaid)` etc. as it understands you — that's the live intent classification.

## Language
Set `REALTIME_LANG` in `.env`: `en-IN` (default, easiest to converse in), `hi-IN`, or `ta-IN`.
Saaras handles code-mixed (Hinglish) speech regardless.

## Notes / gotchas
- **First run is slow (~20s):** the local Silero VAD model downloads once, then caches.
- **Mic:** the browser asks for mic permission — allow it.
- Uses streaming `SarvamTTSService` (not the HTTP/batch one) for low latency.
- Models: STT `saaras:v3`, TTS `bulbul:v2`, LLM `sarvam-30b` (`sarvam-m` is deprecated).
- If a Pipecat constructor kwarg errors, you're on a different Pipecat release — the API moves
  fast; scaffold a fresh quickstart (`pipecat init quickstart`) and port these three services in.
