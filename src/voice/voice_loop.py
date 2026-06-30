"""Live voice loop: Sarvam STT -> RTOAgent (sarvam-30b + tools) -> Sarvam TTS.

This is the user-facing 'A' layer. Each turn: speak the agent line, capture the
customer's speech, transcribe it, get the next agent line, repeat — until the agent
reaches a terminal disposition.
"""
from __future__ import annotations

from agent.rto_agent import RTOAgent
from voice.audio_io import play_wav_bytes, record_until_silence


def run_voice_call(client, order: dict, max_turns: int = 6) -> dict:
    agent = RTOAgent(client, order)
    lang = order["language_code"]

    print(f"\n📞 Calling {order['customer_name']} about order {order['order_id']} "
          f"({order['language_name']})\n")

    def speak(text: str) -> None:
        if not text:
            return
        print(f"🤖 Meera: {text}")
        play_wav_bytes(client.synthesize(text, lang))

    speak(agent.greeting())

    for _ in range(max_turns):
        if agent.is_done:
            break
        audio = record_until_silence()
        stt = client.transcribe(audio, language_code=lang)
        customer_text = stt["transcript"]
        print(f"🙋 Customer: {customer_text}")
        speak(agent.respond(customer_text))

    if not agent.is_done:
        agent.finalize()
    print(f"\n✅ Disposition: {agent.disposition}")
    return agent.outcome()
