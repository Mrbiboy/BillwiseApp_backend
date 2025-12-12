from pydantic import BaseModel
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Numeric, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from database.database import Base


class CashFlowPredictionDB(Base):
    __tablename__ = "cash_flow_prediction"

    prediction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    predicted_income = Column(Numeric(15, 2))
    predicted_expenses = Column(Numeric(15, 2))
    predicted_balance = Column(Numeric(15, 2))
    confidence = Column(Numeric(5, 2))

    prediction_date = Column(TIMESTAMP, nullable=False)


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
    risk_level: str
    confidence: float
    timestamp: datetime
