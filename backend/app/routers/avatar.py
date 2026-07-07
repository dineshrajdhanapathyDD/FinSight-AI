from fastapi import APIRouter
from app.models.schemas import AvatarRequest
from app.services.avatar_service import generate_avatar_video, get_avatar_config

router = APIRouter()


@router.post("/generate")
async def generate_avatar(request: AvatarRequest):
    """Generate talking avatar video for given text."""
    video_url = await generate_avatar_video(
        text=request.text,
        language=request.language.value,
        emotion=request.emotion or "neutral",
    )

    if video_url:
        return {
            "status": "success",
            "video_url": video_url,
            "engine": "d-id",
        }
    else:
        return {
            "status": "local",
            "message": "Use local avatar animation",
            "text": request.text,
            "emotion": request.emotion,
            "engine": "local_css_animation",
        }


@router.get("/config")
async def avatar_configuration():
    """Get avatar rendering configuration."""
    return get_avatar_config()
