"""
Exceptions for the IndoxHub client.
"""

from datetime import datetime
from typing import Optional


class IndoxHubError(Exception):
    """Base exception for all IndoxHub errors."""

    pass


class AuthenticationError(IndoxHubError):
    """Raised when authentication fails."""

    pass


class NetworkError(IndoxHubError):
    """Raised when a network error occurs."""

    pass


class RateLimitError(IndoxHubError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str, reset_time: Optional[datetime] = None):
        super().__init__(message)
        self.reset_time = reset_time


class ProviderError(IndoxHubError):
    """Raised when a provider returns an error."""

    pass


class ProviderNotFoundError(ProviderError):
    """Raised when a requested provider is not found."""

    pass


class ModelNotFoundError(ProviderError):
    """Raised when a requested model is not found."""

    pass


class ModelNotAvailableError(ProviderError):
    """Raised when a model is disabled or not supported by the provider."""

    pass


class InvalidParametersError(IndoxHubError):
    """Raised when invalid parameters are provided."""

    pass


class RequestError(IndoxHubError):
    """Raised when a request to a provider fails."""

    pass


class InsufficientCreditsError(IndoxHubError):
    """Raised when the user doesn't have enough credits."""

    pass


class ValidationError(IndoxHubError):
    """Raised when request validation fails."""

    pass


class APIError(IndoxHubError):
    """Raised when the API returns an error."""

    pass
