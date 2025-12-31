from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from services.cash_flow_forcast_service.models import CashFlowInput, CashFlowPrediction
from services.cash_flow_forcast_service.models import CashFlowPredictionDB
from services.cash_flow_forcast_service.prediction import CashFlowPredictor
from database.database import get_db
from database.database import save_prediction

router = APIRouter(prefix="/api/cashflow", tags=["CashFlowForecast"])


predictor = CashFlowPredictor()


@router.get("/")
async def root():
    return {"message": "BillWise Cash Flow Forecast Service"}


@router.post("/predict-cashflow", response_model=CashFlowPrediction)
async def predict_cashflow(input_data: CashFlowInput, db: Session = Depends(get_db)):
    try:
        pred = predictor.predict(input_data.dict())

        response = CashFlowPrediction(
            user_id=input_data.user_id,
            net_cashflow=pred["net_cashflow"],
            cashflow_risk=pred["cashflow_risk"],
            risk_level=pred["risk_level"],
            confidence=pred["risk_probability"],
            timestamp=datetime.utcnow(),
        )

        # Save to DB
        save_prediction(
            db,
            {
                "user_id": input_data.user_id,
                "predicted_income": input_data.monthly_income_usd,
                "predicted_expenses": input_data.monthly_expenses_usd,
                "predicted_balance": pred["net_cashflow"],
                "confidence": pred["risk_probability"],
                "timestamp": response.timestamp,
            },
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.get("/user-history/{user_id}")
async def get_user_prediction_history(user_id: str, db: Session = Depends(get_db)):
    records = (
        db.query(CashFlowPredictionDB)
        .filter(CashFlowPredictionDB.user_id == user_id)
        .order_by(CashFlowPredictionDB.prediction_date.desc())
        .all()
    )

    return [
        {
            "prediction_id": str(r.prediction_id),
            "income": float(r.predicted_income),
            "expenses": float(r.predicted_expenses),
            "balance": float(r.predicted_balance),
            "confidence": float(r.confidence),
            "date": r.prediction_date,
        }
        for r in records
    ]
