"""
models.py - ORM Models pour le Bill Service
"""
import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from database.database import Base
import uuid


class Bill(Base):
    """
    Modèle ORM pour les factures
    Correspond à la table 'bill' de la base de données
    """
    __tablename__ = "bill"

    # Clés primaires
    bill_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False
    )
    
    # Clés étrangères
    transaction_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    account_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    # Informations de la facture
    merchant = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(DateTime(timezone=False), nullable=False)
    status = Column(
        String(20),
        default="pending",
        nullable=False
    )
    is_recurring = Column(Boolean, default=False, nullable=False)

    # Index pour les recherches fréquentes
    __table_args__ = (
        Index('idx_bill_account_id', 'account_id'),
        Index('idx_bill_status', 'status'),
        Index('idx_bill_due_date', 'due_date'),
    )

    def __repr__(self):
        return f"<Bill(bill_id={self.bill_id}, merchant={self.merchant}, amount={self.amount})>"