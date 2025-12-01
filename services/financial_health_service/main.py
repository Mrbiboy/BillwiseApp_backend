# financial_health_service/main.py
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import from your services module
try:
    from services import FinancialHealthService
    from schemas import FinancialHealthRequest, FinancialHealthResponse
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    # Alternative import if the above fails
    import importlib.util
    spec = importlib.util.spec_from_file_location("services", current_dir / "services.py")
    services_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(services_module)
    FinancialHealthService = services_module.FinancialHealthService
    
    spec = importlib.util.spec_from_file_location("schemas", current_dir / "schemas.py")
    schemas_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schemas_module)
    FinancialHealthRequest = schemas_module.FinancialHealthRequest
    FinancialHealthResponse = schemas_module.FinancialHealthResponse

app = FastAPI(
    title="Financial Health Service",
    description="Predicts financial health score based on user data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
try:
    service = FinancialHealthService()
    print("✅ Financial Health Service loaded successfully")
except Exception as e:
    print(f"❌ Failed to load Financial Health Service: {str(e)}")
    service = None

@app.post("/predict", response_model=FinancialHealthResponse)
async def predict_financial_health(request: FinancialHealthRequest):
    """
    Predict financial health score based on user financial data
    """
    if service is None:
        raise HTTPException(
            status_code=503, 
            detail="Service is not available. Check if model files are present."
        )
    
    try:
        # Convert Pydantic model to dict
        data = request.dict()
        
        # Get prediction
        result = service.predict(data)
        
        return FinancialHealthResponse(
            financial_score=result["financial_score"],
            status=result["status"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if service:
        return {
            "status": "healthy", 
            "service": "financial_health_service",
            "model_loaded": True
        }
    return {
        "status": "unhealthy",
        "service": "financial_health_service",
        "model_loaded": False
    }

@app.get("/")
async def root():
    return {
        "message": "Financial Health Service",
        "endpoints": {
            "POST /predict": "Predict financial health score",
            "GET /health": "Service health check"
        }
    }