from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import re
from services.sms_parser_service.models import Transaction, Bill

class SMSDatabaseSaver:
    """Simple class to save parsed SMS data to database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_sms_data(self, account_id: str, parsed_data: dict) -> dict:
        """
        Save parsed SMS data to database
        
        Args:
            account_id: UUID of the account
            parsed_data: Dict from nlp_processor.parse() with keys:
                        provider, service, amount, due_date, raw_text, etc.
        
        Returns:
            dict with 'transaction' and 'bill' (if applicable)
        """
        try:
            # Extract and clean amount
            amount = self._extract_amount(parsed_data.get('amount'))
            
            # Determine merchant (prioritize provider over service)
            merchant = (
                parsed_data.get('provider') or 
                parsed_data.get('service') or 
                'Unknown'
            )
            
            # Get raw text
            raw_text = parsed_data.get('raw_text', '')
            
            # Determine transaction type
            trans_type = self._get_transaction_type(raw_text)
            
            # Determine category
            category = self._categorize(merchant, raw_text)
            
            # Create transaction
            transaction = Transaction(
                account_id=account_id,
                amount=amount,
                type=trans_type,
                category=category,
                merchant=merchant,
                source='sms',
                description=raw_text[:500] if raw_text else None
            )
            
            self.db.add(transaction)
            self.db.flush()  # Get transaction_id without committing yet
            
            result = {'transaction': transaction, 'bill': None}
            
            # Check if it's a bill (check for due_date or bill keywords)
            is_bill = self._is_bill(raw_text) or parsed_data.get('due_date')
            
            if is_bill:
                due_date = self._parse_date(parsed_data.get('due_date'))
                
                # If we couldn't parse due_date but it's clearly a bill,
                # set a default due date (30 days from now)
                if not due_date:
                    from datetime import timedelta
                    due_date = datetime.utcnow() + timedelta(days=30)
                
                bill = Bill(
                    transaction_id=transaction.transaction_id,
                    account_id=account_id,
                    merchant=merchant,
                    amount=amount,
                    due_date=due_date,
                    status='pending',
                    is_recurring=self._is_recurring(raw_text)
                )
                
                self.db.add(bill)
            
            # Commit both transaction and bill together
            self.db.commit()
            self.db.refresh(transaction)
            
            if is_bill:
                self.db.refresh(bill)
                result['bill'] = bill
            
            return result
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error saving to database: {str(e)}")
    
    # Helper methods
    def _extract_amount(self, amount_str) -> Decimal:
        """Extract decimal from amount string"""
        if not amount_str:
            return Decimal('0.00')
        
        # Handle if it's already a number
        if isinstance(amount_str, (int, float)):
            return Decimal(str(amount_str))
        
        # Clean string and extract numbers
        amount_str = str(amount_str)
        # Remove currency symbols and letters, keep digits, dots, and commas
        cleaned = re.sub(r'[^\d.,]', '', amount_str)
        
        # Handle comma as decimal separator (European format)
        if ',' in cleaned and '.' not in cleaned:
            cleaned = cleaned.replace(',', '.')
        # Handle comma as thousand separator
        elif ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        
        try:
            return Decimal(cleaned) if cleaned else Decimal('0.00')
        except:
            return Decimal('0.00')
    
    def _get_transaction_type(self, text: str) -> str:
        """Determine debit or credit"""
        if not text:
            return 'debit'
        
        text_lower = text.lower()
        credit_keywords = ['credited', 'received', 'deposited', 'refund', 'credit', 'reçu']
        
        if any(word in text_lower for word in credit_keywords):
            return 'credit'
        return 'debit'
    
    def _categorize(self, merchant: str, text: str) -> str:
        """Categorize transaction"""
        text_lower = text.lower() if text else ''
        merchant_lower = merchant.lower() if merchant else ''
        
        # Utilities (includes telecom like Inwi, IAM, Orange)
        utilities_keywords = ['electricity', 'water', 'internet', 'phone', 'mobile', 
                             'telecom', 'inwi', 'iam', 'orange', 'maroc telecom',
                             'fibre', 'wifi', 'électricité', 'eau']
        if any(word in text_lower or word in merchant_lower for word in utilities_keywords):
            return 'utilities'
        
        # Groceries
        groceries_keywords = ['grocery', 'supermarket', 'marjane', 'carrefour', 'acima']
        if any(word in text_lower or word in merchant_lower for word in groceries_keywords):
            return 'groceries'
        
        # Transport
        transport_keywords = ['uber', 'taxi', 'fuel', 'careem', 'transport', 'parking']
        if any(word in text_lower or word in merchant_lower for word in transport_keywords):
            return 'transport'
        
        # Entertainment
        entertainment_keywords = ['netflix', 'spotify', 'cinema', 'game', 'subscription']
        if any(word in text_lower or word in merchant_lower for word in entertainment_keywords):
            return 'entertainment'
        
        return 'other'
    
    def _is_bill(self, text: str) -> bool:
        """Check if SMS is a bill"""
        if not text:
            return False
        
        text_lower = text.lower()
        bill_keywords = ['bill', 'invoice', 'due', 'payment due', 'facture', 
                        'payable', 'échéance', 'montant à payer']
        return any(word in text_lower for word in bill_keywords)
    
    def _is_recurring(self, text: str) -> bool:
        """Check if recurring"""
        if not text:
            return False
        
        text_lower = text.lower()
        recurring_keywords = ['monthly', 'subscription', 'recurring', 'mensuel', 
                             'abonnement', 'récurrent']
        return any(word in text_lower for word in recurring_keywords)
    
    def _parse_date(self, date_str):
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        # Clean the date string
        date_str = str(date_str).strip()
        
        # Try multiple date formats
        formats = [
            '%d/%m/%Y',      # 12/03/2025
            '%Y-%m-%d',      # 2025-03-12
            '%m/%d/%Y',      # 03/12/2025
            '%d-%m-%Y',      # 12-03-2025
            '%d.%m.%Y',      # 12.03.2025
            '%Y/%m/%d',      # 2025/03/12
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If no format worked, return None
        return None