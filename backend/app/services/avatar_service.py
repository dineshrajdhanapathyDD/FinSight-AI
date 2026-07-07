"""Avatar generation service using D-ID API or local animation fallback."""

import json
import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()

D_ID_API_URL = "https://api.d-id.com"

# Default avatar image (IDBI branded female advisor)
DEFAULT_AVATAR_URL = "https://create-images-results.d-id.com/DefaultPresenters/Mia_f/image.jpeg"


async def generate_avatar_video(
    text: str,
    language: str = "en",
    emotion: str = "neutral",
) -> Optional[str]:
    """Generate talking avatar video using D-ID API."""
    
    if not settings.d_id_api_key:
        # Return None - frontend uses local avatar animation
        return None

    voice_map = {
        "en": "en-IN-NeerjaNeural",
        "hi": "hi-IN-SwaraNeural",
        "ta": "ta-IN-PallaviNeural",
        "te": "te-IN-ShrutiNeural",
        "bn": "bn-IN-TanishaaNeural",
        "mr": "mr-IN-AarohiNeural",
        "kn": "kn-IN-SapnaNeural",
        "ml": "ml-IN-SobhanaNeural",
    }

    try:
        async with httpx.AsyncClient() as client:
            # Create talk
            response = await client.post(
                f"{D_ID_API_URL}/talks",
                headers={
                    "Authorization": f"Basic {settings.d_id_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "source_url": DEFAULT_AVATAR_URL,
                    "script": {
                        "type": "text",
                        "input": text[:500],  # D-ID has text limits
                        "provider": {
                            "type": "microsoft",
                            "voice_id": voice_map.get(language, "en-IN-NeerjaNeural"),
                        },
                    },
                    "config": {
                        "fluent": True,
                        "pad_audio": 0.5,
                    },
                },
                timeout=30.0,
            )
            
            if response.status_code == 201:
                talk_data = response.json()
                talk_id = talk_data.get("id")
                
                # Poll for result (simplified - in production use webhooks)
                import asyncio
                for _ in range(20):
                    await asyncio.sleep(2)
                    result = await client.get(
                        f"{D_ID_API_URL}/talks/{talk_id}",
                        headers={"Authorization": f"Basic {settings.d_id_api_key}"},
                    )
                    result_data = result.json()
                    if result_data.get("status") == "done":
                        return result_data.get("result_url")
                
                return None
            else:
                print(f"D-ID API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Avatar generation error: {e}")
        return None


def get_avatar_config() -> dict:
    """Return avatar configuration for frontend local rendering."""
    return {
        "avatar_url": DEFAULT_AVATAR_URL,
        "idle_video": "/assets/avatar_idle.mp4",
        "expressions": {
            "happy": "smile",
            "neutral": "default",
            "thinking": "look_up",
            "concerned": "slight_frown",
        },
        "use_local_animation": not bool(settings.d_id_api_key),
    }
