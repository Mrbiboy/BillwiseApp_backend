# services/Model_ETF/models.py

import sys
from pathlib import Path

# Fix import path so Python can find ../../database/database.py
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from database.database import Base
from datetime import datetime


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    amount_eur = Column(Float, nullable=False)
    recommendation_date = Column(DateTime, default=datetime.utcnow, index=True)
    portfolio = Column(JSON, nullable=False)           # List of dicts with allocation
    expected_2y_return = Column(Float)                 # Best forecasted 2Y return
    strategy = Column(String, nullable=False)          # concentrated / diversified / safe

    def __repr__(self):
        return f"<Recommendation user={self.user_id} amount=€{self.amount_eur}>"