"""
Exceptions for the IndoxRouter server.
"""


class BaseError(Exception):
    """Base error class for all IndoxRouter errors."""

    pass


class ProviderNotFoundError(BaseError):
    """Raised when a provider is not found."""

    pass


class ModelNotFoundError(BaseError):
    """Raised when a model is not found."""

    pass


class InvalidParametersError(BaseError):
    """Raised when invalid parameters are provided."""

    pass


class RequestError(BaseError):
    """Raised when a request to a provider fails."""

    pass


class InsufficientCreditsError(BaseError):
    """Raised when a user doesn't have enough credits."""

    pass
