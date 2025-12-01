# financial_health_service/services.py
import os
import pandas as pd
import joblib
from typing import Dict, Any

BASE_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(BASE_DIR, "financial_health_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "financial_health_scaler.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "financial_health_encoders.pkl")

class FinancialHealthService:
    def __init__(self):
        """Initialize the service by loading model, scaler, and encoders"""
        try:
            # Check if model files exist
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
            if not os.path.exists(SCALER_PATH):
                raise FileNotFoundError(f"Scaler file not found: {SCALER_PATH}")
            if not os.path.exists(ENCODERS_PATH):
                raise FileNotFoundError(f"Encoders file not found: {ENCODERS_PATH}")
            
            # Load the model components
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            self.encoders = joblib.load(ENCODERS_PATH)
            
            print(f"✅ Model loaded successfully")
            print(f"   Model: {type(self.model).__name__}")
            print(f"   Features expected: {self.model.n_features_in_ if hasattr(self.model, 'n_features_in_') else 'Unknown'}")
            
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            raise

    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict financial health score
        
        Args:
            data: Dictionary containing user financial data
            
        Returns:
            Dictionary with financial_score and status
        """
        try:
            # Create DataFrame from input data
            df = pd.DataFrame([data])
            
            # Encode categorical variables
            for col in ['employment_status', 'region', 'gender', 'education_level']:
                if col in self.encoders:
                    le = self.encoders[col]
                    # Handle unseen categories
                    if df[col].iloc[0] not in le.classes_:
                        print(f"⚠️ Unknown category '{df[col].iloc[0]}' for {col}, using default")
                        df[col] = le.transform([le.classes_[0]])[0]
                    else:
                        df[col] = le.transform(df[col])
                else:
                    print(f"⚠️ No encoder found for {col}")
                    df[col] = 0
            
            # Scale features
            X_scaled = self.scaler.transform(df)
            
            # Make prediction
            score = round(float(self.model.predict(X_scaled)[0]), 1)
            
            # Determine status
            if score < 50:
                status = "Critical"
            elif score < 70:
                status = "Fragile"
            elif score < 85:
                status = "Stable"
            else:
                status = "Thriving"
            
            return {
                "financial_score": score,
                "status": status,
                "details": {
                    "range": "0-100",
                    "interpretation": f"Score of {score} indicates {status} financial health"
                }
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            raise