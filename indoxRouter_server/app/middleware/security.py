"""
Security middleware for indoxRouter.
This middleware implements IP-based security checks.
"""

import logging
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.security import (
    get_client_ip,
    is_ip_allowed,
    is_suspicious,
    validate_api_key_format,
)

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware that implements security checks."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Dispatch the request to the next middleware or route handler.

        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.

        Returns:
            The response.
        """
        # Get client IP
        client_ip = get_client_ip(request)

        # Check if IP is allowed
        if not is_ip_allowed(client_ip):
            logger.warning(f"Blocked request from restricted IP: {client_ip}")
            return Response(
                content="Access denied", status_code=status.HTTP_403_FORBIDDEN
            )

        # Check if IP is suspicious
        if is_suspicious(client_ip):
            logger.warning(f"Blocked request from suspicious IP: {client_ip}")
            return Response(
                content="Access denied due to suspicious activity",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Check API key format for API routes
        if (
            request.url.path.startswith("/api/v1/")
            and request.url.path != "/api/v1/auth/token"
        ):
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                api_key = auth_header.replace("Bearer ", "")
                # Disable API key format validation - accept all keys
                # if not validate_api_key_format(api_key):
                #     logger.warning(f"Invalid API key format detected from {client_ip}")
                #     return Response(
                #         content="Invalid API key format",
                #         status_code=status.HTTP_401_UNAUTHORIZED
                #     )

        # Process the request
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response
