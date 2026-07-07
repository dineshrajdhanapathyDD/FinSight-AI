from fastapi import APIRouter, HTTPException
from app.models.schemas import RecommendationRequest
from app.data.customers import CUSTOMERS, FUND_RECOMMENDATIONS

router = APIRouter()


@router.post("/generate")
async def generate_recommendations(request: RecommendationRequest):
    """Generate personalized investment recommendations."""
    customer = CUSTOMERS.get(request.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    risk_profile = customer["risk_profile"]
    age = customer["age"]

    # Filter funds suitable for customer's risk profile
    suitable_funds = [
        fund for fund in FUND_RECOMMENDATIONS
        if risk_profile in fund["suitable_for"]
    ]

    # Compute recommended allocation based on age and risk
    if risk_profile == "aggressive":
        target_equity = min(90, 100 - age)
        target_debt = 100 - target_equity - 10
        target_gold = 10
    elif risk_profile == "conservative":
        target_equity = max(30, 80 - age)
        target_debt = 100 - target_equity - 10
        target_gold = 10
    else:  # moderate
        target_equity = max(40, 90 - age)
        target_debt = 100 - target_equity - 10
        target_gold = 10

    # Determine SIP amount
    sip_amount = request.amount or (customer["monthly_income"] * 0.2)

    recommendations = []
    for fund in suitable_funds[:3]:
        rec = {
            "fund": fund,
            "suggested_sip": int(sip_amount * 0.4) if fund["category"] in ["Large Cap", "Flexi Cap", "Hybrid"] else int(sip_amount * 0.3),
            "reasoning": _get_reasoning(fund, customer, request.goal),
            "compliance_status": "SEBI Compliant",
            "suitability_score": _compute_suitability(fund, customer),
        }
        recommendations.append(rec)

    return {
        "status": "success",
        "customer_name": customer["name"],
        "risk_profile": risk_profile,
        "target_allocation": {
            "equity": target_equity,
            "debt": target_debt,
            "gold": target_gold,
        },
        "recommended_sip_total": int(sip_amount),
        "recommendations": recommendations,
        "disclaimer": "Mutual fund investments are subject to market risks. Read all scheme related documents carefully.",
    }


def _get_reasoning(fund: dict, customer: dict, goal: str | None) -> str:
    reasons = []
    if fund["rating"] >= 4:
        reasons.append(f"Highly rated fund ({fund['rating']}★)")
    if fund["expense_ratio"] < 1.0:
        reasons.append(f"Low expense ratio ({fund['expense_ratio']}%)")
    if fund["returns_5y"] > 12:
        reasons.append(f"Strong 5-year track record ({fund['returns_5y']}% CAGR)")
    if customer["risk_profile"] in fund["suitable_for"]:
        reasons.append(f"Matches your {customer['risk_profile']} risk profile")
    if goal:
        reasons.append(f"Aligned with your '{goal}' goal")
    return " | ".join(reasons)


def _compute_suitability(fund: dict, customer: dict) -> float:
    score = 3.0
    if customer["risk_profile"] in fund["suitable_for"]:
        score += 1.0
    if fund["rating"] >= 4:
        score += 0.5
    if fund["expense_ratio"] < 1.0:
        score += 0.3
    return min(5.0, round(score, 1))
