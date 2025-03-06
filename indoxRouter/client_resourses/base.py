"""
Base resource module for indoxRouter.
This module contains the BaseResource class that all resource classes inherit from.
"""

from typing import Dict, Any, Optional

from ..config import Config
from ..exceptions import (
    InvalidParametersError,
    AuthenticationError,
    ProviderNotFoundError,
)


class BaseResource:
    """Base resource class for all API resources."""

    def __init__(self, client):
        """
        Initialize the resource.

        Args:
            client: The client instance that this resource belongs to.
        """
        self.client = client
        self.config = client.config

        # Get user from client, or use a default if not available
        if hasattr(client, "user") and client.user is not None:
            self.user = client.user
        else:
            self.user = {
                "id": 1,
                "name": "Default User",
                "email": "default@example.com",
            }

    def _get_provider_api_key(
        self, provider: str, provider_api_key: Optional[str] = None
    ) -> str:
        """
        Get the API key for a provider.

        Args:
            provider: The provider to get the API key for.
            provider_api_key: Optional API key to use. If provided, this takes precedence.

        Returns:
            The API key for the provider.

        Raises:
            AuthenticationError: If no API key is found for the provider.
        """
        # If a provider API key is provided, use it
        if provider_api_key:
            return provider_api_key

        # Otherwise, try to get it from the configuration
        api_key = self.config.get_provider_key(provider)
        if not api_key:
            raise AuthenticationError(
                f"No API key found for provider '{provider}'. "
                f"Please provide an API key or configure it in the configuration file."
            )

        return api_key
