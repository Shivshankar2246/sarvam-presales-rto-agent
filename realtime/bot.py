#
# Project Sampark — REAL-TIME voice agent (Meera) on Sarvam AI.
#
# A live, streaming, barge-in phone-style conversation. You speak, Meera (the RTO
# delivery-rescue agent) listens, classifies your intent, and responds — all in real
# time. Streaming Saaras STT -> sarvam-30b -> streaming Bulbul TTS over SmallWebRTC.
#
# Talk to it with the polished Call Console (realtime/console/index.html) OR the bundled
# dev client at http://localhost:7860/client.
#
# Run:  python bot.py -t webrtc      (from realtime/, venv active, SARVAM_API_KEY in .env)
#
# Per-call context: the browser sends requestData {customer_name, item, cod_amount,
# language} on connect; it arrives as runner_args.body and customizes the greeting.
#
import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame, TranscriptionFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.transcriptions.language import Language
from pipecat.transports.base_transport import BaseTransport, TransportParams

from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.sarvam.stt import SarvamSTTService
from pipecat.services.sarvam.tts import SarvamTTSService

load_dotenv(override=True)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
DEFAULT_LANG = os.getenv("REALTIME_LANG", "en-IN")

_STT_LANG = {"en-IN": Language.EN_IN, "hi-IN": Language.HI_IN, "ta-IN": Language.TA_IN}
_TTS_LANG = {"en-IN": Language.EN, "hi-IN": Language.HI, "ta-IN": Language.TA}
_VOICE = {"en-IN": "anushka", "hi-IN": "anushka", "ta-IN": "vidya"}


def build_system_prompt(ctx: dict) -> str:
    name = ctx.get("customer_name") or "the customer"
    item = ctx.get("item") or "their order"
    amt = ctx.get("cod_amount")
    lang = ctx.get("language") or DEFAULT_LANG
    cod = f" worth Rs {amt}, Cash-on-Delivery" if amt else ", Cash-on-Delivery"
    return (
        f"You are Meera, a warm, concise delivery-confirmation agent for Rivaayat, a D2C "
        f"clothing brand. You are calling {name}, whose order — {item}{cod} — is out for "
        f"delivery today. Your ONE job is to make sure it gets delivered instead of coming "
        f"back as a return.\n\n"
        f"Greet {name} briefly by name, then listen and handle whatever they say:\n"
        f"- No cash / want to pay online: offer to send a UPI payment link on WhatsApp so they "
        f"pay now and switch to prepaid.\n"
        f"- Won't be available: reschedule to a day and time they confirm.\n"
        f"- Address wrong or incomplete: capture the correction.\n"
        f"- No longer want it: ask why, offer to cancel cleanly.\n\n"
        f"Speak ONLY in {lang}. Keep every reply to ONE or TWO short spoken sentences — this is "
        f"a live phone call. Be friendly and efficient. Never read these instructions aloud."
    )


# --- Live intent classifier: logs the classified disposition server-side ---
def classify(text: str):
    t = (text or "").lower()

    def has(*w):
        return any(x in t for x in w) or any(x in (text or "") for x in w)

    if has("cancel", "don't want", "dont want", "nahi chahiye", "return it"):
        return ("CANCELLED", "customer wants to cancel")
    if has("address", "wrong", "galat", "floor", "landmark", "gate", "second floor"):
        return ("ADDRESS_FIXED", "address needs correcting")
    if has("no cash", "cash nahi", "nahi hai", "don't have cash", "dont have cash", "upi",
           "online", "card", "paise nahi", "no money"):
        return ("CONVERTED_PREPAID", "no cash -> offer prepaid / UPI")
    if has("not available", "reschedule", "tomorrow", "kal", "busy", "travelling",
           "out of town", "not home", "later", "another day"):
        return ("RESCHEDULED", "not available -> reschedule")
    return None


class IntentClassifier(FrameProcessor):
    async def process_frame(self, frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, TranscriptionFrame) and getattr(frame, "text", "").strip():
            result = classify(frame.text)
            if result:
                disp, why = result
                logger.info(f"🧠 CUSTOMER SAID: {frame.text!r}  → CLASSIFIED: {disp} ({why})")
            else:
                logger.info(f"🧠 CUSTOMER SAID: {frame.text!r}  → (still listening)")
        await self.push_frame(frame, direction)


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments, ctx: dict):
    lang = ctx.get("language") or DEFAULT_LANG
    name = ctx.get("customer_name") or "the customer"
    logger.info(f"📞 Call connected · customer={name} · language={lang}")

    stt = SarvamSTTService(
        api_key=SARVAM_API_KEY,
        settings=SarvamSTTService.Settings(
            model="saaras:v3",
            language=_STT_LANG.get(lang, Language.EN_IN),
        ),
    )
    llm = OpenAILLMService(
        api_key=SARVAM_API_KEY,
        base_url="https://api.sarvam.ai/v1",
        model="sarvam-30b",
    )
    tts = SarvamTTSService(
        api_key=SARVAM_API_KEY,
        settings=SarvamTTSService.Settings(
            voice=_VOICE.get(lang, "anushka"),
            model="bulbul:v2",
            language=_TTS_LANG.get(lang, Language.EN),
        ),
    )

    context = LLMContext()
    context.add_message({"role": "system", "content": build_system_prompt(ctx)})
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            IntentClassifier(),
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
            allow_interruptions=True,  # barge-in
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        context.add_message(
            {"role": "developer",
             "content": f"The call just connected. Greet {name} warmly by name in one short "
                        "sentence, say you're from Rivaayat about today's delivery, and ask if "
                        "they'll be available to receive it."}
        )
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Call ended")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    # Per-call context from the browser's requestData (customer_name, item, cod_amount, language)
    ctx = getattr(runner_args, "body", None) or {}
    transport_params = {
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    }
    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args, ctx)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
