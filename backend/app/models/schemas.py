from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"
    ASSAMESE = "as"


class ChatRequest(BaseModel):
    customer_id: str
    message: str
    language: Language = Language.ENGLISH
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    avatar_video_url: Optional[str] = None
    audio_url: Optional[str] = None
    session_id: str
    agents_used: list[str] = []
    recommendations: Optional[list[dict]] = None
    sentiment: Optional[str] = None


class SpeechToTextRequest(BaseModel):
    audio_base64: str
    language: Language = Language.HINDI


class TextToSpeechRequest(BaseModel):
    text: str
    language: Language = Language.HINDI
    voice_id: Optional[str] = None


class PortfolioRequest(BaseModel):
    customer_id: str


class RecommendationRequest(BaseModel):
    customer_id: str
    goal: Optional[str] = None
    amount: Optional[float] = None
    duration_months: Optional[int] = None


class AvatarRequest(BaseModel):
    text: str
    language: Language = Language.ENGLISH
    emotion: Optional[str] = "neutral"
