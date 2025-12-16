"""
Shared database configuration for all services
This is the ONLY shared component for database connectivity
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from datetime import datetime

# Database URL from environment variables
DATABASE_URL="postgresql://avnadmin:AVNS_wAl_C8tHEBkCA4cIWbO@pg-3197ed6b-uca-f390.g.aivencloud.com:12654/defaultdb?sslmode=require"

# Fix for Heroku/some providers that use 'postgres://' instead of 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


print("database.py: URl: ",DATABASE_URL)

# Create SQLAlchemy engine with UTF-8 encoding support
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max overflow connections
    connect_args={
        "options": "-c client_encoding=UTF8"
    },
    echo=False  # Set to True for SQL debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models (each service can have its own Base)
Base = declarative_base()

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_prediction(db: Session, prediction_data: dict):
    from services.cash_flow_forcast_service.models import CashFlowPredictionDB
    record = CashFlowPredictionDB(
        user_id=prediction_data['user_id'],
        predicted_income=prediction_data['predicted_income'],
        predicted_expenses=prediction_data['predicted_expenses'],
        predicted_balance=prediction_data['predicted_balance'],
        confidence=prediction_data['confidence'],
        prediction_date=prediction_data["timestamp"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record