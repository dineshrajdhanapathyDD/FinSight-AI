from fastapi import APIRouter, HTTPException
from app.models.schemas import PortfolioRequest
from app.data.customers import CUSTOMERS, MARKET_DATA

router = APIRouter()


@router.get("/market")
async def get_market_data():
    """Get current market overview."""
    return {"status": "success", "data": MARKET_DATA}


@router.get("/{customer_id}")
async def get_portfolio(customer_id: str):
    """Get customer portfolio details."""
    customer = CUSTOMERS.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "status": "success",
        "customer": {
            "name": customer["name"],
            "risk_profile": customer["risk_profile"],
        },
        "portfolio": customer["portfolio"],
        "goals": customer["goals"],
    }


@router.get("/{customer_id}/analysis")
async def get_portfolio_analysis(customer_id: str):
    """Get AI-generated portfolio analysis."""
    customer = CUSTOMERS.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    portfolio = customer["portfolio"]
    allocation = portfolio["allocation"]

    # Simple rule-based analysis for MVP
    analysis = {
        "health_score": 78,
        "strengths": [],
        "concerns": [],
        "suggestions": [],
    }

    # Check diversification
    if allocation["equity"] > 70:
        analysis["concerns"].append("High equity concentration - consider adding debt for stability")
    elif allocation["equity"] < 30 and customer["age"] < 45:
        analysis["concerns"].append("Low equity allocation for your age - missing growth potential")
    else:
        analysis["strengths"].append("Good equity-debt balance for your risk profile")

    # Check gold allocation
    if allocation.get("gold", 0) > 0:
        analysis["strengths"].append("Gold allocation provides inflation hedge")
    else:
        analysis["suggestions"].append("Consider 5-10% gold allocation for portfolio protection")

    # Check returns
    if portfolio["returns_pct"] > 12:
        analysis["strengths"].append(f"Strong returns of {portfolio['returns_pct']}% - outperforming inflation significantly")

    # Goal gap analysis
    for goal in customer["goals"]:
        monthly_needed = goal["target"] / (goal["timeline_years"] * 12)
        total_sip = sum(h["sip_amount"] for h in portfolio["holdings"])
        if total_sip < monthly_needed * 0.8:
            analysis["suggestions"].append(
                f"Increase SIP by ₹{int(monthly_needed - total_sip):,} to meet '{goal['name']}' goal"
            )

    analysis["health_score"] = min(100, 60 + len(analysis["strengths"]) * 10 - len(analysis["concerns"]) * 8)

    return {"status": "success", "analysis": analysis}
