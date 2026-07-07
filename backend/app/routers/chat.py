import uuid
from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import generate_response
from app.services.speech_service import text_to_speech

router = APIRouter()

# In-memory session store (use Redis in production)
sessions: dict = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Process a chat message and return AI response with optional audio."""
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = {"history": [], "language": request.language}

    session = sessions[session_id]
    session["history"].append({"role": "user", "content": request.message})

    # Generate AI response
    result = await generate_response(
        message=request.message,
        customer_id=request.customer_id,
        language=request.language.value,
        conversation_history=session["history"],
    )

    response_text = result["text"]
    session["history"].append({"role": "assistant", "content": response_text})

    # Generate audio (if AWS available)
    audio_url = await text_to_speech(response_text, request.language.value)

    return ChatResponse(
        response=response_text,
        audio_url=audio_url,
        session_id=session_id,
        agents_used=result.get("agents_used", []),
        sentiment="positive",
    )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get conversation history for a session."""
    session = sessions.get(session_id)
    if not session:
        return {"history": []}
    return {"history": session["history"], "language": session.get("language")}


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a conversation session."""
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "cleared"}
