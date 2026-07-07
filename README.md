# FinSight AI — Dhan Sakhi 🧠💰

**AI-Powered Avatar-Based Multilingual Wealth Advisor**

> IDBI Innovate 2026 | Track 01: Digital Wealth Management

---

## Overview

FinSight AI (Dhan Sakhi) is an AI-powered digital wealth management application featuring a photorealistic avatar that delivers personalized, scalable wealth advisory services through natural voice conversation in 12+ Indian languages.

### Key Features

- 🗣️ **Multilingual Voice Conversation** — Hindi, Tamil, Telugu, Bengali, English + 7 more
- 👩‍💼 **AI Avatar** — Animated, lip-synced digital advisor with emotional intelligence
- 🤖 **Agentic AI** — Research, Compliance, and Portfolio agents work autonomously
- 📊 **Portfolio Dashboard** — Real-time holdings, allocation, AI health score
- 💡 **Personalized Recommendations** — SEBI-compliant, risk-profile aware
- 🎯 **Goal-Based Planning** — Retirement, home purchase, education
- 🔒 **Compliance Built-In** — Every recommendation validated before delivery

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  React App  │────▶│  FastAPI     │────▶│  Amazon Bedrock  │
│  (Frontend) │     │  (Backend)   │     │  (Claude LLM)    │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼─────┐ ┌───▼──────┐
        │ Research  │ │Compliance│ │Portfolio  │
        │ Agent    │ │ Agent    │ │ Agent     │
        └──────────┘ └─────────┘ └──────────┘
```

---

## Quick Start

### Option 1: Local Development (Recommended for Demo)

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
# Edit .env with your AWS credentials (optional - works without them)

uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### Option 2: Docker

```bash
docker-compose up --build
```

Open http://localhost

---

## Demo Without AWS Credentials

The app works **fully without AWS credentials** using intelligent fallback:

| Feature | With AWS | Without AWS (Demo Mode) |
|---------|----------|------------------------|
| Chat AI | Amazon Bedrock Claude | Context-aware local responses |
| Voice Input | AWS Transcribe | Browser Web Speech API |
| Voice Output | Amazon Polly | Browser Speech Synthesis |
| Avatar Video | D-ID API | CSS animated avatar |

This means you can demo the full experience instantly without any setup.

---

## Project Structure

```
FinSight AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── routers/
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   ├── portfolio.py     # Portfolio endpoints
│   │   │   ├── recommendations.py
│   │   │   ├── speech.py        # TTS/STT endpoints
│   │   │   └── avatar.py        # Avatar generation
│   │   ├── services/
│   │   │   ├── llm_service.py   # Bedrock + fallback LLM
│   │   │   ├── speech_service.py
│   │   │   └── avatar_service.py
│   │   ├── data/
│   │   │   └── customers.py     # Synthetic demo data
│   │   └── models/
│   │       └── schemas.py       # Pydantic models
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js               # API client
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx  # Language + profile selection
│   │   │   ├── ChatPage.jsx     # Main conversation UI
│   │   │   └── PortfolioPage.jsx
│   │   └── components/
│   │       ├── Avatar.jsx       # Animated avatar component
│   │       └── ChatBubble.jsx
│   ├── package.json
│   ├── Dockerfile
│   └── tailwind.config.js
├── docker-compose.yml
├── idea.md                      # Full submission document
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/message` | Send message, get AI response |
| GET | `/api/portfolio/{id}` | Get customer portfolio |
| GET | `/api/portfolio/{id}/analysis` | AI portfolio analysis |
| GET | `/api/portfolio/market` | Market data |
| POST | `/api/recommendations/generate` | Investment recommendations |
| POST | `/api/speech/tts` | Text to speech |
| POST | `/api/speech/stt` | Speech to text |
| POST | `/api/avatar/generate` | Generate avatar video |
| GET | `/api/avatar/config` | Avatar configuration |

---

## Technologies

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS, Framer Motion, Vite |
| Backend | Python, FastAPI, LangGraph, LangChain |
| AI/ML | Amazon Bedrock (Nova Lite), Polly, Transcribe, SageMaker |
| Avatar | D-ID API / CSS Animation fallback |
| Infrastructure | Docker, Nginx, AWS (optional) |

---

## Demo Profiles

| Customer | Risk Profile | Language | Portfolio |
|----------|-------------|----------|-----------|
| Rajesh Kumar | Moderate | Hindi | ₹8.45L |
| Priya Sharma | Aggressive | English | ₹3.20L |
| Venkatesh Iyer | Conservative | Tamil | ₹45.20L |

---

## Team

**IDBI Innovate 2026 — Track 01: Digital Wealth Management**

---

## License

MIT License — Built for IDBI Innovate 2026 Hackathon
