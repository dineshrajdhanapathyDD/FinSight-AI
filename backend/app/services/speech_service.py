"""Speech services using Amazon Polly and Transcribe, with browser fallback."""

import base64
import json
from typing import Optional
from app.config import get_settings

settings = get_settings()

try:
    import boto3
    polly_client = boto3.client("polly", region_name=settings.aws_region)
    transcribe_client = boto3.client("transcribe", region_name=settings.aws_region)
    AWS_SPEECH_AVAILABLE = True
except Exception:
    AWS_SPEECH_AVAILABLE = False


# Language to Polly voice mapping
VOICE_MAP = {
    "en": "Kajal",      # Indian English neural voice
    "hi": "Kajal",      # Hindi neural voice
    "ta": "Kajal",      # Fallback
    "te": "Kajal",
    "bn": "Kajal",
    "mr": "Kajal",
    "gu": "Kajal",
    "kn": "Kajal",
    "ml": "Kajal",
}

# Language code mapping for Transcribe
TRANSCRIBE_LANG_MAP = {
    "en": "en-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
}


async def text_to_speech(text: str, language: str = "en") -> Optional[str]:
    """Convert text to speech using Amazon Polly. Returns base64 audio."""
    if not AWS_SPEECH_AVAILABLE or not settings.aws_access_key_id:
        # Return None - frontend will use Web Speech API as fallback
        return None

    try:
        voice_id = VOICE_MAP.get(language, "Kajal")
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine="neural",
            LanguageCode=TRANSCRIBE_LANG_MAP.get(language, "en-IN"),
        )
        audio_stream = response["AudioStream"].read()
        return base64.b64encode(audio_stream).decode("utf-8")
    except Exception as e:
        print(f"Polly error: {e}")
        return None


async def speech_to_text(audio_base64: str, language: str = "hi") -> Optional[str]:
    """Convert speech to text. Returns transcribed text."""
    if not AWS_SPEECH_AVAILABLE or not settings.aws_access_key_id:
        # Frontend handles via Web Speech API
        return None

    # For real-time transcription in production, use Transcribe Streaming
    # For MVP demo, frontend uses Web Speech API (browser-native)
    return None
