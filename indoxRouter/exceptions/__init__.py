"""
Exceptions module for indoxRouter.
This module contains all the custom exceptions used throughout the application.
"""


class IndoxRouterError(Exception):
    """Base exception for all indoxRouter errors."""

    pass


class AuthenticationError(IndoxRouterError):
    """Raised when authentication fails."""

    pass


class InvalidAPIKeyError(AuthenticationError):
    """Raised when an invalid API key is provided."""

    pass


class ProviderError(IndoxRouterError):
    """Raised when there's an error with a provider."""

    pass


class ModelNotFoundError(ProviderError):
    """Raised when a model is not found."""

    pass


class ProviderNotFoundError(ProviderError):
    """Raised when a provider is not found."""

    pass


class RequestError(IndoxRouterError):
    """Raised when a request to a provider fails."""

    pass


class RateLimitError(RequestError):
    """Raised when a rate limit is exceeded."""

    pass


class QuotaExceededError(RequestError):
    """Raised when a quota is exceeded."""

    pass


class InvalidParametersError(IndoxRouterError):
    """Raised when invalid parameters are provided."""

    pass
