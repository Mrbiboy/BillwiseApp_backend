from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid


class Account(Base):
    __tablename__ = "account"

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    balance = Column(Numeric(15, 2), default=0)
    currency = Column(String(3), nullable=False)

    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id"))
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(String(10), nullable=False)
    description = Column(String)
    transaction_date = Column(DateTime, server_default=func.now())

    account = relationship("Account", back_populates="transactions")
