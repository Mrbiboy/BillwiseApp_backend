from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.database import get_db

from services.sms_parser_service.nlp_processor import SMSParser
from services.sms_parser_service.db_saver import SMSDatabaseSaver

router = APIRouter(prefix="/api/sms-parser", tags=["SMS Parser"])

# Initialize your NLP parser
sms_parser = SMSParser()


# curl -X POST "http://localhost:8004/parse-sms" -H "Content-Type: application/json; charset=utf-8" -d "{\"user_id\":\"123e4567-e89b-12d3-a456-426614174000\",\"account_id\":\"123e4567-e89b-12d3-a456-426614174001\",\"sms_text\":\"Votre facture Inwi Fibre numero 1234567890 de Mars 2025 de 450.00dh payable avant 12/03/2025 est disponible sur bit.inwi.ma/Facture\"}"
# {"success":true,"message":"SMS processed and saved successfully","parsed_data":{"provider":"Inwi","service":null,"account":"1234567890","bill_month":"Mars 2025","amount":"450.00dh","due_date":null,"url":"bit.inwi.ma/Facture","raw_text":"Votre facture Inwi Fibre numero 1234567890 de Mars 2025 de 450.00dh payable avant 12/03/2025 est disponible sur bit.inwi.ma/Facture"},"transaction_id":"e54fd218-540b-4bc8-948b-cfe123318887","bill_id":"173c203d-335f-4b1a-81f4-ddbb5888f11c"}
# Request/Response models
class SMSRequest(BaseModel):
    user_id: str
    account_id: str
    sms_text: str

    class Config:
        # Ensure proper UTF-8 handling in Pydantic
        json_encoders = {str: lambda v: v.encode("utf-8").decode("utf-8")}


class SMSResponse(BaseModel):
    success: bool
    message: str
    parsed_data: dict
    transaction_id: Optional[str] = None
    bill_id: Optional[str] = None


@router.post("/parse-sms", response_model=SMSResponse)
async def parse_and_save_sms(request: SMSRequest, db: Session = Depends(get_db)):
    """
    Parse SMS with NLP and save to database
    """
    try:
        # Step 1: Parse SMS with YOUR existing NLP service
        parsed_data = sms_parser.parse(request.sms_text)
        # parsed_data = {
        #     "provider": "...",
        #     "service": "...",
        #     "amount": "...",
        #     "due_date": "...",
        #     "raw_text": "..."
        # }

        # Step 2: Save to database
        db_saver = SMSDatabaseSaver(db)
        result = db_saver.save_sms_data(account_id=request.account_id, parsed_data=parsed_data)

        # Step 3: Return response
        return SMSResponse(
            success=True,
            message="SMS processed and saved successfully",
            parsed_data=parsed_data,
            transaction_id=str(result["transaction"].transaction_id),
            bill_id=str(result["bill"].bill_id) if result["bill"] else None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sms_parser_service"}
