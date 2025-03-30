"""
IndoxRouter: A unified client for various AI providers.

This package provides a client for interacting with the IndoxRouter server,
which serves as a unified interface to multiple AI providers and models.

Example:
    ```python
    from indoxrouter import Client

    # Initialize client with API key
    client = Client(api_key="your_api_key")

    # Generate a chat completion
    response = client.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ], model="openai/gpt-4o-mini")

    print(response["data"])
    ```
"""

from .client import Client
from .exceptions import (
    IndoxRouterError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidParametersError,
    InsufficientCreditsError,
)

__version__ = "0.2.0"
__all__ = [
    "Client",
    "IndoxRouterError",
    "AuthenticationError",
    "NetworkError",
    "RateLimitError",
    "ProviderError",
    "ModelNotFoundError",
    "ProviderNotFoundError",
    "InvalidParametersError",
    "InsufficientCreditsError",
]
