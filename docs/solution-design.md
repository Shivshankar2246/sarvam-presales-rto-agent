# Project Sampark — Solution Design

> Internal design spec. Drives `/src`, the n8n workflow, and the business write-up.
> **Sampark** (संपर्क) = "contact / to connect." The agent reconnects the brand with the
> customer in the 30-minute window before a delivery fails.

---

## 1. The customer (pre-sales scenario)

**"Zivaa"** — a fast-growing D2C ethnic-wear brand (fictional, representative of a real segment).

| Attribute | Value |
|---|---|
| Orders / month | ~1,20,000 (growing ~8% MoM) |
| COD share | 64% → **~76,800 COD orders/month** |
| COD RTO (apparel) | **~30%** → ~23,000 RTOs/month |
| Avg order value | ₹1,450 |
| Fulfilment | 3PL — Delhivery, Shadowfax, Ekart |
| Current NDR process | In-house 12-seat tele-calling team. Reaches ~40% of customers. ~80 calls/agent/day. English/Hindi only. 10am–7pm. |
| Buyer | VP Operations / Head of Supply Chain (economic buyer), CX Lead (champion) |

**The bleed:** ~23,000 COD orders RTO every month. At a conservative **₹200 per RTO**
(logistics-only — forward + reverse freight, packaging, handling; all-in is ₹400+), that is
**~₹46 lakh/month — ~₹5.5 cr/year** evaporating (₹11 cr+ at all-in cost). The tele-calling team
only touches 40% of at-risk orders, in 2 languages, during business hours. The other 60% —
disproportionately Tier 2/3, regional-language, COD buyers — go uncontacted and RTO at the
highest rates.

> This is the wedge: **the customers who RTO the most are exactly the ones the current process
> cannot reach** — because of language, call capacity, and timing.

---

## 2. What we built

An **outbound, event-triggered, multilingual voice agent** that calls the customer in their own
language the moment an order is at RTO risk ("Out for Delivery" or after a failed attempt /
NDR), confirms the four things that cause RTO, and writes the resolution back into the brand's
systems automatically.

**The four RTO causes Sampark resolves on the call:**
1. **Not available** at delivery time → reschedule to a slot the customer confirms.
2. **Wrong / incomplete address** → capture the correction + a landmark.
3. **COD not ready / hesitant** (no cash, or would rather pay online) → **lock the order as prepaid** with a sweetener (free shipping, ships today) + a UPI link on WhatsApp — the single biggest RTO killer, because a paid order removes the free-cancel option — or confirm cash will be ready.
4. **Changed mind / duplicate / "ordered by mistake"** → capture reason, cancel cleanly (saves the freight instead of shipping a guaranteed return).

It is an **A+B** system:
- **A — Voice bot:** Sarvam **STT (Saaras `saaras:v3`)** → **LLM (`sarvam-30b`, OpenAI-compatible tool-calling)** → **TTS (Bulbul `bulbul:v3`)**, fully in the customer's language, code-mixing aware (Hinglish/Tanglish).
- **B — Agentic backend (n8n):** on the structured call outcome, fans out downstream — update OMS, instruct the 3PL (reschedule/hold/cancel), log to CRM, and escalate ambiguous calls to a human. The disposition reaches n8n **two ways**: the **batch** workflow (`sampark-trigger`) where n8n places the call itself, and the **live** workflow (`sampark-live-resolve`) where the real-time Call Console POSTs the captured outcome mid-call — the A+B path, verified end-to-end.

---

## 3. End-to-end agentic sequence (the "event → reason → tool → downstream" flow)

```
[1] TRIGGER          OMS / 3PL webhook → n8n:  order_id, status = OUT_FOR_DELIVERY | NDR_ATTEMPT_FAILED
        │
[2] ENRICH           n8n pulls order context (DB/OMS): name, language_pref, phone,
        │            address, COD amount, SKU, attempt #, courier
        │
[3] DIAL             n8n → Voice Service (FastAPI): place outbound call (telephony: Plivo/Exotel — mockable)
        │
[4] CONVERSE         Voice loop, in customer's language:
        │              Saaras STT  →  sarvam-30b (system goal + tools)  →  Bulbul TTS
        │            Agent reasons over the 4 RTO causes, calls tools as needed:
        │              • reschedule_delivery(order_id, slot)
        │              • update_address(order_id, corrected, landmark)
        │              • convert_to_prepaid(order_id)        → returns UPI link, sent on WhatsApp
        │              • cancel_order(order_id, reason)
        │              • escalate_to_human(order_id, reason) | schedule_callback(order_id, time)
        │
[5] OUTCOME          Voice Service → n8n: structured disposition JSON
        │              { intent, disposition, new_slot?, corrected_address?, prepaid_converted?, transcript, language }
        │
[6] FAN-OUT          n8n downstream (conditional):
        │              • Update OMS order (slot / address / status / prepaid flag)
        │              • Notify 3PL: reschedule | hold | cancel (saves a doomed dispatch)
        │              • Append row to CRM / Google Sheet (ops dashboard)
        │              • If ambiguous/angry/high-value → human queue (Slack/CRM task)
        │
[7] ANALYTICS        Call audio + transcript → post-call analytics (optional):
                       batch STT + diarization + LLM disposition tagging (Sarvam Call Analytics)
```

Mock data is fine for the PoC — the **flow** is the deliverable: an event fires, the agent
reasons in-language, a tool executes, and a downstream system is updated.

> **Live variant (the A+B path, verified).** Steps [1]–[3] above are the *batch* mode where n8n
> places the call. In the **live** mode, the real-time Call Console *is* the call: the moment Meera
> captures the outcome, the browser POSTs `{ order_id, disposition, captured }` to
> `n8n /sampark-live-resolve`, which jumps straight to **[6] FAN-OUT** — no dial-out, no second call.
> Same downstream, driven by the live conversation. This is what fuses A and B into one system.

---

## 4. Agent contract — system goal + tools

**System goal (`sarvam-30b`):** "You are Meera, calling on behalf of Zivaa about the customer's
order that is out for delivery. Speak ONLY in the customer's language. Your single job is to make
this delivery succeed. In order: confirm they'll be available; confirm the address; confirm they
have the COD amount ready OR offer to switch to UPI prepaid; if they want to cancel, capture why.
Be warm, brief, and respectful. Never invent order details — use the provided context. Call a tool
the moment a resolution is decided. Keep turns short — this is a phone call."

**Tools (function-calling schema):**

| Tool | Args | Effect (downstream via n8n) |
|---|---|---|
| `reschedule_delivery` | `order_id, preferred_slot` | OMS slot update + 3PL reschedule |
| `update_address` | `order_id, corrected_address, landmark` | OMS address update + 3PL re-route |
| `convert_to_prepaid` | `order_id` | Send UPI payment link (free-shipping sweetener), flag prepaid in OMS |
| `cancel_order` | `order_id, reason` | OMS cancel + 3PL hold (avoid the doomed dispatch) |
| `schedule_callback` | `order_id, callback_time` | Re-queue the call |
| `escalate_to_human` | `order_id, reason` | Create human task (Slack/CRM) |

The disposition returned to n8n is always one of:
`CONFIRMED · RESCHEDULED · ADDRESS_FIXED · CONVERTED_PREPAID · CANCELLED · UNREACHABLE · ESCALATED`.

---

## 5. Multilingual conversation scripts (for the demo)

Three languages to satisfy "2+ Indian languages" and the **code-mixing plus**. Each maps to a
different RTO cause so the demo shows range.

### 5a. Hindi — COD-ready → prepaid conversion (the money shot)
```
Meera (TTS hi-IN): नमस्ते, मैं ज़िवा से मीरा बोल रही हूँ। आपका ऑर्डर आज डिलीवरी के लिए निकला है —
                   ₹1,450 कैश ऑन डिलीवरी। क्या आप घर पर रहेंगे?
Customer (STT):    हाँ रहूँगा, लेकिन अभी कैश नहीं है घर पे।
Meera:             कोई बात नहीं! मैं आपके लिए फ्री शिपिंग लगा देती हूँ और अभी एक UPI लिंक WhatsApp पर
                   भेज देती हूँ — GPay या PhonePe से ₹1,450 दे दीजिए, ऑर्डर आज ही निकल जाएगा। भेज दूँ?
Customer:          हाँ भेज दो।
   → TOOL: convert_to_prepaid(order_id)         disposition = CONVERTED_PREPAID
```

### 5b. Tamil — not available → reschedule
```
Meera (TTS ta-IN): வணக்கம், நான் ஜிவா-ல் இருந்து மீரா பேசுறேன். உங்க ஆர்டர் இன்னைக்கு டெலிவரிக்கு
                   வந்துருக்கு. நீங்க வீட்ல இருப்பீங்களா?
Customer (STT):    இல்லை, நான் இன்னைக்கு ஊருக்கு போயிட்டேன். நாளைக்கு வரேன்.
Meera:             பரவாயில்லை! நாளைக்கு மதியம் டெலிவரி பண்ணட்டுமா?
Customer:          சரி, நாளைக்கு மதியம் ஓகே.
   → TOOL: reschedule_delivery(order_id, "tomorrow 12–3pm")   disposition = RESCHEDULED
```

### 5c. Hinglish (code-mix) — wrong address → correction
```
Meera (TTS, Hinglish): Hello, main Zivaa se Meera bol rahi hoon. Aapka order out for delivery
                       hai, but courier bol raha hai address mein gali ka naam missing hai. Aap
                       confirm kar denge?
Customer (STT):        Haan, ground floor likha hai but actually second floor hai, aur landmark
                       hai blue gate ke saamne.
Meera:                 Perfect, main update kar deti hoon — second floor, blue gate ke saamne.
                       Delivery aaj hi ho jayegi.
   → TOOL: update_address(order_id, "...2nd floor", "opp. blue gate")   disposition = ADDRESS_FIXED
```

These three are the spine of the 3–5 min demo video.

---

## 6. Why Sarvam (the pre-sales argument, in one place)

| Capability | Why it's load-bearing here | Generic alternative fails because |
|---|---|---|
| 22 Indian languages, regional STT/TTS | The high-RTO customer is a Tier 2/3 COD buyer who answers a Tamil/Bhojpuri call, ignores an English SMS | OpenAI/ElevenLabs lack production-grade Indian-language + accent coverage |
| Code-mixing (Hinglish/Tanglish) | Real Indian phone speech is mixed; the agent must understand "cash nahi hai" + "blue gate ke saamne" | Generic STT mis-transcribes code-switched speech |
| Low latency | It's a live phone call — >1s lag and the customer hangs up | Routing audio to US-hosted models adds latency |
| On-prem / data sovereignty | Names, addresses, phone, COD amounts = PII; BFSI/large brands need India-resident data | US APIs raise DPDP / data-residency flags |
| Indian-context LLM (`sarvam-30b`) | Understands "ghar pe nahi rahunga," UPI, COD norms natively | Generic LLM needs heavy prompting for Indian commerce context |

---

## 7. Scope of the PoC vs production (for the write-up's "Limitations" section)

**In the PoC:** the full A+B flow runs end-to-end on mock order data — in-language voice
conversation (real Sarvam STT/LLM/TTS) → captured disposition → n8n downstream update (OMS/3PL/CRM).
The voice bot ships in **two forms**: a turn-based service (`src/`, drives the dashboard + the batch
n8n pipeline) and a **real-time streaming, barge-in call** (`realtime/`, Pipecat + Sarvam over
WebRTC) you can actually talk to — and it's this **live call that drives n8n** (`sampark-live-resolve`),
verified end-to-end with a live Tamil call. Telephony is mockable or wired to Plivo/Exotel.

**For production (90-day rollout):** real telephony at scale + concurrency, OMS/3PL API
integrations (Unicommerce/Increff + Delhivery/Shadowfax), DPDP-compliant consent + DND handling,
retry/voicemail logic, human-handoff warm transfer, A/B against the human team, and the post-call
analytics loop feeding disposition models.
