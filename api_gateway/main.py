from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.wallet_service.router import router as wallet_router
# later: auth_router, users_router, etc.

app = FastAPI(title="BillWise App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wallet_router)

@app.get("/")
def health():
    return {"status": "ok"}
