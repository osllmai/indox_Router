"""
indoxRouter - A unified interface for various LLM providers.

This package provides a simple and consistent way to interact with different
LLM providers like OpenAI, Claude, Mistral, and more.
"""

__version__ = "0.1.0"

from .client import Client, IndoxRouter
from .config import Config, get_config
from .models import (
    ChatMessage,
    ChatResponse,
    CompletionResponse,
    EmbeddingResponse,
    ImageResponse,
    ModelInfo,
    Usage,
)
from .exceptions import (
    IndoxRouterError,
    AuthenticationError,
    ProviderError,
    ProviderNotFoundError,
    ModelNotFoundError,
    InvalidParametersError,
    RequestError,
)
from .constants import (
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    DEFAULT_FREQUENCY_PENALTY,
    DEFAULT_PRESENCE_PENALTY,
    DEFAULT_IMAGE_SIZE,
    DEFAULT_IMAGE_COUNT,
)
from .utils import (
    count_tokens,
    calculate_cost,
    format_timestamp,
)

__all__ = [
    # Main client
    "Client",
    "IndoxRouter",
    # Configuration
    "Config",
    "get_config",
    # Database
    "Database",
    "get_database",
    # Models
    "ChatMessage",
    "ChatResponse",
    "CompletionResponse",
    "EmbeddingResponse",
    "ImageResponse",
    "ModelInfo",
    "Usage",
    # Exceptions
    "IndoxRouterError",
    "AuthenticationError",
    "ProviderError",
    "ProviderNotFoundError",
    "ModelNotFoundError",
    "InvalidParametersError",
    "RequestError",
    # Constants
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_TOP_P",
    "DEFAULT_FREQUENCY_PENALTY",
    "DEFAULT_PRESENCE_PENALTY",
    "DEFAULT_IMAGE_SIZE",
    "DEFAULT_IMAGE_COUNT",
    # Utilities
    "count_tokens",
    "calculate_cost",
    "format_timestamp",
]
