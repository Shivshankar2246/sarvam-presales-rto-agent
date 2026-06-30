"""Post-call analytics pipeline (OPTIONAL deliverable).

Takes a completed call — either a recorded audio file or a saved call outcome — and
produces structured analytics the ops team can aggregate: confirmed disposition, the
RTO cause / objection, sentiment, whether prepaid was offered/accepted, and an
English one-line summary (so one ops team can read calls across 10 languages).

Pipeline (mirrors Sarvam's Call Analytics cookbook):
    audio --(Saaras batch STT + diarization)--> transcript
    transcript --(sarvam-30b, JSON-structured)--> tags
    tags --> append to outputs/call_analytics.csv  (the ops dashboard feed)

Runs against the real Sarvam client, or fully offline against the mock.

Usage:
    # Analyze a scenario's call end-to-end (offline-friendly):
    python src/analytics/post_call_analytics.py --scenario cod_prepaid

    # Analyze a recorded call (needs SARVAM_API_KEY for batch STT):
    python src/analytics/post_call_analytics.py --audio samples/call.wav --language hi-IN

    # Analyze a saved outcome JSON (e.g. piped from the server):
    python src/analytics/post_call_analytics.py --from-json call_outcome.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # make src/ importable

from agent.rto_agent import RTOAgent  # noqa: E402
from agent.scenarios import SCENARIOS, get_scenario  # noqa: E402
from sarvam_client import get_client  # noqa: E402

ANALYTICS_SYSTEM = (
    "You are a call-quality analyst for a D2C delivery-confirmation team. "
    "TASK=POST_CALL_ANALYTICS. Read the call transcript and return ONLY a JSON object with keys: "
    "disposition (one of CONFIRMED/RESCHEDULED/ADDRESS_FIXED/CONVERTED_PREPAID/CANCELLED/UNREACHABLE/ESCALATED), "
    "rto_cause (short phrase), objection (short phrase or 'none'), sentiment (positive/neutral/negative), "
    "prepaid_offered (true/false), prepaid_accepted (true/false), language (BCP-47 code), "
    "summary_en (one English sentence). Return only the JSON, no prose."
)

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "outputs", "call_analytics.csv",
)


def _transcript_text(transcript: list[dict]) -> str:
    return "\n".join(f"{t['speaker']}: {t['text']}" for t in transcript)


def analyze(client, outcome: dict) -> dict:
    """Run the LLM disposition-tagging step over a call outcome's transcript."""
    transcript = outcome.get("transcript", [])
    messages = [
        {"role": "system", "content": ANALYTICS_SYSTEM},
        {"role": "user", "content": "Call transcript:\n" + _transcript_text(transcript)},
    ]
    resp = client.chat(messages)  # no tools — we want a JSON answer
    content = resp.choices[0].message.content or "{}"
    try:
        tags = json.loads(content)
    except json.JSONDecodeError:
        # tolerate models that wrap JSON in prose/code fences
        start, end = content.find("{"), content.rfind("}")
        tags = json.loads(content[start : end + 1]) if start != -1 else {}
    tags.setdefault("order_id", outcome.get("order_id"))
    return tags


def _write_csv_row(tags: dict) -> None:
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    fields = ["order_id", "disposition", "rto_cause", "objection", "sentiment",
              "prepaid_offered", "prepaid_accepted", "language", "summary_en"]
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if new_file:
            w.writeheader()
        w.writerow(tags)


def _outcome_from_scenario(name: str) -> dict:
    client = get_client()
    sc = get_scenario(name)
    agent = RTOAgent(client, sc["order"])
    agent.greeting()
    for line in sc["customer_lines"]:
        if agent.is_done:
            break
        agent.respond(line)
    return agent.outcome()


def _outcome_from_audio(audio_path: str, language: str) -> dict:
    """Transcribe a recorded call, then treat the whole thing as one speaker block.

    Production note: Sarvam's Batch API returns a diarized transcript (per-speaker
    turns). Here we keep it simple for the PoC and tag the raw transcript.
    """
    client = get_client()
    with open(audio_path, "rb") as f:
        stt = client.transcribe(f.read(), language_code=language)
    return {
        "order_id": os.path.basename(audio_path),
        "transcript": [{"speaker": "call", "text": stt["transcript"]}],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Project Sampark — post-call analytics")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--scenario", choices=list(SCENARIOS), help="Run a scenario and analyze it")
    src.add_argument("--audio", help="Path to a recorded call .wav (batch STT first)")
    src.add_argument("--from-json", dest="from_json", help="Path to a saved call outcome JSON")
    p.add_argument("--language", default="hi-IN", help="Language code (for --audio)")
    args = p.parse_args()

    if args.scenario:
        outcome = _outcome_from_scenario(args.scenario)
    elif args.audio:
        outcome = _outcome_from_audio(args.audio, args.language)
    else:
        with open(args.from_json, encoding="utf-8") as f:
            outcome = json.load(f)

    client = get_client()
    tags = analyze(client, outcome)
    _write_csv_row(tags)

    print("📊 Post-call analytics:")
    print(json.dumps(tags, ensure_ascii=False, indent=2))
    print(f"\n→ Appended to {CSV_PATH} (the ops-dashboard feed)")


if __name__ == "__main__":
    main()
