"""Sample order contexts + scripted customer lines for the three demo scenarios.

Used by run_demo.py --auto to replay a believable conversation with no human input,
and by server.py as example trigger payloads. Mock order data is fine — the flow is
the deliverable.
"""
from __future__ import annotations

SCENARIOS: dict[str, dict] = {
    # 1) COD -> prepaid conversion (the money shot) — Hindi
    "cod_prepaid": {
        "order": {
            "order_id": "RVT-48217",
            "customer_name": "Rakesh Kumar",
            "language_code": "hi-IN",
            "language_name": "Hindi",
            "item": "Men's Kurta Set (Blue, L)",
            "cod_amount": 1450,
            "address": "H.No 14, Indira Nagar, Lucknow, UP 226016",
            "status": "OUT_FOR_DELIVERY",
        },
        "customer_lines": [
            "हाँ रहूँगा घर पे, लेकिन अभी मेरे पास कैश नहीं है।",
            "हाँ भेज दो UPI लिंक, मैं अभी पे कर देता हूँ।",
        ],
    },
    # 2) Not available -> reschedule — Tamil
    "reschedule": {
        "order": {
            "order_id": "RVT-50934",
            "customer_name": "Lakshmi Narayanan",
            "language_code": "ta-IN",
            "language_name": "Tamil",
            "item": "Silk Saree (Maroon)",
            "cod_amount": 2890,
            "address": "12, Gandhi Street, T. Nagar, Chennai, TN 600017",
            "status": "OUT_FOR_DELIVERY",
        },
        "customer_lines": [
            "இல்லை, நான் இன்னைக்கு ஊருக்கு போயிட்டேன். நாளைக்குதான் வருவேன்.",
            "சரி, நாளைக்கு மதியம் ஓகே.",
        ],
    },
    # 3) Wrong/incomplete address -> correction — Hinglish (code-mix)
    "address": {
        "order": {
            "order_id": "RVT-51120",
            "customer_name": "Priya Sharma",
            "language_code": "hi-IN",
            "language_name": "Hindi/Hinglish",
            "item": "Anarkali Dress (Green, M)",
            "cod_amount": 1799,
            "address": "Flat 2, Sunshine Apartments, Pune, MH 411014",
            "status": "NDR_ATTEMPT_FAILED",
        },
        "customer_lines": [
            "Haan, ground floor likha hai but actually second floor hai, blue gate ke saamne.",
            "Haan bilkul, aaj hi bhej do please.",
        ],
    },
}


def get_scenario(name: str) -> dict:
    if name not in SCENARIOS:
        raise KeyError(f"Unknown scenario '{name}'. Choose from: {', '.join(SCENARIOS)}")
    return SCENARIOS[name]
