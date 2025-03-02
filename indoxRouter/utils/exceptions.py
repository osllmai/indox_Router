# utils/exceptions.py


class IndoxError(Exception):
    """Base exception class for all IndoxRouter errors"""

    pass


class AuthenticationError(IndoxError):
    """Raised when authentication fails"""

    pass


class InsufficientCreditsError(IndoxError):
    """Raised when a user has insufficient credits for an operation"""

    pass


class RateLimitError(IndoxError):
    """Raised when a provider's rate limit is exceeded"""

    pass


class ModelNotFoundError(IndoxError):
    """Raised when a requested model is not found"""

    pass


class ProviderNotFoundError(IndoxError):
    """Raised when a requested provider is not found"""

    pass


class ProviderAPIError(IndoxError):
    """Raised when a provider's API returns an error"""

    pass


class ConfigurationError(IndoxError):
    """Raised when there's an issue with the configuration"""

    pass


class TokenizerError(IndoxError):
    """Raised when there's an issue with tokenization"""

    pass


class ValidationError(IndoxError):
    """Raised when input validation fails"""

    pass
