"""Email OTP authentication endpoints."""
import random
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# In-memory OTP store (use DynamoDB/Redis in production)
otp_store: dict = {}

# Try AWS SES for real email delivery
try:
    import boto3
    ses_client = boto3.client("ses", region_name=settings.aws_region)
    SES_AVAILABLE = True
except Exception:
    SES_AVAILABLE = False


class OtpRequest(BaseModel):
    email: str


class OtpVerify(BaseModel):
    email: str
    otp: str


@router.post("/send-otp")
async def send_otp(request: OtpRequest):
    """Generate and send OTP to email."""
    email = request.email.lower().strip()

    # Generate 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    otp_store[email] = {"code": otp_code, "created_at": time.time(), "attempts": 0}

    # Try sending via AWS SES
    email_sent = False
    if SES_AVAILABLE and settings.aws_access_key_id:
        try:
            ses_client.send_email(
                Source="noreply@finsight-ai.demo",
                Destination={"ToAddresses": [email]},
                Message={
                    "Subject": {"Data": "FinSight AI - Your OTP Code"},
                    "Body": {
                        "Html": {
                            "Data": f"""
                            <div style="font-family: Arial; max-width: 400px; margin: 0 auto; padding: 20px;">
                                <h2 style="color: #00857C;">FinSight AI - Dhan Sakhi</h2>
                                <p>Your one-time password is:</p>
                                <div style="background: #FEF3E8; border: 2px solid #E87722; border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0;">
                                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #E87722;">{otp_code}</span>
                                </div>
                                <p style="color: #666; font-size: 12px;">This code expires in 5 minutes. Do not share it with anyone.</p>
                                <p style="color: #00857C; font-size: 12px;">IDBI Bank | Digital Wealth Management</p>
                            </div>
                            """
                        }
                    },
                },
            )
            email_sent = True
        except Exception as e:
            print(f"SES send failed: {e}")
            email_sent = False

    return {
        "status": "sent",
        "email": email,
        "email_delivered": email_sent,
        "otp_hint": otp_code,  # Show in UI for demo (remove in production)
        "message": "OTP sent successfully" if email_sent else "OTP generated (demo mode - shown in UI)",
        "expires_in": 300,
    }


@router.post("/verify-otp")
async def verify_otp(request: OtpVerify):
    """Verify OTP code."""
    email = request.email.lower().strip()
    otp_data = otp_store.get(email)

    if not otp_data:
        raise HTTPException(status_code=400, detail="No OTP found. Please request a new one.")

    # Check expiry (5 minutes)
    if time.time() - otp_data["created_at"] > 300:
        del otp_store[email]
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one.")

    # Check attempts (max 5)
    if otp_data["attempts"] >= 5:
        del otp_store[email]
        raise HTTPException(status_code=429, detail="Too many attempts. Please request a new OTP.")

    otp_data["attempts"] += 1

    # Verify (accept actual OTP or universal demo code)
    if request.otp == otp_data["code"] or request.otp == "123456":
        del otp_store[email]
        return {
            "verified": True,
            "email": email,
            "message": "Authentication successful",
        }
    else:
        return {
            "verified": False,
            "message": f"Invalid OTP. {5 - otp_data['attempts']} attempts remaining.",
        }
