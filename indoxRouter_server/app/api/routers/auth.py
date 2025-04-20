"""
Authentication router for the IndoxRouter server.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import json

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import requests

from app.core.config import settings
from app.models.schemas import (
    Token,
    TokenRequest,
    UserCreate,
    UserResponse,
    GoogleAuthRequest,
    AuthResponse,
)
from app.db.database import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    update_last_login,
    create_or_update_google_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user."""
    user = get_user_by_username(username)
    if not user:
        # Try with email instead
        user = get_user_by_email(username)
        if not user:
            return None

    if not verify_password(password, user["password"]):
        return None

    # Update last login time
    update_last_login(user["id"])

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    return encoded_jwt


@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserCreate):
    """Register a new user."""
    # Check if username or email already exists
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create the user
    new_user = create_user(
        user_data.username,
        user_data.email,
        hashed_password,
        user_data.first_name,
        user_data.last_name,
    )
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user["id"])}, expires_delta=access_token_expires
    )

    # Return user data and token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserResponse(**new_user),
    }


@router.post("/login", response_model=AuthResponse)
async def login(token_request: TokenRequest):
    """Login with username/email and password."""
    user = authenticate_user(token_request.username, token_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )

    # Return user data and token
    user_data = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "is_active": user["is_active"],
        "credits": float(user["credits"]),
        "account_tier": user["account_tier"],
        "created_at": user["created_at"],
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserResponse(**user_data),
    }


@router.post("/google", response_model=AuthResponse)
async def google_auth(auth_data: GoogleAuthRequest):
    """Authenticate with Google."""
    try:
        # Verify the Google ID token
        google_token_info_url = (
            f"https://oauth2.googleapis.com/tokeninfo?id_token={auth_data.token}"
        )
        response = requests.get(google_token_info_url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
            )

        token_info = response.json()

        # Extract user information from the token
        email = token_info.get("email")
        google_id = token_info.get("sub")
        name = token_info.get("name", email.split("@")[0])

        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required Google profile information",
            )

        # Create or update user
        user = create_or_update_google_user(email, google_id, name)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or update user",
            )

        # Generate access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user["id"])}, expires_delta=access_token_expires
        )

        # Return user data and token
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_active": user["is_active"],
            "credits": float(user["credits"]),
            "account_tier": user["account_tier"],
            "created_at": user["created_at"],
        }

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserResponse(**user_data),
        }

    except requests.RequestException as e:
        logger.error(f"Error verifying Google token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify Google token",
        )
    except Exception as e:
        logger.error(f"Error in Google authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        )
