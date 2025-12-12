from fastapi import FastAPI
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PaymentRequest(BaseModel):
    amount: float


@app.post("/create-payment-intent")
def create_payment_intent(data: PaymentRequest):

    intent = stripe.PaymentIntent.create(
        amount=int(data.amount * 100),  # cents
        currency="usd",
        payment_method_types=["card"],
    )

    return {"clientSecret": intent.client_secret}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8086)
