import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "BillWise Cash Flow Service"
    database_url: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    model_path: str = os.getenv("MODEL_PATH", "./trained_models")
    
    class Config:
        env_file = ".env"

settings = Settings()