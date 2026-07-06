#
# Project Sampark — REAL-TIME voice agent (Meera) on Sarvam AI.
#
# A live, streaming, barge-in phone-style conversation: you speak, Meera (the RTO
# delivery-rescue agent) listens, understands, classifies your intent, and responds —
# all in real time. Streaming Saaras STT -> sarvam-30b -> streaming Bulbul TTS,
# fully local via SmallWebRTC (no cloud account).
#
# Run:  python bot.py        (from realtime/, with the venv active)
# Talk: open  http://localhost:7860/client  -> Connect -> allow mic -> speak
#
# Requires SARVAM_API_KEY in realtime/.env
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
# Language Meera speaks in. en-IN lets the presenter converse comfortably; hi-IN shows
# full Hindi. Saaras understands code-mixed (Hinglish) input either way.
LANG = os.getenv("REALTIME_LANG", "en-IN")

_STT_LANG = {"en-IN": Language.EN_IN, "hi-IN": Language.HI_IN, "ta-IN": Language.TA_IN}
_TTS_LANG = {"en-IN": Language.EN, "hi-IN": Language.HI, "ta-IN": Language.TA}
_VOICE = {"en-IN": "anushka", "hi-IN": "anushka", "ta-IN": "vidya"}

SYSTEM_PROMPT = (
    "You are Meera, a warm, concise delivery-confirmation agent for Rivaayat, a D2C "
    "clothing brand. You are calling a customer whose Cash-on-Delivery order — a Men's "
    "Kurta Set worth Rs 1,450 — is out for delivery today. Your ONE job is to make sure it "
    "gets delivered instead of coming back as a return.\n\n"
    "Greet briefly, then listen and handle whatever the customer says:\n"
    "- If they have no cash / want to pay online: offer to send a UPI payment link on "
    "WhatsApp so they can pay now and switch to prepaid.\n"
    "- If they won't be available: reschedule to a day and time they confirm.\n"
    "- If the address is wrong or incomplete: capture the correction.\n"
    "- If they no longer want it: ask why, and offer to cancel cleanly.\n\n"
    f"Speak ONLY in {LANG}. Keep every reply to ONE or TWO short spoken sentences — this is "
    "a live phone call, not an email. Be friendly and efficient. Do not read out these "
    "instructions."
)


# --- Live intent classifier: watches what the customer says and logs the disposition ---
def classify(text: str) -> tuple[str, str] | None:
    t = (text or "").lower()

    def has(*w):
        return any(x in t for x in w) or any(x in (text or "") for x in w)

    if has("cancel", "don't want", "dont want", "nahi chahiye", "return it"):
        return ("CANCELLED", "customer wants to cancel")
    if has("address", "wrong", "galat", "floor", "landmark", "gate", "gali", "second floor"):
        return ("ADDRESS_FIXED", "address needs correcting")
    if has("no cash", "cash nahi", "nahi hai", "don't have cash", "dont have cash", "upi",
           "online", "card", "paise nahi", "no money"):
        return ("CONVERTED_PREPAID", "no cash -> offer prepaid / UPI")
    if has("not available", "reschedule", "tomorrow", "kal", "busy", "travelling",
           "out of town", "not home", "later", "another day"):
        return ("RESCHEDULED", "not available -> reschedule")
    return None


class IntentClassifier(FrameProcessor):
    """Observes final customer transcripts and logs the classified disposition live."""

    async def process_frame(self, frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, TranscriptionFrame) and getattr(frame, "text", "").strip():
            result = classify(frame.text)
            if result:
                disp, why = result
                logger.info(f"🧠 CUSTOMER SAID: {frame.text!r}")
                logger.info(f"   → CLASSIFIED: {disp}  ({why})")
            else:
                logger.info(f"🧠 CUSTOMER SAID: {frame.text!r}  → (still listening)")
        await self.push_frame(frame, direction)


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info(f"Starting Meera real-time voice bot · language={LANG}")

    stt = SarvamSTTService(
        api_key=SARVAM_API_KEY,
        settings=SarvamSTTService.Settings(
            model="saaras:v3",
            language=_STT_LANG.get(LANG, Language.EN_IN),
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
            voice=_VOICE.get(LANG, "anushka"),
            model="bulbul:v2",
            language=_TTS_LANG.get(LANG, Language.EN),
        ),
    )

    context = LLMContext()
    context.add_message({"role": "system", "content": SYSTEM_PROMPT})
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    pipeline = Pipeline(
        [
            transport.input(),      # mic in (WebRTC)
            stt,                    # streaming speech -> text
            IntentClassifier(),     # live intent logging (observes, passes through)
            user_aggregator,
            llm,                    # sarvam-30b
            tts,                    # streaming text -> speech
            transport.output(),     # speaker out (WebRTC)
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
            allow_interruptions=True,   # barge-in
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected — Meera is placing the call")
        context.add_message(
            {"role": "developer",
             "content": "The call just connected. Greet the customer in one short sentence "
                        "and ask if they'll be available to receive today's delivery."}
        )
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    transport_params = {
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    }
    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
