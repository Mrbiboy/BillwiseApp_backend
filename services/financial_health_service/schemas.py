# financial_health_service/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

class EmploymentStatus(str, Enum):
    EMPLOYED = "Employed"
    SELF_EMPLOYED = "Self-Employed"
    UNEMPLOYED = "Unemployed"
    STUDENT = "Student"
    RETIRED = "Retired"

class Region(str, Enum):
    NORTH_AMERICA = "North America"
    EUROPE = "Europe"
    ASIA = "Asia"
    AFRICA = "Africa"
    SOUTH_AMERICA = "South America"
    AUSTRALIA = "Australia"

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    BACHELORS = "Bachelor's"
    MASTERS = "Master's"
    PHD = "PhD"
    OTHER = "Other"

class FinancialHealthRequest(BaseModel):
    age: int = Field(..., ge=18, le=100, description="Age of the user")
    monthly_income_usd: float = Field(..., ge=0, description="Monthly income in USD")
    monthly_expenses_usd: float = Field(..., ge=0, description="Monthly expenses in USD")
    savings_usd: float = Field(..., ge=0, description="Total savings in USD")
    loan_amount_usd: Optional[float] = Field(0, ge=0, description="Total loan amount")
    monthly_emi_usd: Optional[float] = Field(0, ge=0, description="Monthly EMI payment")
    employment_status: EmploymentStatus = Field(EmploymentStatus.EMPLOYED, description="Employment status")
    region: Region = Field(Region.NORTH_AMERICA, description="Geographic region")
    gender: Gender = Field(Gender.MALE, description="Gender")
    education_level: EducationLevel = Field(EducationLevel.BACHELORS, description="Education level")
    
    @validator('monthly_expenses_usd')
    def validate_expenses(cls, v, values):
        if 'monthly_income_usd' in values and v > values['monthly_income_usd'] * 2:
            print("⚠️ Warning: Expenses are more than double income")
        return v

class FinancialHealthResponse(BaseModel):
    financial_score: float = Field(..., ge=0, le=100, description="Financial health score (0-100)")
    status: str = Field(..., description="Financial health status")
    details: Optional[dict] = Field(None, description="Additional details")