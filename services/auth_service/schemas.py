# auth_service/schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserRegister(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: Optional[str] = None  # Will convert UUID to string
    email: str
    phone: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        """Convert UUID to string"""
        if hasattr(obj, 'user_id') and isinstance(obj.user_id, UUID):
            obj.user_id = str(obj.user_id)
        return super().from_orm(obj)

class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"