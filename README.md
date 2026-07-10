# FinSight AI — Dhan Sakhi 🧠💰

**AI-Powered Avatar-Based Multilingual Wealth Advisor**

> IDBI Innovate 2026 | Track 01: Digital Wealth Management

---

## Live Demo

| Component | URL |
|-----------|-----|
| **Frontend App (HTTPS)** | [https://dgmfyimmjupnd.cloudfront.net](https://dgmfyimmjupnd.cloudfront.net) |
<!--
| **Backend API** | [https://z1go1ry6zi.execute-api.us-east-1.amazonaws.com](https://z1go1ry6zi.execute-api.us-east-1.amazonaws.com) |
| **Health Check** | [https://z1go1ry6zi.execute-api.us-east-1.amazonaws.com/health](https://z1go1ry6zi.execute-api.us-east-1.amazonaws.com/health) |
-->

### Demo Login

| Step | Action |
|------|--------|
| 1 | Enter any email address |
| 2 | Click "Send OTP" |
| 3 | Enter demo OTP: **`123456`** |
| 4 | Select language and customer profile |
| 5 | Start chatting with Dhan Sakhi! |

> Real email OTP delivery is also supported for verified emails via AWS SES.

---

## Overview

FinSight AI (Dhan Sakhi) is an AI-powered digital wealth management application featuring a photorealistic avatar that delivers personalized, scalable wealth advisory services through natural voice conversation in 12+ Indian languages.

### Key Features

- **Email OTP Authentication** — Real email-based OTP via AWS SES + Demo mode (OTP: `123456`) for instant access
- **Multilingual Voice Conversation** — Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, English (9 languages)
- 👩‍💼 **AI Avatar** — Animated, lip-synced digital advisor with emotional intelligence
- 🤖 **Agentic AI** — Research, Compliance, and Portfolio agents work autonomously
- 📊 **Portfolio Dashboard** — Real-time holdings, allocation, AI health score
- 💡 **Personalized Recommendations** — SEBI-compliant, risk-profile aware
- 🎯 **Goal-Based Planning** — Retirement, home purchase, education
- � **Voice Controls** — Play/Pause/Stop voice output at any time

---

## System Architecture


![architecture.drawio.png](https://images.tomarkdown.dev/uploaded/relgufjlufxjb11e.png)


### High-Level Architecture

```mermaid
graph TB
    subgraph Client["🖥️ Client Layer"]
        MA[📱 IDBI Mobile App<br/>React Native]
        WA[🌐 Web App<br/>React + Tailwind CSS]
    end

    subgraph Edge["☁️ Edge Layer"]
        CF[Amazon CloudFront<br/>HTTPS + CDN]
    end

    subgraph Auth["🔐 Authentication"]
        SES[Amazon SES<br/>Email OTP Delivery]
        OTP[OTP Service<br/>Generate + Verify]
    end

    subgraph Gateway["� API Layer"]
        AG[Amazon API Gateway<br/>HTTP API + CORS]
    end

    subgraph Compute["⚡ Serverless Compute"]
        LAM[AWS Lambda<br/>FastAPI + Mangum]
    end

    subgraph Services["🧩 Microservices"]
        AUTH[🔐 Auth Service]
        CHAT[💬 Chat Service]
        PORT[📊 Portfolio Service]
        REC[💡 Recommendation Service]
        SPE[🎤 Speech Service]
        AVA[🎭 Avatar Service]
    end

    subgraph AI["🤖 AI/ML Layer"]
        subgraph Agents["Agentic AI (LangGraph)"]
            RA[🔍 Research Agent]
            CA[✅ Compliance Agent]
            PA[📈 Portfolio Agent]
            EA[⚙️ Execution Agent]
        end
        NOVA[Amazon Nova Lite<br/>Conversational AI]
        NOVAP[Amazon Nova Pro<br/>Financial Analysis]
        KB[Bedrock Knowledge Bases<br/>SEBI Regulations]
    end

    subgraph Speech["🗣️ Speech Layer"]
        POL[Amazon Polly Neural<br/>TTS - 12+ Languages]
        TRN[Amazon Transcribe<br/>STT - Multilingual]
    end

    subgraph Data["� Data Layer"]
        DDB[(DynamoDB<br/>Sessions)]
        RDS[(RDS PostgreSQL<br/>Portfolios)]
        S3[(S3<br/>Assets)]
    end

    subgraph External["🏦 Integrations"]
        IDBI[IDBI Core Banking<br/>Sandbox APIs]
        MKT[NSE/BSE<br/>Market Data]
        MF[BSE StarMF<br/>MF APIs]
    end

    MA --> CF
    WA --> CF
    CF --> AG
    AG --> LAM
    LAM --> Services
    AUTH --> SES
    AUTH --> OTP
    CHAT --> Agents
    Agents --> NOVA
    Agents --> NOVAP
    Agents --> KB
    SPE --> POL
    SPE --> TRN
    Services --> Data
    Services --> External
```

### Authentication Flow (Email OTP)

![process-flow.drawio.png](https://images.tomarkdown.dev/uploaded/lmwjs8vk38w3u5ns.png)


```mermaid
sequenceDiagram
    participant U as 👤 User
    participant App as 📱 Frontend
    participant API as 🔀 API Gateway
    participant Auth as � Auth Service
    participant SES as � AWS SES
    participant Store as 💾 OTP Store

    U->>App: Enter email address
    App->>API: POST /api/auth/send-otp
    API->>Auth: Generate 6-digit OTP
    Auth->>Store: Store OTP (5 min expiry)
    Auth->>SES: Send email with OTP
    SES-->>U: 📧 Email delivered with OTP
    Auth-->>App: {status: "sent"}
    App-->>U: Show OTP input screen

    U->>App: Enter 6-digit OTP
    App->>API: POST /api/auth/verify-otp
    API->>Auth: Validate OTP
    Auth->>Store: Check code + expiry + attempts
    Store-->>Auth: Valid ✓
    Auth-->>App: {verified: true}
    App-->>U: ✅ Login successful → Dashboard
```

### Chat Conversation Flow

```mermaid
sequenceDiagram
    participant C as � Customer
    participant App as 📱 App
    participant STT as 👂 Transcribe
    participant LLM as 🤖 Nova
    participant RA as � Research
    participant CA as ✅ Compliance
    participant PA as 📈 Portfolio
    participant TTS as 🗣️ Polly
    participant AV as 🎭 Avatar

    C->>App: 🎤 Voice Input (Hindi)
    App->>STT: Audio stream
    STT-->>App: Text transcript

    App->>LLM: User message + context
    
    par Parallel Agent Execution
        LLM->>RA: Fetch market data
        RA-->>LLM: Market insights
        LLM->>CA: Check SEBI compliance
        CA-->>LLM: Validated ✓
        LLM->>PA: Analyze portfolio
        PA-->>LLM: Risk + gaps
    end

    LLM-->>App: Personalized response
    App->>TTS: Text → Speech (Hindi)
    TTS-->>App: Audio MP3
    App->>AV: Animate avatar
    AV-->>App: Lip-synced video
    App-->>C: 🗣️👩‍💼 Avatar speaks response
```

## Use-case diagram

![use-case.drawio.png](https://images.tomarkdown.dev/uploaded/zqsxoe5n2qnzquab.png)

### Agentic AI Architecture

```mermaid
graph LR
    subgraph Input["User Input"]
        V[🎤 Voice]
        T[⌨️ Text]
    end

    subgraph Orchestrator["LangGraph Orchestrator"]
        IC[Intent Classifier]
        CM[Context Memory]
        RP[Response Planner]
    end

    subgraph Agents["Specialized Agents"]
        RA[🔍 Research<br/>Market + Fund Data]
        CA[✅ Compliance<br/>SEBI Validation]
        PA[📈 Portfolio<br/>Analysis + Risk]
        EA[⚙️ Execution<br/>Order Placement]
    end

    subgraph Models["Amazon Bedrock"]
        NL[Nova Lite<br/>Fast Conversations]
        NP[Nova Pro<br/>Complex Analysis]
    end

    subgraph Output["Response"]
        TXT[📝 Text]
        AUD[🔊 Audio]
        VID[🎭 Avatar]
    end

    V --> IC
    T --> IC
    IC --> CM
    CM --> RP
    RP --> RA
    RP --> CA
    RP --> PA
    RP --> EA
    RA --> NL
    CA --> NL
    PA --> NP
    EA --> NL
    NL --> TXT
    NP --> TXT
    TXT --> AUD
    AUD --> VID
```

### Deployment Architecture

```mermaid
graph TB
    subgraph Internet
        USER[🌍 Users]
    end

    subgraph AWS["AWS Cloud (us-east-1)"]
        CF[☁️ CloudFront<br/>HTTPS CDN]
        S3F[📦 S3 Bucket<br/>React Frontend]
        APIGW[� HTTP API Gateway<br/>CORS Enabled]
        LAMBDA[⚡ Lambda Function<br/>512MB / 30s timeout]
        SES2[� SES<br/>OTP Emails]
        BEDROCK[🤖 Bedrock<br/>Nova Lite + Pro]
        POLLY[🗣️ Polly Neural<br/>TTS]
    end

    USER --> CF
    CF --> S3F
    USER --> APIGW
    APIGW --> LAMBDA
    LAMBDA --> SES2
    LAMBDA --> BEDROCK
    LAMBDA --> POLLY
```


## Snapshots of the prototype

![prototype-snapshots.drawio.png](https://images.tomarkdown.dev/uploaded/tjpnnpe2ebmrtkbe.png)



## Wireframes/Mock diagrams of the proposed solution

![wireframes.drawio.png](https://images.tomarkdown.dev/uploaded/x4ojhqrj1362jowy.png)




---

## Quick Start

### Option 1: Use Live Demo

Visit https://dgmfyimmjupnd.cloudfront.net

1. Enter any email address
2. Use demo OTP: **`123456`**
3. Select a language and demo customer profile
4. Start chatting!

### Option 2: Local Development

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## Project Structure

```
FinSight AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── routers/
│   │   │   ├── auth.py          # Email OTP authentication
│   │   │   ├── chat.py          # AI chat with agents
│   │   │   ├── portfolio.py     # Portfolio management
│   │   │   ├── recommendations.py
│   │   │   ├── speech.py        # TTS/STT
│   │   │   └── avatar.py        # Avatar generation
│   │   ├── services/
│   │   │   ├── llm_service.py   # Bedrock Nova + fallback
│   │   │   ├── speech_service.py
│   │   │   └── avatar_service.py
│   │   └── data/
│   │       └── customers.py     # Synthetic demo data
│   ├── lambda_handler.py        # AWS Lambda entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Route management
│   │   ├── api.js               # API client
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx    # Email OTP login
│   │   │   ├── LandingPage.jsx  # Language + profile
│   │   │   ├── ChatPage.jsx     # Avatar conversation
│   │   │   └── PortfolioPage.jsx
│   │   └── components/
│   │       ├── Avatar.jsx       # Animated avatar
│   │       └── ChatBubble.jsx
│   ├── package.json
│   └── tailwind.config.js
├── docs/
│   ├── architecture.drawio
│   ├── process-flow.drawio
│   ├── use-case.drawio
│   ├── wireframes.drawio
│   └── prototype-snapshots.drawio
├── infra/
│   └── template.yaml           # SAM template
└── docker-compose.yml
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/send-otp` | Send OTP to email via SES |
| POST | `/api/auth/verify-otp` | Verify OTP code |
| POST | `/api/chat/message` | AI chat with agents |
| GET | `/api/portfolio/{id}` | Customer portfolio |
| GET | `/api/portfolio/{id}/analysis` | AI health score |
| POST | `/api/recommendations/generate` | Investment advice |
| POST | `/api/speech/tts` | Text to speech |
| GET | `/api/avatar/config` | Avatar settings |
| GET | `/health` | Service health |

---

## AWS Services Used

| Service | Purpose |
|---------|---------|
| **AWS Lambda** | Serverless backend (Python 3.11, FastAPI) |
| **API Gateway** | HTTP API with CORS |
| **S3** | Frontend hosting + deployment packages |
| **CloudFront** | HTTPS CDN for frontend |
| **Amazon Bedrock** | Nova Lite v1 for conversational AI |
| **Amazon SES** | Email OTP delivery |
| **Amazon Polly** | Neural text-to-speech (Hindi/English) |
| **IAM** | Least-privilege access control |

---

## Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, Tailwind CSS, Framer Motion | UI with IDBI brand colors |
| **Backend** | Python, FastAPI, LangGraph | API + Agent orchestration |
| **Auth** | AWS SES + OTP (Demo: `123456`) | Email-based secure authentication |
| **LLM** | Amazon Bedrock Nova Lite/Pro | Conversational AI |
| **Speech** | Amazon Polly Neural + Transcribe | Multilingual TTS/STT |
| **Avatar** | D-ID API / CSS Animation | Talking avatar |
| **Hosting** | S3 + CloudFront (HTTPS) | Static frontend |
| **Compute** | AWS Lambda + API Gateway | Serverless backend |
| **Database** | DynamoDB | Session storage |
| **Region** | us-east-1 | All services deployed here |

---

## Color Scheme (IDBI Bank Brand)

| Color | Hex | Usage |
|-------|-----|-------|
| IDBI Teal | `#00857C` | Primary, headers, trust elements |
| IDBI Orange | `#E87722` | Accent, CTAs, highlights, buttons |
| Dark Teal | `#004D47` | Backgrounds, gradients |
| Light Teal | `#E6F5F3` | Hover states, cards |
| Light Orange | `#FEF3E8` | Alerts, notifications |

---

## Languages Supported

| Language | Code | Voice (TTS) | Speech Recognition |
|----------|------|-------------|-------------------|
| English | en | Amazon Polly (Kajal Neural) | Web Speech API |
| Hindi | hi | Amazon Polly (Kajal Neural) | Web Speech API |
| Tamil | ta | Browser TTS | Web Speech API |
| Telugu | te | Browser TTS | Web Speech API |
| Bengali | bn | Browser TTS | Web Speech API |
| Marathi | mr | Browser TTS | Web Speech API |
| Gujarati | gu | Browser TTS | Web Speech API |
| Kannada | kn | Browser TTS | Web Speech API |
| Malayalam | ml | Browser TTS | Web Speech API |

---

## Security

- Email-based OTP authentication (no passwords stored)
- Demo mode with universal OTP (`123456`) for hackathon evaluation
- Real OTP delivery via AWS SES for verified emails
- OTP expires after 5 minutes
- Maximum 5 verification attempts per OTP
- HTTPS via CloudFront
- CORS restricted on API Gateway
- No sensitive data in frontend code
- AWS IAM roles with least privilege

---

## Submission Links

| Item | Link |
|------|------|
| **GitHub Repo** | [https://github.com/dineshrajdhanapathyDD/FinSight-AI](https://github.com/dineshrajdhanapathyDD/FinSight-AI) |
| **Live Product** | [https://dgmfyimmjupnd.cloudfront.net](https://dgmfyimmjupnd.cloudfront.net) |
| **Demo Video** | _To be added_ |
<!--| **API Endpoint** | [https://z1go1ry6zi.execute-api.us-east-1.amazonaws.com](https://z1go1ry6zi.execute-api.us-east-1.amazonaws.com) |-->
---

## Team

**IDBI Innovate 2026 — Track 01: Digital Wealth Management**

---

## License

MIT License — Built for IDBI Innovate 2026 Hackathon
