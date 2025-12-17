from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from models import Account, Transaction


def get_account(db: Session, user_id: UUID):
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        account = Account(user_id=user_id, balance=Decimal("0"))
        db.add(account)
        db.commit()
        db.refresh(account)
    return account


def add_balance(db: Session, user_id: UUID, amount: float, description="Top Up"):
    account = get_account(db, user_id)
    account.balance += Decimal(str(amount))

    tx = Transaction(
        account_id=account.account_id, amount=Decimal(str(amount)), type="credit", description=description    # "topup" → "credit"
    )

    db.add(tx)
    db.commit()
    db.refresh(account)
    return account


def deduct_balance(db: Session, user_id: UUID, amount: float, description="Payment"):
    account = get_account(db, user_id)

    if account.balance < Decimal(str(amount)):
        raise Exception("Insufficient balance")

    account.balance -= Decimal(str(amount))

    tx = Transaction(
        account_id=account.account_id, amount=Decimal(str(amount)), type="debit", description=description     # "payment" → "debit"
    )

    db.add(tx)
    db.commit()
    db.refresh(account)
    return account

