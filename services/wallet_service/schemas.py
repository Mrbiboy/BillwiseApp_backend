from pydantic import BaseModel


class WalletResponse(BaseModel):
    balance: float


class TopUpRequest(BaseModel):
    amount: float


class PaymentRequest(BaseModel):
    amount: float
#    bill_id: int
