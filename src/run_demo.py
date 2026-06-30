"""Project Sampark — runnable demo entrypoint.

Examples:
    # Offline, scripted (no key needed) — replays the Hindi COD->prepaid call:
    python src/run_demo.py --scenario cod_prepaid --mode auto

    # Type the customer's responses yourself:
    python src/run_demo.py --scenario reschedule --mode text

    # Live voice (needs SARVAM_API_KEY + mic): real STT/LLM/TTS in-language:
    python src/run_demo.py --scenario address --mode voice

    # Auto mode but PLAY the agent's real Sarvam TTS audio (great for the demo video):
    python src/run_demo.py --scenario cod_prepaid --mode auto --speak
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # make src/ importable

from agent.rto_agent import RTOAgent  # noqa: E402
from agent.scenarios import SCENARIOS, get_scenario  # noqa: E402
from config import CHAT_MODEL, settings  # noqa: E402
from sarvam_client import get_client  # noqa: E402


def _banner(order: dict, client) -> None:
    mode = "MOCK (no API key — offline scripted)" if getattr(client, "is_mock", False) else f"REAL Sarvam ({CHAT_MODEL})"
    print("=" * 72)
    print("  PROJECT SAMPARK — RTO-reduction voice agent")
    print(f"  Backend: {mode}")
    print(f"  Call:    {order['customer_name']}  ·  order {order['order_id']}  ·  {order['language_name']}")
    print(f"  Trigger: {order['status']}  ·  COD Rs {order['cod_amount']}  ·  {order['item']}")
    print("=" * 72 + "\n")


def _maybe_speak(client, text: str, lang: str, enabled: bool) -> None:
    if not enabled or not text:
        return
    try:
        from voice.audio_io import play_wav_bytes

        play_wav_bytes(client.synthesize(text, lang))
    except Exception as e:
        print(f"   (audio playback skipped: {e})")


def run(scenario_name: str, mode: str, speak: bool) -> dict:
    client = get_client()
    sc = get_scenario(scenario_name)
    order = sc["order"]
    lang = order["language_code"]

    if mode == "voice":
        from voice.voice_loop import run_voice_call

        return run_voice_call(client, order)

    _banner(order, client)
    agent = RTOAgent(client, order)

    greeting = agent.greeting()
    print(f"🤖 Meera: {greeting}")
    _maybe_speak(client, greeting, lang, speak)

    scripted = iter(sc["customer_lines"]) if mode == "auto" else None
    for _ in range(8):
        if agent.is_done:
            break
        if mode == "auto":
            customer_text = next(scripted, None)
            if customer_text is None:
                break
            print(f"🙋 Customer: {customer_text}")
        else:  # text
            try:
                customer_text = input("🙋 You (customer): ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if customer_text.lower() in ("quit", "exit", ""):
                break

        reply = agent.respond(customer_text)
        print(f"🤖 Meera: {reply}")
        _maybe_speak(client, reply, lang, speak)

    # End-of-call: ensure a disposition is recorded even if the model chatted without committing.
    if not agent.is_done:
        agent.finalize()

    outcome = agent.outcome()
    print("\n" + "-" * 72)
    print(f"✅ DISPOSITION: {outcome['disposition']}")
    if outcome["tools_called"]:
        print("\n🔧 Tools called (these fan out via n8n to OMS / 3PL / WhatsApp / CRM):")
        for t in outcome["tools_called"]:
            print(f"   • {t['tool']}({json.dumps(t['args'], ensure_ascii=False)}) "
                  f"-> {t['result']['downstream']}")
    print("\n📤 Structured outcome returned to n8n:")
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    print("-" * 72)
    return outcome


def main() -> None:
    p = argparse.ArgumentParser(description="Project Sampark RTO voice-agent demo")
    p.add_argument("--scenario", default="cod_prepaid", choices=list(SCENARIOS),
                   help="Which demo scenario to run")
    p.add_argument("--mode", default="auto", choices=["auto", "text", "voice"],
                   help="auto=scripted, text=type responses, voice=live mic")
    p.add_argument("--speak", action="store_true",
                   help="Play the agent's real Sarvam TTS audio (needs key + audio libs)")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    if settings.use_mock and args.mode == "voice":
        print("⚠  Voice mode needs a real SARVAM_API_KEY. Falling back to scripted auto mode.\n")
        args.mode = "auto"

    run(args.scenario, args.mode, args.speak)


if __name__ == "__main__":
    main()
