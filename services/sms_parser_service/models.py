from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database.database import Base

class Account(Base):
    """User account to track bills and transactions"""
    __tablename__ = "account"
    
    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    currency = Column(String(3), default='DH')
    
    # Relationships
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="account", cascade="all, delete-orphan")

class Transaction(Base):
    """Stores transaction extracted from SMS"""
    __tablename__ = "transaction"
    
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('account.account_id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(String(10), nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    category = Column(String(100))
    merchant = Column(String(255))
    source = Column(String(50))
    description = Column(Text)
    
    # Relationship
    account = relationship("Account", back_populates="transactions")
    bill = relationship("Bill", back_populates="transaction", uselist=False)
    
    __table_args__ = (
        CheckConstraint("type IN ('debit', 'credit')", name='check_transaction_type'),
        CheckConstraint("source IN ('sms', 'manual')", name='check_transaction_source'),
    )

class Bill(Base):
    """Stores bills extracted from SMS"""
    __tablename__ = "bill"
    
    bill_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transaction.transaction_id', ondelete='SET NULL'), nullable=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey('account.account_id', ondelete='CASCADE'), nullable=False)
    merchant = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending')
    is_recurring = Column(Boolean, default=False)
    
    # Relationships
    account = relationship("Account", back_populates="bills")
    transaction = relationship("Transaction", back_populates="bill")
    
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'paid')", name='check_bill_status'),
    )