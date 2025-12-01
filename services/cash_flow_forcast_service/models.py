from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CashFlowInput(BaseModel):
    user_id: str
    monthly_income_usd: float
    monthly_expenses_usd: float
    monthly_emi_usd: float
    savings_usd: float
    record_date: datetime

class CashFlowPrediction(BaseModel):
    user_id: str
    net_cashflow: float
    cashflow_risk: int
    risk_level: str  # "low" or "high"
    confidence: float
    timestamp: datetime

# class FinancialHealthReport(BaseModel):
#     user_id: str
#     net_cashflow: float
#     risk_category: str
#     recommendations: list[str]
#     forecast_date: datetime