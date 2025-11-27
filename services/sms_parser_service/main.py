import sys
from pathlib import Path

backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.database import get_db

from services.sms_parser_service.nlp_processor import SMSParser
from services.sms_parser_service.db_saver import SMSDatabaseSaver

app = FastAPI(title="SMS Parser Service", version="1.0.0")

# Initialize your NLP parser
sms_parser = SMSParser()

# Request/Response models
class SMSRequest(BaseModel):
    user_id: str
    account_id: str
    sms_text: str
    
    class Config:
        # Ensure proper UTF-8 handling in Pydantic
        json_encoders = {
            str: lambda v: v.encode('utf-8').decode('utf-8')
        }

class SMSResponse(BaseModel):
    success: bool
    message: str
    parsed_data: dict
    transaction_id: Optional[str] = None
    bill_id: Optional[str] = None

@app.post("/parse-sms", response_model=SMSResponse)
async def parse_and_save_sms(
    request: SMSRequest,
    db: Session = Depends(get_db)
):
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
        result = db_saver.save_sms_data(
            account_id=request.account_id,
            parsed_data=parsed_data
        )
        
        # Step 3: Return response
        return SMSResponse(
            success=True,
            message="SMS processed and saved successfully",
            parsed_data=parsed_data,
            transaction_id=str(result['transaction'].transaction_id),
            bill_id=str(result['bill'].bill_id) if result['bill'] else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sms_parser_service"}
