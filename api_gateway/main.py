import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Base, engine

from services.wallet_service.router import router as wallet_router
from services.auth_service.router import router as auth_router
from services.bill_service.router import router as bill_router
from services.sms_parser_service.router import router as sms_parser_router
from services.cash_flow_forcast_service.router import router as cashflow_router
#from services.ETF_Recommendation.router import router as etf_router

app = FastAPI(
    title="BillWise App Backend",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(bill_router)
app.include_router(sms_parser_router)
app.include_router(cashflow_router)
#app.include_router(etf_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
