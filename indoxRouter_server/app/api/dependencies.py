"""
API dependencies for the IndoxRouter server.
"""

import json
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.core.config import settings
from app.utils.rate_limiter import check_rate_limit, get_rate_limit_headers
from app.db.database import get_user_by_id, verify_api_key, get_user_by_username
from app.exceptions import RateLimitError

# API key header
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
# OAuth2 password bearer scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


async def get_current_user(
    request: Request, authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Get the current user from the API key in the Authorization header.

    Args:
        request: The FastAPI request object.
        authorization: The Authorization header value.

    Returns:
        The user information if authenticated.

    Raises:
        HTTPException: If authentication fails.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Remove "Bearer " prefix if present
    api_key = authorization.replace("Bearer ", "")

    # Verify the API key and get the user
    user_info = verify_api_key(api_key)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user_info.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Check rate limits
    # Determine the endpoint and estimate token usage
    path = request.url.path
    endpoint = path.split("/")[-1]

    # Get estimated token count from request
    estimated_tokens = 0
    if request.method == "POST":
        try:
            body = await request.json()

            # Estimate tokens based on endpoint
            if endpoint == "chat":
                messages = body.get("messages", [])
                estimated_tokens = sum(
                    len(msg.get("content", "")) // 4 for msg in messages
                )
            elif endpoint == "completions":
                prompt = body.get("prompt", "")
                estimated_tokens = len(prompt) // 4
            elif endpoint == "embeddings":
                text = body.get("text", [])
                if isinstance(text, list):
                    estimated_tokens = sum(len(t) // 4 for t in text)
                else:
                    estimated_tokens = len(text) // 4

            # Apply minimum token count for any request
            estimated_tokens = max(10, estimated_tokens)

        except Exception:
            # If we can't parse the body, use a default estimate
            estimated_tokens = 50

    # Get user tier
    user_tier = user_info.get("account_tier", "free")

    # Skip rate limiting for admin tier users
    if user_tier == "admin":
        return user_info

    # Check rate limit for non-admin users
    allowed, rate_info = check_rate_limit(
        user_id=user_info["id"], user_tier=user_tier, tokens=estimated_tokens
    )

    # Add rate limit headers to the response
    headers = get_rate_limit_headers(user_info["id"], user_tier)
    request.state.rate_limit_headers = headers

    if not allowed:
        raise RateLimitError(
            f"Rate limit exceeded: {rate_info.get('reason', 'unknown reason')}. "
            f"Try again in {rate_info.get('reset_after', 0)} seconds."
        )

    return user_info


def get_provider_api_key(provider: str) -> Optional[str]:
    """
    Get the API key for a provider.

    Args:
        provider: The provider ID.

    Returns:
        The API key for the provider, or None if not configured.
    """
    # Check if provider is supported
    provider = provider.lower()

    # Get the API key based on the provider
    if provider == "openai":
        return settings.OPENAI_API_KEY
    elif provider == "anthropic":
        return settings.ANTHROPIC_API_KEY
    elif provider == "cohere":
        return settings.COHERE_API_KEY
    elif provider == "google":
        return settings.GOOGLE_API_KEY
    elif provider == "mistral":
        return settings.MISTRAL_API_KEY
    elif provider == "deepseek":
        return settings.DEEPSEEK_API_KEY
    else:
        return None


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    Validate JWT token and get the current user.

    Args:
        token: The JWT token from the Authorization header.

    Returns:
        The user information if authenticated.

    Raises:
        HTTPException: If authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Get the user from the database
        user = get_user_by_id(int(user_id))

        if user is None or not user.get("is_active", False):
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception


async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Check if the current user has admin privileges.
    Raises an HTTPException if the user is not an admin.

    Args:
        current_user: The current authenticated user

    Returns:
        The current user information if they are an admin
    """
    # This could be extended to check a more complex permissions system
    # For now, we'll just check if the user is in the 'admin' tier
    if current_user.get("account_tier") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin privileges required.",
        )
    return current_user
