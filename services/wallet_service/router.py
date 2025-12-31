import os
import sys
from pathlib import Path
from uuid import UUID

# Add project root to path to enable imports like `database.database`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from service import get_account, add_balance, deduct_balance
from schemas import TopUpRequest, PaymentRequest
import stripe
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe.webhook_key = os.getenv("STRIPE_WEBHOOK_SECRET")
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


@router.post("/create-checkout")
def create_checkout_session(amount: float, user_id: UUID):
    # Stripe requires minimum of $0.50 for checkout sessions
    if amount < 0.50:
        raise HTTPException(status_code=400, detail="Minimum top-up amount is $0.50")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Wallet Top-Up"},
                    "unit_amount": int(Decimal(str(amount)) * 100),
                },
                "quantity": 1,
            }
        ],
        metadata={"user_id": str(user_id)},
        success_url="http://localhost:8081/wallet?success=true",
        cancel_url="http://localhost:8081/wallet?canceled=true",
    )

    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(payload, sig, stripe.webhook_key)

    if event["type"] == "checkout.session.completed":
        intent = event["data"]["object"]

        user_id = UUID(intent["metadata"]["user_id"])
        amount = intent["amount"] / 100

        add_balance(db=db, user_id=user_id, amount=amount, description="Stripe wallet top-up")

    return {"status": "ok"}
