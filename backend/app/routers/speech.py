from fastapi import APIRouter
from app.models.schemas import SpeechToTextRequest, TextToSpeechRequest
from app.services.speech_service import text_to_speech, speech_to_text

router = APIRouter()


@router.post("/tts")
async def convert_text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech audio."""
    audio_base64 = await text_to_speech(request.text, request.language.value)
    
    if audio_base64:
        return {
            "status": "success",
            "audio_base64": audio_base64,
            "format": "mp3",
            "engine": "aws_polly",
        }
    else:
        return {
            "status": "fallback",
            "message": "Use browser Web Speech API for TTS",
            "text": request.text,
            "language": request.language.value,
            "engine": "browser_webspeech",
        }


@router.post("/stt")
async def convert_speech_to_text(request: SpeechToTextRequest):
    """Convert speech audio to text."""
    text = await speech_to_text(request.audio_base64, request.language.value)
    
    if text:
        return {
            "status": "success",
            "text": text,
            "language": request.language.value,
            "engine": "aws_transcribe",
        }
    else:
        return {
            "status": "fallback",
            "message": "Use browser Web Speech API for STT",
            "engine": "browser_webspeech",
        }
