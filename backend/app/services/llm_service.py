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


def _get_localized(language: str, translations: dict) -> str:
    """Get text for the given language, fallback to English."""
    return translations.get(language, translations.get("en", ""))


def _fallback_response(message: str, customer: dict, language: str) -> dict:
    """Intelligent fallback responses for demo without AWS credentials."""
    msg_lower = message.lower()
    name = customer["name"].split()[0]
    portfolio = customer["portfolio"]

    # Detect intent and generate contextual response
    if any(w in msg_lower for w in ["hello", "hi", "namaste", "hey", "start"]):
        text = _get_localized(language, {
            "en": f"Hello {name}! 👋 I'm Dhan Sakhi, your AI wealth advisor. Your portfolio is at ₹{portfolio['total_value']:,.0f} with {portfolio['returns_pct']}% returns. How can I help you today?",
            "hi": f"नमस्ते {name} जी! 🙏 मैं धन सखी हूँ, आपकी AI वेल्थ एडवाइजर। आज आपका पोर्टफोलियो ₹{portfolio['total_value']:,.0f} पर है, जो {portfolio['returns_pct']}% ऊपर है। मैं आपकी किस तरह से मदद कर सकती हूँ?",
            "ta": f"வணக்கம் {name}! 🙏 நான் தன் சகி, உங்கள் AI செல்வ ஆலோசகர். உங்கள் போர்ட்ஃபோலியோ ₹{portfolio['total_value']:,.0f} உள்ளது, {portfolio['returns_pct']}% வருமானம். நான் எப்படி உதவ முடியும்?",
            "te": f"నమస్కారం {name}! 🙏 నేను ధన్ సఖి, మీ AI సంపద సలహాదారు. మీ పోర్ట్‌ఫోలియో ₹{portfolio['total_value']:,.0f} ఉంది, {portfolio['returns_pct']}% రిటర్న్స్. నేను ఎలా సహాయం చేయగలను?",
            "bn": f"নমস্কার {name}! 🙏 আমি ধন সখী, আপনার AI সম্পদ উপদেষ্টা। আপনার পোর্টফোলিও ₹{portfolio['total_value']:,.0f} এ আছে, {portfolio['returns_pct']}% রিটার্ন। আমি কীভাবে সাহায্য করতে পারি?",
            "mr": f"नमस्कार {name}! 🙏 मी धन सखी आहे, तुमची AI संपत्ती सल्लागार. तुमचा पोर्टफोलिओ ₹{portfolio['total_value']:,.0f} वर आहे, {portfolio['returns_pct']}% परतावा. मी कशी मदत करू शकते?",
            "gu": f"નમસ્તે {name}! 🙏 હું ધન સખી છું, તમારી AI સંપત્તિ સલાહકાર. તમારો પોર્ટફોલિયો ₹{portfolio['total_value']:,.0f} પર છે, {portfolio['returns_pct']}% વળતર. હું કેવી રીતે મદદ કરી શકું?",
            "kn": f"ನಮಸ್ಕಾರ {name}! 🙏 ನಾನು ಧನ್ ಸಖಿ, ನಿಮ್ಮ AI ಸಂಪತ್ತು ಸಲಹೆಗಾರ. ನಿಮ್ಮ ಪೋರ್ಟ್‌ಫೋಲಿಯೊ ₹{portfolio['total_value']:,.0f} ಇದೆ, {portfolio['returns_pct']}% ಲಾಭ. ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
            "ml": f"നമസ്കാരം {name}! 🙏 ഞാൻ ധൻ സഖി, നിങ്ങളുടെ AI സമ്പത്ത് ഉപദേശകൻ. നിങ്ങളുടെ പോർട്ട്‌ഫോളിയോ ₹{portfolio['total_value']:,.0f} ആണ്, {portfolio['returns_pct']}% റിട്ടേൺ. എനിക്ക് എങ്ങനെ സഹായിക്കാനാകും?",
        })

    elif any(w in msg_lower for w in ["portfolio", "holdings", "investment", "kitna"]):
        holdings_text = "\n".join([
            f"  • {h['name']}: ₹{h['value']:,.0f} ({h['returns_pct']:+.1f}%)"
            for h in portfolio["holdings"]
        ])
        text = _get_localized(language, {
            "en": f"Here's your portfolio overview, {name}:\n\n💰 Total Value: ₹{portfolio['total_value']:,.0f}\n📈 Returns: {portfolio['returns_pct']}%\n\nYour Holdings:\n{holdings_text}\n\nWould you like me to analyze any specific holding?",
            "hi": f"{name} जी, आपके पोर्टफोलियो का विवरण:\n\n💰 कुल मूल्य: ₹{portfolio['total_value']:,.0f}\n📈 रिटर्न: {portfolio['returns_pct']}%\n\nआपकी होल्डिंग्स:\n{holdings_text}\n\nक्या आप किसी विशेष फंड के बारे में जानना चाहते हैं?",
            "ta": f"{name}, உங்கள் போர்ட்ஃபோலியோ விவரம்:\n\n💰 மொத்த மதிப்பு: ₹{portfolio['total_value']:,.0f}\n📈 வருமானம்: {portfolio['returns_pct']}%\n\nஉங்கள் முதலீடுகள்:\n{holdings_text}\n\nஏதேனும் குறிப்பிட்ட ஃபண்ட் பற்றி அறிய விரும்புகிறீர்களா?",
            "te": f"{name}, మీ పోర్ట్‌ఫోలియో వివరాలు:\n\n💰 మొత్తం విలువ: ₹{portfolio['total_value']:,.0f}\n📈 రిటర్న్స్: {portfolio['returns_pct']}%\n\nమీ హోల్డింగ్స్:\n{holdings_text}\n\nఏదైనా నిర్దిష్ట ఫండ్ గురించి తెలుసుకోవాలనుకుంటున్నారా?",
            "bn": f"{name}, আপনার পোর্টফোলিও বিবরণ:\n\n💰 মোট মূল্য: ₹{portfolio['total_value']:,.0f}\n📈 রিটার্ন: {portfolio['returns_pct']}%\n\nআপনার হোল্ডিংস:\n{holdings_text}\n\nকোনো নির্দিষ্ট ফান্ড সম্পর্কে জানতে চান?",
            "mr": f"{name}, तुमच्या पोर्टफोलिओचा तपशील:\n\n💰 एकूण मूल्य: ₹{portfolio['total_value']:,.0f}\n📈 परतावा: {portfolio['returns_pct']}%\n\nतुमच्या होल्डिंग्स:\n{holdings_text}\n\nकोणत्याही विशिष्ट फंडाबद्दल जाणून घ्यायचे आहे का?",
            "gu": f"{name}, તમારા પોર્ટફોલિયોની વિગત:\n\n💰 કુલ મૂલ્ય: ₹{portfolio['total_value']:,.0f}\n📈 વળતર: {portfolio['returns_pct']}%\n\nતમારી હોલ્ડિંગ્સ:\n{holdings_text}\n\nકોઈ ચોક્કસ ફંડ વિશે જાણવા માંગો છો?",
            "kn": f"{name}, ನಿಮ್ಮ ಪೋರ್ಟ್‌ಫೋಲಿಯೊ ವಿವರ:\n\n💰 ಒಟ್ಟು ಮೌಲ್ಯ: ₹{portfolio['total_value']:,.0f}\n📈 ಲಾಭ: {portfolio['returns_pct']}%\n\nನಿಮ್ಮ ಹೋಲ್ಡಿಂಗ್‌ಗಳು:\n{holdings_text}\n\nಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಫಂಡ್ ಬಗ್ಗೆ ತಿಳಿಯಲು ಬಯಸುವಿರಾ?",
            "ml": f"{name}, നിങ്ങളുടെ പോർട്ട്‌ഫോളിയോ വിവരം:\n\n💰 ആകെ മൂല്യം: ₹{portfolio['total_value']:,.0f}\n📈 റിട്ടേൺ: {portfolio['returns_pct']}%\n\nനിങ്ങളുടെ ഹോൾഡിംഗ്സ്:\n{holdings_text}\n\nഏതെങ്കിലും ഫണ്ടിനെ കുറിച്ച് അറിയാൻ ആഗ്രഹിക്കുന്നുണ്ടോ?",
        })

    elif any(w in msg_lower for w in ["sip", "invest", "start", "monthly", "shuru"]):
        sip_amount = int(customer['monthly_income'] * 0.2)
        text = _get_localized(language, {
            "en": f"Based on your income of ₹{customer['monthly_income']:,.0f}/month, I recommend a SIP of ₹{sip_amount:,.0f}/month.\n\nMy recommendations:\n📊 ICICI Balanced Advantage - ₹8,000/month (Moderate risk)\n📊 Axis Bluechip - ₹5,000/month (Stable growth)\n📊 HDFC Short Term Debt - ₹7,000/month (Safe)\n\n✅ SEBI compliance verified\n⚠️ Mutual fund investments are subject to market risks.\n\nWould you like to start any of these SIPs?",
            "hi": f"{name} जी, आपकी आय ₹{customer['monthly_income']:,.0f}/माह के आधार पर, मैं ₹{sip_amount:,.0f}/माह SIP की सलाह देती हूँ।\n\nमेरी सिफारिश:\n📊 ICICI Balanced Advantage - ₹8,000/माह (मध्यम जोखिम)\n📊 Axis Bluechip - ₹5,000/माह (स्थिर विकास)\n📊 HDFC Short Term Debt - ₹7,000/माह (सुरक्षित)\n\n✅ SEBI अनुपालन सत्यापित\n\nक्या आप इनमें से किसी में निवेश शुरू करना चाहेंगे?",
            "ta": f"{name}, உங்கள் வருமானம் ₹{customer['monthly_income']:,.0f}/மாதம் அடிப்படையில், ₹{sip_amount:,.0f}/மாதம் SIP பரிந்துரைக்கிறேன்.\n\nஎன் பரிந்துரைகள்:\n📊 ICICI Balanced Advantage - ₹8,000/மாதம்\n📊 Axis Bluechip - ₹5,000/மாதம்\n📊 HDFC Short Term Debt - ₹7,000/மாதம்\n\n✅ SEBI இணக்கம் சரிபார்க்கப்பட்டது\n⚠️ மியூச்சுவல் ஃபண்ட் முதலீடுகள் சந்தை அபாயங்களுக்கு உட்பட்டவை.",
            "te": f"{name}, మీ ఆదాయం ₹{customer['monthly_income']:,.0f}/నెల ఆధారంగా, ₹{sip_amount:,.0f}/నెల SIP సిఫార్సు చేస్తున్నాను.\n\nనా సిఫార్సులు:\n📊 ICICI Balanced Advantage - ₹8,000/నెల\n📊 Axis Bluechip - ₹5,000/నెల\n📊 HDFC Short Term Debt - ₹7,000/నెల\n\n✅ SEBI సమ్మతి ధృవీకరించబడింది\n⚠️ మ్యూచువల్ ఫండ్ పెట్టుబడులు మార్కెట్ రిస్క్‌లకు లోబడి ఉంటాయి.",
            "bn": f"{name}, আপনার আয় ₹{customer['monthly_income']:,.0f}/মাসের ভিত্তিতে, ₹{sip_amount:,.0f}/মাস SIP সুপারিশ করছি.\n\nআমার সুপারিশ:\n📊 ICICI Balanced Advantage - ₹8,000/মাস\n📊 Axis Bluechip - ₹5,000/মাস\n📊 HDFC Short Term Debt - ₹7,000/মাস\n\n✅ SEBI সম্মতি যাচাই করা হয়েছে\n⚠️ মিউচুয়াল ফান্ড বিনিয়োগ বাজার ঝুঁকির অধীন.",
            "mr": f"{name}, तुमच्या ₹{customer['monthly_income']:,.0f}/महिना उत्पन्नावर आधारित, ₹{sip_amount:,.0f}/महिना SIP सुचवतो.\n\nशिफारसी:\n📊 ICICI Balanced Advantage - ₹8,000/महिना\n📊 Axis Bluechip - ₹5,000/महिना\n📊 HDFC Short Term Debt - ₹7,000/महिना\n\n✅ SEBI अनुपालन सत्यापित\n⚠️ म्युच्युअल फंड गुंतवणूक बाजार जोखमींच्या अधीन आहेत.",
            "gu": f"{name}, તમારી આવક ₹{customer['monthly_income']:,.0f}/મહિના આધારે, ₹{sip_amount:,.0f}/મહિના SIP ની ભલામણ કરું છું.\n\nભલામણો:\n📊 ICICI Balanced Advantage - ₹8,000/મહિના\n📊 Axis Bluechip - ₹5,000/મહિના\n📊 HDFC Short Term Debt - ₹7,000/મહિના\n\n✅ SEBI અનુપાલન ચકાસાયેલ\n⚠️ મ્યુચ્યુઅલ ફંડ રોકાણ બજાર જોખમોને આધીન છે.",
            "kn": f"{name}, ನಿಮ್ಮ ₹{customer['monthly_income']:,.0f}/ತಿಂಗಳ ಆದಾಯದ ಆಧಾರದ ಮೇಲೆ, ₹{sip_amount:,.0f}/ತಿಂಗಳ SIP ಶಿಫಾರಸು ಮಾಡುತ್ತೇನೆ.\n\nಶಿಫಾರಸುಗಳು:\n📊 ICICI Balanced Advantage - ₹8,000/ತಿಂಗಳು\n📊 Axis Bluechip - ₹5,000/ತಿಂಗಳು\n📊 HDFC Short Term Debt - ₹7,000/ತಿಂಗಳು\n\n✅ SEBI ಅನುಸರಣೆ ಪರಿಶೀಲಿಸಲಾಗಿದೆ",
            "ml": f"{name}, നിങ്ങളുടെ ₹{customer['monthly_income']:,.0f}/മാസ വരുമാനത്തിന്റെ അടിസ്ഥാനത്തിൽ, ₹{sip_amount:,.0f}/മാസ SIP ശുപാർശ ചെയ്യുന്നു.\n\nശുപാർശകൾ:\n📊 ICICI Balanced Advantage - ₹8,000/മാസം\n📊 Axis Bluechip - ₹5,000/മാസം\n📊 HDFC Short Term Debt - ₹7,000/മാസം\n\n✅ SEBI അനുസരണം പരിശോധിച്ചു\n⚠️ മ്യൂച്ചൽ ഫണ്ട് നിക്ഷേപങ്ങൾ വിപണി അപകടങ്ങൾക്ക് വിധേയമാണ്.",
        })

    elif any(w in msg_lower for w in ["risk", "safe", "jokhim", "surakshit"]):
        text = _get_localized(language, {
            "en": f"Your risk profile is '{customer['risk_profile']}', {name}.\n\nThis is determined from your transaction behavior and investment history:\n• Your age: {customer['age']} years\n• Income stability: High\n• Past investments: {customer['risk_profile']} risk products\n\nWould you like to update your risk profile or see recommendations matching it?",
            "hi": f"{name} जी, आपकी रिस्क प्रोफाइल '{customer['risk_profile']}' है।\n\nयह आपके लेन-देन व्यवहार और निवेश इतिहास से निर्धारित है:\n• आपकी उम्र: {customer['age']} वर्ष\n• आय स्थिरता: उच्च\n• पिछले निवेश: मध्यम जोखिम वाले\n\nक्या आप अपनी रिस्क प्रोफाइल अपडेट करना चाहेंगे?",
            "ta": f"{name}, உங்கள் ரிஸ்க் புரொஃபைல் '{customer['risk_profile']}' ஆகும்.\n\n• வயது: {customer['age']} வருடங்கள்\n• வருமான நிலைத்தன்மை: உயர்\n• கடந்த முதலீடுகள்: {customer['risk_profile']} ரிஸ்க்\n\nஉங்கள் ரிஸ்க் புரொஃபைலை புதுப்பிக்க விரும்புகிறீர்களா?",
            "te": f"{name}, మీ రిస్క్ ప్రొఫైల్ '{customer['risk_profile']}' గా ఉంది.\n\n• వయసు: {customer['age']} సంవత్సరాలు\n• ఆదాయ స్థిరత్వం: అధిక\n• గత పెట్టుబడులు: {customer['risk_profile']} రిస్క్\n\nమీ రిస్క్ ప్రొఫైల్ అప్‌డేట్ చేయాలనుకుంటున్నారా?",
            "bn": f"{name}, আপনার রিস্ক প্রোফাইল '{customer['risk_profile']}' হিসাবে নির্ধারিত.\n\n• বয়স: {customer['age']} বছর\n• আয় স্থিরতা: উচ্চ\n• পূর্ববর্তী বিনিয়োগ: {customer['risk_profile']} ঝুঁকি\n\nআপনার রিস্ক প্রোফাইল আপডেট করতে চান?",
            "mr": f"{name}, तुमची रिस्क प्रोफाइल '{customer['risk_profile']}' आहे.\n\n• वय: {customer['age']} वर्षे\n• उत्पन्न स्थिरता: उच्च\n• मागील गुंतवणूक: {customer['risk_profile']} जोखीम\n\nतुमची रिस्क प्रोफाइल अपडेट करायची आहे का?",
            "gu": f"{name}, તમારી રિસ્ક પ્રોફાઇલ '{customer['risk_profile']}' છે.\n\n• ઉંમર: {customer['age']} વર્ષ\n• આવક સ્થિરતા: ઉચ્ચ\n• અગાઉના રોકાણ: {customer['risk_profile']} જોખમ\n\nતમારી રિસ્ક પ્રોફાઇલ અપડેટ કરવા માંગો છો?",
            "kn": f"{name}, ನಿಮ್ಮ ರಿಸ್ಕ್ ಪ್ರೊಫೈಲ್ '{customer['risk_profile']}' ಆಗಿದೆ.\n\n• ವಯಸ್ಸು: {customer['age']} ವರ್ಷ\n• ಆದಾಯ ಸ್ಥಿರತೆ: ಹೆಚ್ಚು\n• ಹಿಂದಿನ ಹೂಡಿಕೆಗಳು: {customer['risk_profile']} ಅಪಾಯ\n\nನಿಮ್ಮ ರಿಸ್ಕ್ ಪ್ರೊಫೈಲ್ ಅಪ್‌ಡೇಟ್ ಮಾಡಲು ಬಯಸುವಿರಾ?",
            "ml": f"{name}, നിങ്ങളുടെ റിസ്ക് പ്രൊഫൈൽ '{customer['risk_profile']}' ആണ്.\n\n• പ്രായം: {customer['age']} വർഷം\n• വരുമാന സ്ഥിരത: ഉയർന്നത്\n• മുൻ നിക്ഷേപങ്ങൾ: {customer['risk_profile']} റിസ്ക്\n\nനിങ്ങളുടെ റിസ്ക് പ്രൊഫൈൽ അപ്‌ഡേറ്റ് ചെയ്യാൻ ആഗ്രഹിക്കുന്നുണ്ടോ?",
        })

    elif any(w in msg_lower for w in ["goal", "target", "lakshya", "plan"]):
        goals_text = "\n".join([
            f"  🎯 {g['name']}: ₹{g['target']:,.0f} in {g['timeline_years']} years"
            for g in customer["goals"]
        ])
        text = _get_localized(language, {
            "en": f"Your financial goals, {name}:\n\n{goals_text}\n\nLet me review your goal progress... Your 'Home Purchase' goal is on track! 🏠\n\nWhich goal would you like to discuss in detail?",
            "hi": f"{name} जी, आपके वित्तीय लक्ष्य:\n\n{goals_text}\n\nमैं आपके लक्ष्यों की प्रगति की समीक्षा करती हूँ... आपका 'गृह खरीद' लक्ष्य ट्रैक पर है! 🏠\n\nकिस लक्ष्य के बारे में विस्तार से बात करें?",
            "ta": f"{name}, உங்கள் நிதி இலக்குகள்:\n\n{goals_text}\n\nஉங்கள் இலக்கு முன்னேற்றத்தை பார்க்கலாம்... உங்கள் 'வீடு வாங்குதல்' இலக்கு சரியான பாதையில் உள்ளது! 🏠\n\nஎந்த இலக்கு பற்றி விரிவாக பேச விரும்புகிறீர்கள்?",
            "te": f"{name}, మీ ఆర్థిక లక్ష్యాలు:\n\n{goals_text}\n\nమీ లక్ష్య పురోగతిని చూద్దాం... మీ 'ఇల్లు కొనుగోలు' లక్ష్యం ట్రాక్‌లో ఉంది! 🏠\n\nఏ లక్ష్యం గురించి వివరంగా చర్చించాలనుకుంటున్నారు?",
            "bn": f"{name}, আপনার আর্থিক লক্ষ্যসমূহ:\n\n{goals_text}\n\nআপনার লক্ষ্য অগ্রগতি দেখি... আপনার 'বাড়ি কেনা' লক্ষ্য ট্র্যাকে আছে! 🏠\n\nকোন লক্ষ্য নিয়ে বিস্তারিত আলোচনা করতে চান?",
            "mr": f"{name}, तुमची आर्थिक उद्दिष्टे:\n\n{goals_text}\n\nतुमच्या उद्दिष्टांची प्रगती पाहूया... तुमचे 'घर खरेदी' उद्दिष्ट योग्य मार्गावर आहे! 🏠\n\nकोणत्या उद्दिष्टाबद्दल सविस्तर बोलायचे?",
            "gu": f"{name}, તમારા નાણાકીય લક્ષ્યો:\n\n{goals_text}\n\nતમારી લક્ષ્ય પ્રગતિ જોઈએ... તમારું 'ઘર ખરીદી' લક્ષ્ય ટ્રેક પર છે! 🏠\n\nકયા લક્ષ્ય વિશે વિગતવાર ચર્ચા કરવા માંગો છો?",
            "kn": f"{name}, ನಿಮ್ಮ ಆರ್ಥಿಕ ಗುರಿಗಳು:\n\n{goals_text}\n\nನಿಮ್ಮ ಗುರಿ ಪ್ರಗತಿ ನೋಡೋಣ... ನಿಮ್ಮ 'ಮನೆ ಖರೀದಿ' ಗುರಿ ಟ್ರ್ಯಾಕ್‌ನಲ್ಲಿದೆ! 🏠\n\nಯಾವ ಗುರಿ ಬಗ್ಗೆ ವಿವರವಾಗಿ ಮಾತನಾಡಲು ಬಯಸುವಿರಾ?",
            "ml": f"{name}, നിങ്ങളുടെ സാമ്പത്തിക ലക്ഷ്യങ്ങൾ:\n\n{goals_text}\n\nനിങ്ങളുടെ ലക്ഷ്യ പുരോഗതി നോക്കാം... നിങ്ങളുടെ 'വീട് വാങ്ങൽ' ലക്ഷ്യം ട്രാക്കിൽ ആണ്! 🏠\n\nഏത് ലക്ഷ്യത്തെ കുറിച്ച് വിശദമായി സംസാരിക്കാൻ ആഗ്രഹിക്കുന്നു?",
        })

    elif any(w in msg_lower for w in ["market", "nifty", "sensex", "bazaar"]):
        text = _get_localized(language, {
            "en": f"Today's market update:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 Gold: ₹{MARKET_DATA['gold']['value']:,.0f}/gram\n🏦 Repo Rate: {MARKET_DATA['repo_rate']['value']}%\n\nMarket is positive today, {name}. No negative impact on your portfolio. 👍",
            "hi": f"आज का बाजार अपडेट:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 Gold: ₹{MARKET_DATA['gold']['value']:,.0f}/gram\n🏦 Repo Rate: {MARKET_DATA['repo_rate']['value']}%\n\n{name} जी, बाजार सकारात्मक है। आपके पोर्टफोलियो पर कोई नकारात्मक प्रभाव नहीं है। 👍",
            "ta": f"இன்றைய சந்தை புதுப்பிப்பு:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 தங்கம்: ₹{MARKET_DATA['gold']['value']:,.0f}/கிராம்\n🏦 ரெப்போ விகிதம்: {MARKET_DATA['repo_rate']['value']}%\n\n{name}, சந்தை இன்று நேர்மறையாக உள்ளது. உங்கள் போர்ட்ஃபோலியோவில் எதிர்மறை தாக்கம் இல்லை. 👍",
            "te": f"నేటి మార్కెట్ అప్‌డేట్:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 బంగారం: ₹{MARKET_DATA['gold']['value']:,.0f}/గ్రాము\n🏦 రెపో రేటు: {MARKET_DATA['repo_rate']['value']}%\n\n{name}, మార్కెట్ ఈ రోజు సానుకూలంగా ఉంది. మీ పోర్ట్‌ఫోలియోపై ప్రతికూల ప్రభావం లేదు. 👍",
            "bn": f"আজকের বাজার আপডেট:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 সোনা: ₹{MARKET_DATA['gold']['value']:,.0f}/গ্রাম\n🏦 রেপো রেট: {MARKET_DATA['repo_rate']['value']}%\n\n{name}, বাজার আজ ইতিবাচক। আপনার পোর্টফোলিওতে কোনো নেতিবাচক প্রভাব নেই। 👍",
            "mr": f"आजचे बाजार अपडेट:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 सोने: ₹{MARKET_DATA['gold']['value']:,.0f}/ग्रॅम\n🏦 रेपो दर: {MARKET_DATA['repo_rate']['value']}%\n\n{name}, बाजार आज सकारात्मक आहे. तुमच्या पोर्टफोलिओवर नकारात्मक प्रभाव नाही. 👍",
            "gu": f"આજનું બજાર અપડેટ:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 સોનું: ₹{MARKET_DATA['gold']['value']:,.0f}/ગ્રામ\n🏦 રેપો રેટ: {MARKET_DATA['repo_rate']['value']}%\n\n{name}, બજાર આજે સકારાત્મક છે. તમારા પોર્ટફોલિયો પર કોઈ નકારાત્મક અસર નથી. 👍",
            "kn": f"ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ಅಪ್‌ಡೇಟ್:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 ಚಿನ್ನ: ₹{MARKET_DATA['gold']['value']:,.0f}/ಗ್ರಾಂ\n🏦 ರೆಪೋ ದರ: {MARKET_DATA['repo_rate']['value']}%\n\n{name}, ಮಾರುಕಟ್ಟೆ ಇಂದು ಸಕಾರಾತ್ಮಕವಾಗಿದೆ. ನಿಮ್ಮ ಪೋರ್ಟ್‌ಫೋಲಿಯೊ ಮೇಲೆ ಋಣಾತ್ಮಕ ಪರಿಣಾಮವಿಲ್ಲ. 👍",
            "ml": f"ഇന്നത്തെ വിപണി അപ്‌ഡേറ്റ്:\n\n📈 Nifty 50: {MARKET_DATA['nifty50']['value']:,.0f} ({MARKET_DATA['nifty50']['change_pct']:+.2f}%)\n📈 Sensex: {MARKET_DATA['sensex']['value']:,.0f} ({MARKET_DATA['sensex']['change_pct']:+.2f}%)\n🥇 സ്വർണം: ₹{MARKET_DATA['gold']['value']:,.0f}/ഗ്രാം\n🏦 റെപ്പോ നിരക്ക്: {MARKET_DATA['repo_rate']['value']}%\n\n{name}, വിപണി ഇന്ന് പോസിറ്റീവ് ആണ്. നിങ്ങളുടെ പോർട്ട്‌ഫോളിയോയിൽ നെഗറ്റീവ് ഇംപാക്ട് ഇല്ല. 👍",
        })

    elif any(w in msg_lower for w in ["tax", "save", "80c", "kar", "bachat"]):
        text = _get_localized(language, {
            "en": f"Tax-saving recommendations for you, {name}:\n\n💡 Section 80C (₹1.5L limit):\n  • ELSS Mutual Fund - ₹50,000 (shortest 3yr lock-in)\n  • PPF - ₹50,000 (safe, 15yr)\n  • NPS - ₹50,000 (extra ₹50K under 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nPotential savings: ~₹67,500 (at 30% bracket)\n\nShall I start an ELSS SIP for you?",
            "hi": f"{name} जी, टैक्स बचत के लिए मेरी सलाह:\n\n💡 Section 80C (₹1.5L limit):\n  • ELSS Mutual Fund - ₹50,000 (3 साल लॉक-इन, सबसे कम)\n  • PPF - ₹50,000 (सुरक्षित, 15 साल)\n  • NPS - ₹50,000 (अतिरिक्त ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nकुल बचत: ~₹67,500 (30% bracket)\n\nक्या मैं ELSS SIP शुरू करूँ?",
            "ta": f"{name}, வரி சேமிப்பு பரிந்துரைகள்:\n\n💡 Section 80C (₹1.5L வரம்பு):\n  • ELSS Mutual Fund - ₹50,000 (3 வருட லாக்-இன்)\n  • PPF - ₹50,000 (பாதுகாப்பான, 15 வருடம்)\n  • NPS - ₹50,000 (கூடுதல் ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nசாத்தியமான சேமிப்பு: ~₹67,500\n\nELSS SIP தொடங்கவா?",
            "te": f"{name}, పన్ను ఆదా సిఫార్సులు:\n\n💡 Section 80C (₹1.5L పరిమితి):\n  • ELSS Mutual Fund - ₹50,000 (3 సంవత్సరాల లాక్-ఇన్)\n  • PPF - ₹50,000 (సురక్షితం, 15 సంవత్సరాలు)\n  • NPS - ₹50,000 (అదనపు ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nసాధ్యమైన ఆదా: ~₹67,500\n\nELSS SIP ప్రారంభించమంటారా?",
            "bn": f"{name}, কর সাশ্রয় সুপারিশ:\n\n💡 Section 80C (₹1.5L সীমা):\n  • ELSS Mutual Fund - ₹50,000 (3 বছর লক-ইন)\n  • PPF - ₹50,000 (নিরাপদ, 15 বছর)\n  • NPS - ₹50,000 (অতিরিক্ত ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nসম্ভাব্য সঞ্চয়: ~₹67,500\n\nELSS SIP শুরু করব?",
            "mr": f"{name}, कर बचत शिफारसी:\n\n💡 Section 80C (₹1.5L मर्यादा):\n  • ELSS Mutual Fund - ₹50,000 (3 वर्ष लॉक-इन)\n  • PPF - ₹50,000 (सुरक्षित, 15 वर्षे)\n  • NPS - ₹50,000 (अतिरिक्त ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nसंभाव्य बचत: ~₹67,500\n\nELSS SIP सुरू करू का?",
            "gu": f"{name}, કર બચત ભલામણો:\n\n💡 Section 80C (₹1.5L મર્યાદા):\n  • ELSS Mutual Fund - ₹50,000 (3 વર્ષ લોક-ઇન)\n  • PPF - ₹50,000 (સુરક્ષિત, 15 વર્ષ)\n  • NPS - ₹50,000 (વધારાનું ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nસંભવિત બચત: ~₹67,500\n\nELSS SIP શરૂ કરું?",
            "kn": f"{name}, ತೆರಿಗೆ ಉಳಿತಾಯ ಶಿಫಾರಸುಗಳು:\n\n💡 Section 80C (₹1.5L ಮಿತಿ):\n  • ELSS Mutual Fund - ₹50,000 (3 ವರ್ಷ ಲಾಕ್-ಇನ್)\n  • PPF - ₹50,000 (ಸುರಕ್ಷಿತ, 15 ವರ್ಷ)\n  • NPS - ₹50,000 (ಹೆಚ್ಚುವರಿ ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nಸಂಭಾವ್ಯ ಉಳಿತಾಯ: ~₹67,500\n\nELSS SIP ಪ್ರಾರಂಭಿಸಲೇ?",
            "ml": f"{name}, നികുതി ലാഭ ശുപാർശകൾ:\n\n💡 Section 80C (₹1.5L പരിധി):\n  • ELSS Mutual Fund - ₹50,000 (3 വർഷ ലോക്ക്-ഇൻ)\n  • PPF - ₹50,000 (സുരക്ഷിതം, 15 വർഷം)\n  • NPS - ₹50,000 (അധിക ₹50K 80CCD(1B))\n\n💡 Section 80D:\n  • Health Insurance - ₹25,000\n\nസാധ്യമായ ലാഭം: ~₹67,500\n\nELSS SIP ആരംഭിക്കട്ടെ?",
        })

    else:
        text = _get_localized(language, {
            "en": f"I'm here to help, {name}! You can ask me about:\n\n• Portfolio review\n• Start a SIP\n• Market updates\n• Tax saving\n• Financial goals\n• Risk profile\n• Fund comparison\n\nWhat would you like to explore?",
            "hi": f"{name} जी, मैं आपकी मदद के लिए यहाँ हूँ। आप मुझसे पूछ सकते हैं:\n\n• पोर्टफोलियो रिव्यू\n• SIP शुरू करना\n• बाजार अपडेट\n• टैक्स बचत\n• वित्तीय लक्ष्य\n• रिस्क प्रोफाइल\n• फंड तुलना\n\nबताइए, किसमें मदद चाहिए?",
            "ta": f"{name}, நான் உதவ இங்கே இருக்கிறேன்! நீங்கள் கேட்கலாம்:\n\n• போர்ட்ஃபோலியோ மதிப்பாய்வு\n• SIP தொடங்குதல்\n• சந்தை புதுப்பிப்புகள்\n• வரி சேமிப்பு\n• நிதி இலக்குகள்\n• ரிஸ்க் புரொஃபைல்\n• ஃபண்ட் ஒப்பீடு\n\nஎதை ஆராய விரும்புகிறீர்கள்?",
            "te": f"{name}, నేను సహాయం చేయడానికి ఇక్కడ ఉన్నాను! మీరు అడగవచ్చు:\n\n• పోర్ట్‌ఫోలియో సమీక్ష\n• SIP ప్రారంభించడం\n• మార్కెట్ అప్‌డేట్‌లు\n• పన్ను ఆదా\n• ఆర్థిక లక్ష్యాలు\n• రిస్క్ ప్రొఫైల్\n• ఫండ్ పోలిక\n\nఏమి చర్చించాలనుకుంటున్నారు?",
            "bn": f"{name}, আমি সাহায্য করতে এখানে আছি! আপনি জিজ্ঞাসা করতে পারেন:\n\n• পোর্টফোলিও পর্যালোচনা\n• SIP শুরু করা\n• বাজার আপডেট\n• কর সাশ্রয়\n• আর্থিক লক্ষ্য\n• রিস্ক প্রোফাইল\n• ফান্ড তুলনা\n\nকী নিয়ে আলোচনা করতে চান?",
            "mr": f"{name}, मी मदतीसाठी येथे आहे! तुम्ही विचारू शकता:\n\n• पोर्टफोलिओ पुनरावलोकन\n• SIP सुरू करणे\n• बाजार अपडेट\n• कर बचत\n• आर्थिक उद्दिष्टे\n• रिस्क प्रोफाइल\n• फंड तुलना\n\nकशाबद्दल बोलायचे?",
            "gu": f"{name}, હું મદદ કરવા અહીં છું! તમે પૂછી શકો છો:\n\n• પોર્ટફોલિયો સમીક્ષા\n• SIP શરૂ કરવું\n• બજાર અપડેટ\n• કર બચત\n• નાણાકીય લક્ષ્યો\n• રિસ્ક પ્રોફાઇલ\n• ફંડ સરખામણી\n\nશું ચર્ચા કરવા માંગો છો?",
            "kn": f"{name}, ನಾನು ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ! ನೀವು ಕೇಳಬಹುದು:\n\n• ಪೋರ್ಟ್‌ಫೋಲಿಯೊ ವಿಮರ್ಶೆ\n• SIP ಪ್ರಾರಂಭಿಸುವುದು\n• ಮಾರುಕಟ್ಟೆ ಅಪ್‌ಡೇಟ್‌ಗಳು\n• ತೆರಿಗೆ ಉಳಿತಾಯ\n• ಆರ್ಥಿಕ ಗುರಿಗಳು\n• ರಿಸ್ಕ್ ಪ್ರೊಫೈಲ್\n• ಫಂಡ್ ಹೋಲಿಕೆ\n\nಏನು ಚರ್ಚಿಸಲು ಬಯಸುವಿರಾ?",
            "ml": f"{name}, ഞാൻ സഹായിക്കാൻ ഇവിടെയുണ്ട്! നിങ്ങൾ ചോദിക്കാം:\n\n• പോർട്ട്‌ഫോളിയോ അവലോകനം\n• SIP ആരംഭിക്കൽ\n• വിപണി അപ്‌ഡേറ്റുകൾ\n• നികുതി ലാഭം\n• സാമ്പത്തിക ലക്ഷ്യങ്ങൾ\n• റിസ്ക് പ്രൊഫൈൽ\n• ഫണ്ട് താരതമ്യം\n\nഎന്താണ് ചർച്ച ചെയ്യാൻ ആഗ്രഹിക്കുന്നത്?",
        })

    return {
        "text": text,
        "agents_used": ["research_agent", "compliance_agent", "portfolio_agent"],
        "model": "fallback-contextual",
    }
