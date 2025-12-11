# services/Model_ETF/main.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models import Recommendation
from schemas import RecommendationRequest, RecommendationResponse
from etf_advisor_engine import get_recommendation

app = FastAPI(
    title="ETF Long-Term Advisor API",
    description="Smart 2-year ETF allocation powered by machine learning",
    version="1.0"
)


@app.post("/recommend", response_model=RecommendationResponse)
async def create_recommendation(request: RecommendationRequest, db: Session = Depends(get_db)):
    try:
        result = get_recommendation(amount=request.amount_eur)

        # Save to database
        db_rec = Recommendation(
            user_id=request.user_id,
            amount_eur=request.amount_eur,
            portfolio=result["allocations"],
            expected_2y_return=result["expected_2y_return"],
            strategy=result["strategy"]
        )
        db.add(db_rec)
        db.commit()
        db.refresh(db_rec)

        # Return clean response
        return RecommendationResponse(
            date=result["date"],
            total_amount=result["total_amount"],
            strategy=result["strategy"],
            expected_2y_return=result["expected_2y_return"],
            allocations=[
                {
                    "ETF": item["ETF"],
                    "forecast_2y": item["forecast_2y"],
                    "weight": item["Weight"],
                    "amount_eur": item["Amount_EUR"],
                    "reason": item["reason"]
                }
                for item in result["allocations"]
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.get("/")
def home():
    return {"message": "ETF Advisor API is alive – POST to /recommend with user_id & amount_eur"}


# Optional: get user's history
@app.get("/history/{user_id}")
def get_history(user_id: str, db: Session = Depends(get_db)):
    recs = db.query(Recommendation).filter(Recommendation.user_id == user_id).order_by(Recommendation.recommendation_date.desc()).all()
    return recs


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)