from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID
import logging

from database.database import get_db
from .models import Bill
from .schemas import BillCreate, BillUpdate, BillResponse, BillStats

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bills", tags=["Bills"])


@router.get("/health")
async def health_check():
    """Vérifier la santé du service"""
    return {"status": "healthy", "service": "bill-service", "version": "1.0.0"}


@router.post(
    "/", response_model=BillResponse, status_code=201, summary="Créer une nouvelle facture"
)
async def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle facture"""
    try:
        new_bill = Bill(**bill.model_dump())
        db.add(new_bill)
        db.commit()
        db.refresh(new_bill)
        logger.info(f" Facture créée: {new_bill.bill_id} - {new_bill.merchant}")
        return new_bill
    except Exception as e:
        db.rollback()
        logger.error(f" Erreur création facture: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création")


@router.get("/", response_model=List[BillResponse], summary="Lister les factures")
async def list_bills(
    account_id: UUID = Query(None, description="Filtrer par compte"),
    status: str = Query(None, regex="^(pending|paid|overdue)$", description="Filtrer par statut"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Récupérer la liste des factures avec filtres optionnels"""
    try:
        query = db.query(Bill)

        if account_id:
            query = query.filter(Bill.account_id == account_id)

        if status:
            query = query.filter(Bill.status == status)

        bills = query.order_by(desc(Bill.due_date)).offset(offset).limit(limit).all()
        logger.info(f" {len(bills)} factures récupérées")
        return bills
    except Exception as e:
        logger.error(f" Erreur lecture factures: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la lecture")


@router.get(
    "/account/{account_id}",
    response_model=List[BillResponse],
    summary="Récupérer les factures d'un compte",
)
async def get_bills_by_account(
    account_id: UUID,
    status: str = Query(None, regex="^(pending|paid|overdue)$"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Récupérer toutes les factures d'un compte spécifique"""
    try:
        query = db.query(Bill).filter(Bill.account_id == account_id)

        if status:
            query = query.filter(Bill.status == status)

        bills = query.order_by(desc(Bill.due_date)).limit(limit).all()

        if not bills:
            logger.warning(f" Aucune facture pour le compte {account_id}")

        logger.info(f" {len(bills)} factures récupérées pour le compte {account_id}")
        return bills
    except Exception as e:
        logger.error(f" Erreur lecture par compte: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/{bill_id}", response_model=BillResponse, summary="Récupérer une facture")
async def get_bill(bill_id: UUID, db: Session = Depends(get_db)):
    """Récupérer les détails d'une facture spécifique"""
    try:
        bill = db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if not bill:
            logger.warning(f" Facture non trouvée: {bill_id}")
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        return bill
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Erreur lecture facture: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la lecture")


@router.patch("/{bill_id}", response_model=BillResponse, summary="Mettre à jour une facture")
async def update_bill(bill_id: UUID, bill_update: BillUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une facture"""
    try:
        bill = db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if not bill:
            logger.warning(f" Facture non trouvée: {bill_id}")
            raise HTTPException(status_code=404, detail="Facture non trouvée")

        update_data = bill_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bill, field, value)

        db.commit()
        db.refresh(bill)
        logger.info(f" Facture mise à jour: {bill_id}")
        return bill
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f" Erreur mise à jour: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")


@router.delete("/{bill_id}", status_code=204, summary="Supprimer une facture")
async def delete_bill(bill_id: UUID, db: Session = Depends(get_db)):
    """Supprimer une facture"""
    try:
        bill = db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if not bill:
            logger.warning(f" Facture non trouvée: {bill_id}")
            raise HTTPException(status_code=404, detail="Facture non trouvée")

        db.delete(bill)
        db.commit()
        logger.info(f" Facture supprimée: {bill_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f" Erreur suppression: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression")


@router.get(
    "/account/{account_id}/stats",
    response_model=BillStats,
    summary="Statistiques des factures",
)
async def get_bills_stats(account_id: UUID, db: Session = Depends(get_db)):
    """Obtenir les statistiques des factures d'un compte"""
    try:
        bills = db.query(Bill).filter(Bill.account_id == account_id).all()

        total_amount = sum(float(bill.amount) for bill in bills)
        pending_amount = sum(float(bill.amount) for bill in bills if bill.status == "pending")
        overdue_amount = sum(float(bill.amount) for bill in bills if bill.status == "overdue")
        paid_amount = total_amount - pending_amount - overdue_amount

        stats = BillStats(
            total_bills=len(bills),
            total_amount=round(total_amount, 2),
            pending_amount=round(pending_amount, 2),
            overdue_amount=round(overdue_amount, 2),
            paid_amount=round(paid_amount, 2),
        )

        logger.info(f" Stats calculées pour le compte {account_id}")
        return stats
    except Exception as e:
        logger.error(f" Erreur calcul stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors du calcul")
