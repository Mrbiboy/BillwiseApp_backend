import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from sqlalchemy.orm import Session
from database.database import get_db
from models import Recommendation
from schemas import RecommendationRequest, RecommendationResponse
from etf_advisor_engine import get_recommendation
from datetime import datetime

app = FastAPI(
    title="ETF Long-Term Advisor API",
    description="Smart 2-year ETF allocation powered by machine learning",
    version="1.0"
)

# ============ ADD THIS CORS CONFIGURATION ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


# 1. Preview: Get recommendation WITHOUT saving to DB
@app.post("/preview", response_model=RecommendationResponse)
async def preview_recommendation(request: RecommendationRequest):
    try:
        result = get_recommendation(amount=request.amount_eur)

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
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


# 2. Confirm: Get recommendation AND save to database
@app.post("/confirm", response_model=RecommendationResponse)
async def confirm_recommendation(request: RecommendationRequest, db: Session = Depends(get_db)):
    try:
        result = get_recommendation(amount=request.amount_eur)

        # Save to your existing Recommendation table
        db_rec = Recommendation(
            user_id=request.user_id,
            amount_eur=request.amount_eur,
            portfolio=result["allocations"],                    # JSON list of dicts
            expected_2y_return=result["expected_2y_return"],
            strategy=result["strategy"],
            recommendation_date=datetime.utcnow()               # Explicitly set (or rely on default)
        )
        db.add(db_rec)
        db.commit()
        db.refresh(db_rec)

        # Return the same clean response as preview
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
        db.rollback()  # Important: rollback on error
        raise HTTPException(status_code=500, detail=f"Confirmation failed: {str(e)}")


# Optional: View user's investment history
@app.get("/history/{user_id}")
def get_history(user_id: str, db: Session = Depends(get_db)):
    recs = db.query(Recommendation)\
        .filter(Recommendation.user_id == user_id)\
        .order_by(Recommendation.recommendation_date.desc())\
        .all()
    return recs


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)