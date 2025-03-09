"""
API dependencies for the IndoxRouter server.
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current user from the token.

    Args:
        token: The JWT token.

    Returns:
        The user data.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # In a real application, you would fetch the user from a database
    # For now, we'll just return a mock user
    user = {
        "username": username,
        "is_active": True,
    }

    if user is None:
        raise credentials_exception

    return user


def get_provider_api_key(provider: str) -> Optional[str]:
    """
    Get the API key for a provider.

    Args:
        provider: The provider name.

    Returns:
        The API key for the provider, or None if not found.
    """
    provider_keys = {
        "openai": settings.OPENAI_API_KEY,
        "anthropic": settings.ANTHROPIC_API_KEY,
        "cohere": settings.COHERE_API_KEY,
        "google": settings.GOOGLE_API_KEY,
        "mistral": settings.MISTRAL_API_KEY,
    }

    return provider_keys.get(provider)
