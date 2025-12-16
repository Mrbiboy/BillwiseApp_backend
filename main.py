# backend/main.py
from fastapi import FastAPI

app = FastAPI(title="BillWise Test API")

@app.get("/api/health")
def health_check():
    """
    Endpoint minimal pour tester le déploiement
    """
    return {
        "status": "healthy",
        "service": "billwise-test",
        "version": "0.1.0"
    }
