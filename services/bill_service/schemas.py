"""
schemas.py - Schémas Pydantic pour la validation des données
"""
import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class BillCreate(BaseModel):
    """Schéma pour créer une facture"""
    merchant: str = Field(..., min_length=1, max_length=255, description="Nom du fournisseur")
    amount: float = Field(..., gt=0, description="Montant de la facture")
    due_date: datetime = Field(..., description="Date d'échéance")
    account_id: UUID = Field(..., description="ID du compte")
    is_recurring: bool = Field(False, description="Est-ce une facture récurrente?")
    transaction_id: Optional[UUID] = Field(None, description="ID de transaction (optionnel)")

    class Config:
        json_schema_extra = {
            "example": {
                "merchant": "EDF",
                "amount": 89.50,
                "due_date": "2024-12-31T23:59:59",
                "account_id": "550e8400-e29b-41d4-a716-446655440000",
                "is_recurring": True,
                "transaction_id": None
            }
        }


class BillUpdate(BaseModel):
    """Schéma pour mettre à jour une facture"""
    merchant: Optional[str] = Field(None, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(
        None,
        pattern="^(pending|paid|overdue)$",
        description="pending, paid ou overdue"
    )
    is_recurring: Optional[bool] = None
    transaction_id: Optional[UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "paid",
                "transaction_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class BillResponse(BaseModel):
    """Schéma de réponse pour une facture"""
    bill_id: UUID
    account_id: UUID
    merchant: str
    amount: float
    due_date: datetime
    status: str
    is_recurring: bool
    transaction_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class BillStats(BaseModel):
    """Schéma pour les statistiques des factures"""
    total_bills: int
    total_amount: float
    pending_amount: float
    overdue_amount: float
    paid_amount: float

    class Config:
        json_schema_extra = {
            "example": {
                "total_bills": 5,
                "total_amount": 1250.50,
                "pending_amount": 450.00,
                "overdue_amount": 150.00,
                "paid_amount": 650.50
            }
        }