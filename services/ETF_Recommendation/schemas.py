# services/Model_ETF/schemas.py

from pydantic import BaseModel
from typing import List
from datetime import date


class AllocationItem(BaseModel):
    ETF: str
    forecast_2y: float
    weight: float
    amount_eur: int
    reason: str


class RecommendationResponse(BaseModel):
    date: date
    total_amount: float
    strategy: str
    expected_2y_return: float
    allocations: List[AllocationItem]
    note: str = "Recommendation valid for the entire month"


class RecommendationRequest(BaseModel):
    user_id: str
    amount_eur: float