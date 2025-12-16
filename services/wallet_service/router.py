import sys
from pathlib import Path
from uuid import UUID

# Add project root to path to enable imports like `database.database`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from service import get_account, add_balance, deduct_balance
from schemas import TopUpRequest, PaymentRequest

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/")
def get_wallet(user_id: UUID, db: Session = Depends(get_db)):
    account = get_account(db, user_id)
    return {"balance": float(account.balance)}


@router.post("/topup")
def topup_wallet(data: TopUpRequest, user_id: UUID, db: Session = Depends(get_db)):
    account = add_balance(db, user_id, data.amount)
    return {"message": "Wallet topped up", "balance": float(account.balance)}


@router.post("/pay")
def pay_from_wallet(data: PaymentRequest, user_id: UUID, db: Session = Depends(get_db)):
    account = deduct_balance(db, user_id, data.amount)
    return {"message": "Payment successful", "balance": float(account.balance)}
