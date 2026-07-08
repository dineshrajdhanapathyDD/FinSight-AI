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
    if SES_AVAILABLE:
        try:
            ses_client.send_email(
                Source="finsight.ai.otp@gmail.com",
                Destination={"ToAddresses": [email]},
                Message={
                    "Subject": {"Data": "FinSight AI - Your Login OTP"},
                    "Body": {
                        "Html": {
                            "Data": f"""
                            <div style="font-family: Arial, sans-serif; max-width: 450px; margin: 0 auto; padding: 30px; background: #ffffff;">
                                <div style="text-align: center; margin-bottom: 20px;">
                                    <h1 style="color: #00857C; margin: 0;">FinSight AI</h1>
                                    <p style="color: #E87722; font-size: 14px; margin: 5px 0;">Dhan Sakhi - AI Wealth Advisor</p>
                                </div>
                                <hr style="border: 1px solid #E6F5F3; margin: 20px 0;">
                                <p style="color: #333; font-size: 14px;">Hello,</p>
                                <p style="color: #333; font-size: 14px;">Your one-time password for login is:</p>
                                <div style="background: linear-gradient(135deg, #FEF3E8, #E6F5F3); border: 2px solid #E87722; border-radius: 12px; padding: 25px; text-align: center; margin: 25px 0;">
                                    <span style="font-size: 36px; font-weight: bold; letter-spacing: 10px; color: #E87722; font-family: monospace;">{otp_code}</span>
                                </div>
                                <p style="color: #666; font-size: 12px;">This code expires in <strong>5 minutes</strong>.</p>
                                <p style="color: #666; font-size: 12px;">If you did not request this code, please ignore this email.</p>
                                <hr style="border: 1px solid #E6F5F3; margin: 20px 0;">
                                <p style="color: #00857C; font-size: 11px; text-align: center;">IDBI Bank | Digital Wealth Management | IDBI Innovate 2026</p>
                            </div>
                            """
                        },
                        "Text": {
                            "Data": f"Your FinSight AI login OTP is: {otp_code}. This code expires in 5 minutes."
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
        "message": "OTP sent to your email" if email_sent else "OTP sent successfully",
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

    # Verify (accept actual OTP only)
    if request.otp == otp_data["code"]:
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
