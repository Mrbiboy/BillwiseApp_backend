from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from database.database import get_db
from .models import User
from .schemas import UserRegister, UserLogin, UserResponse, AuthResponse
from .utils import hash_password, verify_password, create_access_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.get("/health")
async def health_check():
    """Check service health"""
    return {"status": "healthy", "service": "auth-service", "version": "1.0.0"}


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            logger.warning(f" Registration failed: Email already exists - {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

        # Create new user
        new_user = User(
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hash_password(user_data.password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create access token
        access_token = create_access_token(data={"sub": new_user.user_id})

        logger.info(f" User registered successfully: {new_user.user_id} - {new_user.email}")

        return AuthResponse(user=UserResponse.from_orm(new_user), access_token=access_token)

    except IntegrityError:
        db.rollback()
        logger.error(f" Integrity error during registration: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f" Error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during registration"
        )


@router.post("/login", response_model=AuthResponse, summary="Login user")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    try:
        user = db.query(User).filter(User.email == credentials.email).first()

        if not user or not verify_password(credentials.password, user.password_hash):
            logger.warning(f" Login failed: Invalid credentials - {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
            )

        access_token = create_access_token(data={"sub": user.user_id})

        logger.info(f" User logged in successfully: {user.user_id} - {user.email}")

        return AuthResponse(user=UserResponse.from_orm(user), access_token=access_token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during login"
        )


@router.get("/me/{user_id}", response_model=UserResponse, summary="Get user info")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user information by user_id"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            logger.warning(f" User not found: {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        logger.info(f" User retrieved: {user_id}")
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error retrieving user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving user"
        )


@router.get("/verify/{user_id}", summary="Verify user exists")
async def verify_user(user_id: str, db: Session = Depends(get_db)):
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error verifying user"
        )
