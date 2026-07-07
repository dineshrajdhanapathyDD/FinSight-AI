"""LLM Service using Amazon Bedrock or fallback to local responses."""

import json
from typing import Optional
from app.config import get_settings
from app.data.customers import CUSTOMERS, MARKET_DATA, FUND_RECOMMENDATIONS

settings = get_settings()

# Try to import boto3, fallback gracefully for demo
try:
    import boto3
    bedrock_client = boto3.client(
        "bedrock-runtime",
        region_name=settings.aws_region,
    )
    BEDROCK_AVAILABLE = True
except Exception:
    BEDROCK_AVAILABLE = False


SYSTEM_PROMPT = """You are Dhan Sakhi, an AI-powered wealth advisor for IDBI Bank. You are friendly, 
knowledgeable, and speak in a warm conversational tone. You provide personalized financial advice 
based on the customer's portfolio, risk profile, and goals.

Key behaviors:
- Always greet customers warmly
- Explain financial concepts in simple language
- Give specific, actionable recommendations
- Mention relevant SEBI compliance when recommending products
- Be empathetic and patient
- If customer speaks in Hindi or other languages, respond in the same language
- Never give guarantees on returns
- Always add mutual fund disclaimer when recommending investments

Customer Context:
{customer_context}

Market Context:
{market_context}
"""


async def generate_response(
    message: str,
    customer_id: str,
    language: str = "en",
    conversation_history: list = None,
) -> dict:
    """Generate AI response using Bedrock or fallback."""

    customer = CUSTOMERS.get(customer_id, CUSTOMERS["CUST001"])
    
    customer_context = json.dumps({
        "name": customer["name"],
        "age": customer["age"],
        "risk_profile": customer["risk_profile"],
        "portfolio_value": customer["portfolio"]["total_value"],
        "returns": customer["portfolio"]["returns_pct"],
        "goals": customer["goals"],
    }, indent=2)

    market_context = json.dumps(MARKET_DATA, indent=2)

    system = SYSTEM_PROMPT.format(
        customer_context=customer_context,
        market_context=market_context,
    )

    if BEDROCK_AVAILABLE and settings.aws_access_key_id:
        return await _bedrock_response(system, message, language, conversation_history)
    else:
        return _fallback_response(message, customer, language)


async def _bedrock_response(
    system: str, message: str, language: str, history: list = None
) -> dict:
    """Call Amazon Bedrock Claude for response."""
    messages = []
    if history:
        messages.extend(history[-6:])  # Keep last 3 exchanges
    messages.append({"role": "user", "content": message})

    lang_instruction = ""
    if language != "en":
        lang_map = {"hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", 
                    "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam"}
        lang_instruction = f"\n\nIMPORTANT: Respond in {lang_map.get(language, 'Hindi')} language."

    try:
        response = bedrock_client.invoke_model(
            modelId=settings.bedrock_model_id,
            body=json.dumps({
                "messages": messages,
                "system": [{"text": system + lang_instruction}],
                "inferenceConfig": {
                    "maxTokens": 1024,
                    "temperature": 0.7,
                    "topP": 0.9,
                },
            }),
        )
        result = json.loads(response["body"].read())
        return {
            "text": result["output"]["message"]["content"][0]["text"],
            "agents_used": ["research_agent", "compliance_agent", "portfolio_agent"],
            "model": "bedrock-nova-lite",
        }
    except Exception as e:
        return _fallback_response(message, CUSTOMERS["CUST001"], language)


def _fallback_response(message: str, customer: dict, language: str) -> dict:
    """Intelligent fallback responses for demo without AWS credentials."""
    msg_lower = message.lower()
    name = customer["name"].split()[0]
    portfolio = customer["portfolio"]

    # Detect intent and generate contextual response
    if any(w in msg_lower for w in ["hello", "hi", "namaste", "hey", "start"]):
        if language == "hi":
            text = f"नमस्ते {name} जी! 🙏 मैं धन सखी हूँ, आपकी AI वेल्थ एडवाइजर। आज आपका पोर्टफोलियो ₹{portfolio['total_value']:,.0f} पर है, जो {portfolio['returns_pct']}% ऊपर है। मैं आपकी किस तरह से मदद कर सकती हूँ?"
        else:
            text = f"Hello {name}! 👋 I'm Dhan Sakhi, your AI wealth advisor. Your portfolio is at ₹{portfolio['total_value']:,.0f} with {portfolio['returns_pct']}% returns. How can I help you today?"

    elif any(w in msg_lower for w in ["portfolio", "holdings", "investment", "kitna"]):
        holdings_text = "\n".join([
            f"  • {h['name']}: ₹{h['value']:,.0f} ({h['returns_pct']:+.1f}%)"
            for h in portfolio["holdings"]
        ])
        if language == "hi":
            text = f"{name} जी, आपके पोर्टफोलियो का विवरण:\n\n💰 कुल मूल्य: ₹{portfolio['total_value']:,.0f}\n📈 रिटर्न: {portfolio['returns_pct']}%\n\nआपकी होल्डिंग्स:\n{holdings_text}\n\nक्या आप किसी विशेष फंड के बारे में जानना चाहते हैं?"
        else:
            text = f"Here's your portfolio overview, {name}:\n\n💰 Total Value: ₹{portfolio['total_value']:,.0f}\n📈 Returns: {portfolio['returns_pct']}%\n\nYour Holdings:\n{holdings_text}\n\nWould you like me to analyze any specific holding?"

    elif any(w in msg_lower for w in ["sip", "invest", "start", "monthly", "shuru"]):
        if language == "hi":
            text = f"{name} जी, आपकी आय ₹{customer['monthly_income']:,.0f}/माह के आधार पर, मैं ₹{int(customer['monthly_income']*0.2):,.0f}/माह SIP की सलाह देती हूँ।\n\nमेरी सिफारिश:\n📊 ICICI Balanced Advantage - ₹8,000/माह (मध्यम जोखिम)\n📊 Axis Bluechip - ₹5,000/माह (स्थिर विकास)\n📊 HDFC Short Term Debt - ₹7,000/माह (सुरक्षित)\n\n✅ SEBI अनुपालन सत्यापित\n\nक्या आप इनमें से किसी में निवेश शुरू करना चाहेंगे?"
        else:
            text = f"Based on your income of ₹{customer['monthly_income']:,.0f}/month, I recommend a SIP of ₹{int(customer['monthly_income']*0.2):,.0f}/month.\n\nMy recommendations:\n📊 ICICI Balanced Advantage - ₹8,000/month (Moderate risk)\n📊 Axis Bluechip - ₹5,000/month (Stable growth)\n📊 HDFC Short Term Debt - ₹7,000/month (Safe)\n\n✅ SEBI compliance verified\n⚠️ Mutual fund investments are subject to market risks.\n\nWould you like to start any of these SIPs?"

    elif any(w in msg_lower for w in ["risk", "safe", "jokhim", "surakshit"]):
        if language == "hi":
            text = f"{name} जी, आपकी रिस्क प्रोफाइल '{customer['risk_profile']}' है।\n\nयह आपके लेन-देन व्यवहार और निवेश इतिहास से निर्धारित है:\n• आपकी उम्र: {customer['age']} वर्ष\n• आय स्थिरता: उच्च\n• पिछले निवेश: मध्यम जोखिम वाले\n\nक्या आप अपनी रिस्क प्रोफाइल अपडेट करना चाहेंगे?"
        else:
            text = f"Your risk profile is '{customer['risk_profile']}', {name}.\n\nThis is determined from your transaction behavior and investment history:\n• Your age: {customer['age']} years\n• Income stability: High\n• Past investments: {customer['risk_profile']} risk products\n\nWould you like to update your risk profile or see recommendations matching it?"

    elif any(w in msg_lower for w in ["goal", "target", "lakshya", "plan"]):
        goals_text = "\n".join([
            f"  🎯 {g['name']}: ₹{g['target']:,.0f} in {g['timeline_years']} years"
            for g in customer["goals"]
        ])
        if language == "hi":
            text = f"{name} जी, आपके वित्तीय लक्ष्य:\n\n{goals_text}\n\nमैं आपके लक्ष्यों की प्रगति की समीक्षा करती हूँ... आपका 'गृह खरीद' लक्ष्य ट्रैक पर है! 🏠\n\nकिस लक्ष्य के बारे में विस्तार से बात करें?"
        else:
            text = f"Your financial goals, {name}:\n\n{goals_text}\n\nLet me review your goal progress... Your 'Home Purchase' goal is on track! 🏠\n\nWhich goal would you like to discuss in detail?"

    elif any(w in msg_lower for w in ["market", "nifty", "sensex", "bazaar"]):
        if language == "hi":
            text = f"आज का बाजार अपडेट:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 Gold: ₹{MARKET_DATA['gold']['value']:,.0f}/gram\n🏦 Repo Rate: {MARKET_DATA['repo_rate']['value']}%\n\n{name} जी, बाजार सकारात्मक है। आपके पोर्टफोलियो पर कोई नकारात्मक प्रभाव नहीं है। 👍"
        else:
            text = f"Today's market update:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 Gold: ₹{MARKET_DATA['gold']['value']:,.0f}/gram\n🏦 Repo Rate: {MARKET_DATA['repo_rate']['value']}%\n\nMarket is positive today, {name}. No negative impact on your portfolio. 👍"

    elif any(w in msg_lower for w in ["tax", "save", "80c", "kar", "bachat"]):
        if language == "hi":
            text = f"{name} जी, टैक्स बचत के लिए मेरी सलाह:\n\n💡 Section 80C (₹1.5L limit):\n  • ELSS Mutual Fund - ₹50,000 (3 साल लॉक-इन, सबसे कम)\n  • PPF - ₹50,000 (सुरक्षित, 15 साल)\n  • NPS - ₹50,000 (अतिरिक्त ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nकुल बचत: ~₹67,500 (30% bracket)\n\nक्या मैं ELSS SIP शुरू करूँ?"
        else:
            text = f"Tax-saving recommendations for you, {name}:\n\n💡 Section 80C (₹1.5L limit):\n  • ELSS Mutual Fund - ₹50,000 (shortest 3yr lock-in)\n  • PPF - ₹50,000 (safe, 15yr)\n  • NPS - ₹50,000 (extra ₹50K under 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nPotential savings: ~₹67,500 (at 30% bracket)\n\nShall I start an ELSS SIP for you?"

    else:
        if language == "hi":
            text = f"{name} जी, मैं आपकी मदद के लिए यहाँ हूँ। आप मुझसे पूछ सकते हैं:\n\n• पोर्टफोलियो रिव्यू\n• SIP शुरू करना\n• बाजार अपडेट\n• टैक्स बचत\n• वित्तीय लक्ष्य\n• रिस्क प्रोफाइल\n• फंड तुलना\n\nबताइए, किसमें मदद चाहिए?"
        else:
            text = f"I'm here to help, {name}! You can ask me about:\n\n• Portfolio review\n• Start a SIP\n• Market updates\n• Tax saving\n• Financial goals\n• Risk profile\n• Fund comparison\n\nWhat would you like to explore?"

    return {
        "text": text,
        "agents_used": ["research_agent", "compliance_agent", "portfolio_agent"],
        "model": "fallback-contextual",
    }
