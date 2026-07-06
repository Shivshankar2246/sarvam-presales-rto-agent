"""Project Sampark — Delivery Rescue Console (Streamlit).

A business-facing demo UI for non-technical viewers (COO / VP Ops / CEO). No terminal,
no code. You click "Call now" on an at-risk order; the AI voice agent (real Sarvam:
Saaras + sarvam-30b + Bulbul) has the conversation in the customer's language, you HEAR
it, and the resolution + the systems it updated appear as plain-English cards.

Run:  streamlit run src/dashboard.py     (needs SARVAM_API_KEY in .env for live audio)
"""
from __future__ import annotations

import base64
import io
import os
import sys
import time
import wave

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.rto_agent import RTOAgent  # noqa: E402
from agent.scenarios import SCENARIOS  # noqa: E402
from config import settings, speaker_for  # noqa: E402
from sarvam_client import get_client  # noqa: E402

CUSTOMER_SPEAKER = "aditya"  # male v3 voice for the simulated customer side

st.set_page_config(page_title="Sampark — Delivery Rescue Console", page_icon="📦", layout="wide")

# ----------------------------- styling -----------------------------
st.markdown(
    """
    <style>
      .stApp { background: #f5f7fb; }
      #MainMenu, footer, header { visibility: hidden; }
      .block-container { padding-top: 1.6rem; max-width: 1150px; }
      .hero { background: linear-gradient(100deg,#4f46e5,#0ea5e9); color:#fff;
              border-radius:18px; padding:22px 28px; margin-bottom:14px; }
      .hero h1 { margin:0; font-size:1.7rem; font-weight:800; letter-spacing:-.5px; }
      .hero p  { margin:.35rem 0 0; opacity:.92; font-size:.98rem; }
      .hero .pw { margin-top:.5rem; font-size:.78rem; opacity:.8; letter-spacing:.3px; }
      .kpi { background:#fff; border-radius:14px; padding:16px 18px; height:100%;
             box-shadow:0 1px 3px rgba(16,24,40,.08); border:1px solid #eef1f6; }
      .kpi .l { font-size:.74rem; color:#667085; text-transform:uppercase; letter-spacing:.5px; font-weight:600; }
      .kpi .v { font-size:1.7rem; font-weight:800; color:#101828; margin-top:2px; }
      .kpi .v.small { font-size:1.25rem; }
      /* order cards live inside st.container(border=True); these style the text within */
      .nm { font-weight:700; color:#101828; font-size:1.12rem; line-height:1.3; margin-bottom:7px; }
      .badges { margin-bottom:9px; }
      .meta { color:#475467; font-size:.9rem; line-height:1.5; margin-bottom:7px; }
      .whyflag { color:#98a2b3; font-size:.8rem; line-height:1.4; margin-bottom:12px; }
      .whyflag b { color:#667085; font-weight:600; }
      .badge { display:inline-block; padding:4px 11px; border-radius:999px; font-size:.73rem;
               font-weight:700; margin-right:7px; }
      .b-lang { background:#eef2ff; color:#4f46e5; }
      .b-risk { background:#fef3f2; color:#d92d20; }
      /* give the bordered order containers more room + separation */
      div[data-testid="stVerticalBlockBorderWrapper"] { margin-bottom:12px; }
      div[data-testid="stVerticalBlockBorderWrapper"] > div { padding:4px 4px 0; }
      .convo { background:#fff; border:1px solid #eef1f6; border-radius:16px; padding:18px 18px 8px;
               box-shadow:0 1px 3px rgba(16,24,40,.06); min-height:120px; }
      .row { display:flex; margin:10px 0; align-items:flex-end; }
      .row.agent { justify-content:flex-start; }
      .row.cust  { justify-content:flex-end; }
      .bub { max-width:74%; padding:10px 14px; border-radius:16px; font-size:.98rem; line-height:1.45; }
      .bub.agent { background:#eef2ff; color:#1e1b4b; border-bottom-left-radius:4px; }
      .bub.cust  { background:#101828; color:#fff; border-bottom-right-radius:4px; }
      .who { font-size:.72rem; font-weight:700; opacity:.7; margin-bottom:2px; }
      .av { width:34px; height:34px; border-radius:50%; display:flex; align-items:center;
            justify-content:center; font-size:1.1rem; margin:0 8px; flex:0 0 34px;
            background:#e0e7ff; }
      .live { color:#d92d20; font-weight:800; font-size:.8rem; }
      .live .dot { height:9px; width:9px; background:#d92d20; border-radius:50%;
                   display:inline-block; margin-right:5px; animation:pulse 1s infinite; }
      @keyframes pulse { 0%{opacity:1} 50%{opacity:.3} 100%{opacity:1} }
      .result { background:#ecfdf3; border:1px solid #abefc6; border-radius:16px; padding:18px 22px; margin-top:14px; }
      .result .t { font-size:1.25rem; font-weight:800; color:#027a48; }
      .result .s { color:#054f31; margin-top:4px; font-size:.96rem; }
      .act { background:#fff; border:1px solid #eef1f6; border-radius:12px; padding:12px 14px;
             box-shadow:0 1px 2px rgba(16,24,40,.05); }
      .act .h { font-weight:700; color:#101828; font-size:.9rem; }
      .act .d { color:#667085; font-size:.82rem; margin-top:2px; }
      .act .ok { color:#12b76a; font-weight:800; font-size:.8rem; }
      div.stButton > button { background:#4f46e5; color:#fff; border:0; border-radius:10px;
             font-weight:700; padding:.45rem 0; width:100%; }
      div.stButton > button:hover { background:#4338ca; color:#fff; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- helpers -----------------------------
OUTCOME = {
    "CONVERTED_PREPAID": {
        "emoji": "💳", "title": "Converted to Prepaid",
        "sub": "Customer paid by UPI on the call — this order's return risk just dropped from ~30% to under 2%.",
        "actions": [("🏬", "Order system", "Marked as prepaid"),
                    ("💬", "WhatsApp", "UPI payment link sent"),
                    ("📋", "CRM", "Outcome logged")],
    },
    "RESCHEDULED": {
        "emoji": "🗓️", "title": "Delivery Rescheduled",
        "sub": "Customer confirmed a new slot — the courier won't waste a failed attempt.",
        "actions": [("🚚", "Courier partner", "Rescheduled to confirmed slot"),
                    ("💬", "WhatsApp", "New slot confirmed"),
                    ("📋", "CRM", "Outcome logged")],
    },
    "ADDRESS_FIXED": {
        "emoji": "📍", "title": "Address Corrected",
        "sub": "The delivery address was fixed on the call — the parcel now reaches the right door today.",
        "actions": [("🏬", "Order system", "Address updated"),
                    ("🚚", "Courier partner", "Re-routed for today"),
                    ("📋", "CRM", "Outcome logged")],
    },
    "CANCELLED": {
        "emoji": "🛑", "title": "Cancelled Cleanly",
        "sub": "Customer no longer wanted it — cancelling now saves the freight on a guaranteed return.",
        "actions": [("🏬", "Order system", "Order cancelled"),
                    ("🚚", "Courier partner", "Dispatch held"),
                    ("📋", "CRM", "Reason logged")],
    },
}
DEFAULT_OUTCOME = {
    "emoji": "🙋", "title": "Escalated to a Human",
    "sub": "An edge case the agent flagged for a person — nothing falls through the cracks.",
    "actions": [("👤", "Support queue", "Assigned to an agent"), ("📋", "CRM", "Outcome logged")],
}
SAVE_DISPOSITIONS = {"CONVERTED_PREPAID", "RESCHEDULED", "ADDRESS_FIXED", "CANCELLED"}

# Why each order was flagged high-RTO-risk (illustrative signals a risk engine would score).
RISK_WHY = {
    "cod_prepaid": "COD payment · first-time buyer · Tier-2 pincode",
    "reschedule": "COD payment · high-value order · 4-day transit",
    "address": "COD payment · address flagged incomplete",
}


def wav_seconds(b: bytes) -> float:
    try:
        with wave.open(io.BytesIO(b)) as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return 1.4


def audio_tag(b: bytes) -> str:
    if not b:
        return ""
    b64 = base64.b64encode(b).decode()
    return f'<audio autoplay><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>'


def bubble(speaker: str, text: str) -> str:
    if speaker == "agent":
        return (f'<div class="row agent"><div class="av">👩🏻‍💼</div>'
                f'<div class="bub agent"><div class="who">Meera · Sampark AI</div>{text}</div></div>')
    return (f'<div class="row cust"><div class="bub cust"><div class="who">Customer</div>{text}</div>'
            f'<div class="av">🧑🏽</div></div>')


def run_call(scenario_key: str) -> dict:
    """Run the real agent for a scenario and synthesize per-line audio."""
    client = get_client()
    sc = SCENARIOS[scenario_key]
    order = sc["order"]
    lang = order["language_code"]

    agent = RTOAgent(client, order)
    agent.greeting()
    for line in sc["customer_lines"]:
        if agent.is_done:
            break
        agent.respond(line)
    if not agent.is_done:
        agent.finalize()

    turns = []
    for speaker, text in agent.transcript:
        voice = speaker_for(lang) if speaker == "agent" else CUSTOMER_SPEAKER
        try:
            audio = client.synthesize(text, lang, speaker=voice)
        except Exception:
            audio = b""
        turns.append((speaker, text, audio))

    return {"order": order, "turns": turns, "disposition": agent.disposition, "tools": agent.tool_log}


def render_result(res: dict) -> None:
    o = OUTCOME.get(res["disposition"], DEFAULT_OUTCOME)
    st.markdown(
        f'<div class="result"><div class="t">{o["emoji"]} {o["title"]}</div>'
        f'<div class="s">{o["sub"]}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-weight:700;color:#344054;font-size:.82rem;'
                'text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">'
                'Systems updated automatically — no human touched a thing</div>',
                unsafe_allow_html=True)
    cols = st.columns(len(o["actions"]))
    for col, (emoji, head, detail) in zip(cols, o["actions"]):
        col.markdown(
            f'<div class="act"><div class="h">{emoji} {head}</div>'
            f'<div class="d">{detail}</div><div class="ok">✔ done</div></div>',
            unsafe_allow_html=True,
        )


# ----------------------------- state -----------------------------
if "handled" not in st.session_state:
    st.session_state.handled = 0
    st.session_state.saved = 0
    st.session_state.last = None
    st.session_state.animate = False

# ----------------------------- header + KPIs -----------------------------
backend = "Live · Sarvam AI" if not settings.use_mock else "Demo mode (add SARVAM_API_KEY for live voice)"
st.markdown(
    f'<div class="hero"><h1>📦 Rivaayat · Delivery Rescue Console</h1>'
    f'<p>An AI voice agent that calls Cash-on-Delivery customers in their own language and '
    f'saves the order before it turns into a costly return.</p>'
    f'<div class="pw">Powered by Sampark on Sarvam AI · Speech (Saaras) · Reasoning (sarvam-30b) · Voice (Bulbul) — {backend}</div></div>',
    unsafe_allow_html=True,
)

k = st.columns(4)
kpis = [
    ("COD orders at risk today", "342", False),
    ("Rescued this session", str(st.session_state.saved), False),
    ("Return risk on rescued orders", "30% → <2%", True),
    ("Projected annual recovery", "₹5.5 Cr", False),
]
for col, (label, val, small) in zip(k, kpis):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div>'
                 f'<div class="v {"small" if small else ""}">{val}</div></div>', unsafe_allow_html=True)

st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

# ----------------------------- layout -----------------------------
left, right = st.columns([1, 1.5], gap="large")

with left:
    st.markdown('<div style="font-weight:800;font-size:1.05rem;color:#101828;margin-bottom:8px">'
                '🚨 Orders at risk</div>', unsafe_allow_html=True)
    triggered = None
    for key, sc in SCENARIOS.items():
        o = sc["order"]
        parts = [p.strip() for p in o["address"].split(",")]
        city = parts[-2] if len(parts) >= 2 else parts[-1]
        with st.container(border=True):
            st.markdown(
                f'<div class="nm">{o["customer_name"]}</div>'
                f'<div class="badges"><span class="badge b-lang">{o["language_name"]}</span>'
                f'<span class="badge b-risk">⚠ RTO risk</span></div>'
                f'<div class="meta">{o["item"]}<br>₹{o["cod_amount"]} Cash-on-Delivery · {city}</div>'
                f'<div class="whyflag"><b>Why flagged:</b> {RISK_WHY.get(key, "COD order")}</div>',
                unsafe_allow_html=True,
            )
            if st.button(f"📞 Call {o['customer_name'].split()[0]} now",
                         key=f"btn_{key}", use_container_width=True):
                triggered = key

with right:
    st.markdown('<div style="font-weight:800;font-size:1.05rem;color:#101828;margin-bottom:8px">'
                '📞 Live call</div>', unsafe_allow_html=True)
    stage = st.container()

# ----------------------------- run / render -----------------------------
if triggered:
    with right:
        with st.spinner("Connecting… Meera is placing the call"):
            res = run_call(triggered)
    st.session_state.last = res
    st.session_state.animate = True
    st.session_state.handled += 1
    if res["disposition"] in SAVE_DISPOSITIONS:
        st.session_state.saved += 1
    st.rerun()

res = st.session_state.last
if res:
    with stage:
        convo = st.empty()
        if st.session_state.animate:
            past = ""
            n = len(res["turns"])
            for i, (speaker, text, audio) in enumerate(res["turns"]):
                live = '<div class="live"><span class="dot"></span>LIVE CALL</div>' if i < n else ""
                convo.markdown(f'<div class="convo">{live}{past}{bubble(speaker, text)}{audio_tag(audio)}</div>',
                               unsafe_allow_html=True)
                time.sleep(min(wav_seconds(audio) + 0.35, 9) if audio else 1.3)
                past += bubble(speaker, text)
            convo.markdown(f'<div class="convo">{past}</div>', unsafe_allow_html=True)
            st.session_state.animate = False
        else:
            past = "".join(bubble(s, t) for s, t, _ in res["turns"])
            convo.markdown(f'<div class="convo">{past}</div>', unsafe_allow_html=True)
        render_result(res)
else:
    with stage:
        st.markdown('<div class="convo" style="color:#98a2b3">Pick an at-risk order on the left and '
                    'press <b>Call now</b> to watch Sampark rescue it — live, in the customer\'s language.</div>',
                    unsafe_allow_html=True)
