"""
Rate limiting middleware for indoxRouter.
This middleware adds rate limit headers to responses.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that adds rate limit headers to responses."""

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
        # Process the request
        response = await call_next(request)

        # Add rate limit headers if they exist
        if hasattr(request.state, "rate_limit_headers"):
            for name, value in request.state.rate_limit_headers.items():
                response.headers[name] = value

        return response 