"""
Exceptions for the IndoxRouter client.
"""

from datetime import datetime
from typing import Optional


class IndoxRouterError(Exception):
    """Base exception for all IndoxRouter errors."""

    pass


class AuthenticationError(IndoxRouterError):
    """Raised when authentication fails."""

    pass


class NetworkError(IndoxRouterError):
    """Raised when a network error occurs."""

    pass


class RateLimitError(IndoxRouterError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str, reset_time: Optional[datetime] = None):
        super().__init__(message)
        self.reset_time = reset_time


class ProviderError(IndoxRouterError):
    """Raised when a provider returns an error."""

    pass


class ModelNotFoundError(ProviderError):
    """Raised when a requested model is not found."""

    pass


class ProviderNotFoundError(ProviderError):
    """Raised when a requested provider is not found."""

    pass


class InvalidParametersError(IndoxRouterError):
    """Raised when invalid parameters are provided."""

    pass


class InsufficientCreditsError(IndoxRouterError):
    """Raised when the user doesn't have enough credits."""

    pass
