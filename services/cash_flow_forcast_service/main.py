from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
from datetime import datetime

from models import CashFlowInput, CashFlowPrediction
from prediction import CashFlowPredictor
from database import get_db, save_prediction

app = FastAPI(title="BillWise Cash Flow Forecast API", version="1.0.0")

# CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
predictor = CashFlowPredictor()

@app.get("/")
async def root():
    return {"message": "BillWise Cash Flow Forecast Service"}

@app.post("/predict-cashflow", response_model=CashFlowPrediction)
async def predict_cashflow(input_data: CashFlowInput):
    """Predict cash flow and risk for a user"""
    try:
        # Convert to dict for processing
        input_dict = input_data.dict()
        
        # Make prediction
        prediction = predictor.predict(input_dict)
        
        # Prepare response
        response = CashFlowPrediction(
            user_id=input_data.user_id,
            net_cashflow=prediction['net_cashflow'],
            cashflow_risk=prediction['cashflow_risk'],
            risk_level=prediction['risk_level'],
            confidence=prediction['risk_probability'],
            timestamp=datetime.utcnow()
        )
        
        # Save to database (optional)
        # await save_prediction(response.dict())
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# @app.post("/financial-health/{user_id}", response_model=FinancialHealthReport)
# async def get_financial_health(user_id: str, input_data: CashFlowInput):
#     """Generate comprehensive financial health report"""
#     prediction = await predict_cashflow(input_data)
    
#     # Generate recommendations based on prediction
#     recommendations = generate_recommendations(prediction, input_data)
    
#     return FinancialHealthReport(
#         user_id=user_id,
#         net_cashflow=prediction.net_cashflow,
#         risk_category=prediction.risk_level,
#         recommendations=recommendations,
#         forecast_date=datetime.utcnow()
#     )

@app.get("/user-history/{user_id}")
async def get_user_prediction_history(user_id: str):
    """Get prediction history for a user"""
    # Implement database query
    return {"user_id": user_id, "history": []}

# def generate_recommendations(prediction: CashFlowPrediction, input_data: CashFlowInput) -> List[str]:
#     """Generate personalized financial recommendations"""
#     recommendations = []
    
#     if prediction.risk_level == "high":
#         recommendations.extend([
#             "Consider reducing discretionary spending",
#             "Explore options to refinance high-interest loans",
#             "Build emergency savings buffer",
#             "Review subscription services and recurring payments"
#         ])
#     else:
#         recommendations.extend([
#             "Maintain current spending habits",
#             "Consider investing surplus cash flow",
#             "Continue building savings for long-term goals"
#         ])
    
#     # Expense-specific recommendations
#     expense_ratio = input_data.monthly_expenses_usd / input_data.monthly_income_usd
#     if expense_ratio > 0.7:
#         recommendations.append("Your expense-to-income ratio is high - consider budgeting")
    
#     return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)