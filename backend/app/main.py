from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import chat, portfolio, speech, recommendations, avatar

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Avatar-Based Multilingual Wealth Advisor for IDBI Bank",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(speech.router, prefix="/api/speech", tags=["Speech"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(avatar.router, prefix="/api/avatar", tags=["Avatar"])


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "tracks": "IDBI Innovate 2026 - Track 01: Digital Wealth Management",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
