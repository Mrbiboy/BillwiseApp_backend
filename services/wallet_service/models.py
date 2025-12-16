from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Account(Base):
    __tablename__ = "account"

    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)
    balance = Column(Numeric(10,2), default=0)

    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("account.account_id"))
    amount = Column(Numeric(10,2), nullable=False)
    type = Column(String(20), nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    account = relationship("Account", back_populates="transactions")
