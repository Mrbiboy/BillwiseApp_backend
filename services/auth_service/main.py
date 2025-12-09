"""
Auth Service - User registration, login, and authentication
"""
import sys
from pathlib import Path

# Add parent path for imports (BEFORE all other imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager
from typing import Optional
import logging

from database.database import engine, get_db, Base
from models import User
from schemas import UserRegister, UserLogin, UserResponse, AuthResponse
from utils import hash_password, verify_password, create_access_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info(" Auth Service starting...")
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info(" Auth Service shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Auth Service",
    description="Microservice for user authentication and registration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Check service health"""
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0"
    }

# ==================== REGISTER ====================

@app.post(
    "/api/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            logger.warning(f" Registration failed: Email already exists - {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = User(
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hash_password(user_data.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": new_user.user_id})
        
        logger.info(f" User registered successfully: {new_user.user_id} - {new_user.email}")
        
        return AuthResponse(
            user=UserResponse.from_orm(new_user),
            access_token=access_token
        )
    
    except IntegrityError:
        db.rollback()
        logger.error(f" Integrity error during registration: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f" Error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during registration"
        )

# ==================== LOGIN ====================

@app.post(
    "/api/auth/login",
    response_model=AuthResponse,
    summary="Login user"
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    try:
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user or not verify_password(credentials.password, user.password_hash):
            logger.warning(f" Login failed: Invalid credentials - {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        access_token = create_access_token(data={"sub": user.user_id})
        
        logger.info(f" User logged in successfully: {user.user_id} - {user.email}")
        
        return AuthResponse(
            user=UserResponse.from_orm(user),
            access_token=access_token
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

# ==================== GET USER ====================

@app.get(
    "/api/auth/me/{user_id}",
    response_model=UserResponse,
    summary="Get user info"
)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user information by user_id"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            logger.warning(f" User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f" User retrieved: {user_id}")
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error retrieving user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        )

# ==================== VERIFY TOKEN ====================

@app.get(
    "/api/auth/verify/{user_id}",
    summary="Verify user exists"
)
async def verify_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Verify if user exists"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            logger.warning(f" User verification failed: {user_id}")
            return {"valid": False, "message": "User not found"}
        
        logger.info(f" User verified: {user_id}")
        return {"valid": True, "message": "User exists"}
    except Exception as e:
        logger.error(f" Error verifying user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying user"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8087)