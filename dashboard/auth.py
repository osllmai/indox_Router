"""
Authentication utilities for the IndoxRouter dashboard.
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "indoxrouter-dashboard-secret-2024")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT access token.

    Args:
        token: The JWT token to decode

    Returns:
        The decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None
