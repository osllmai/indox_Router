"""
Base resource module for indoxRouter.
This module contains the BaseResource class that all resource classes inherit from.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..providers import get_provider
from ..db.database import get_connection, update_user_credit
from ..exceptions import ProviderNotFoundError, InvalidParametersError

logger = logging.getLogger(__name__)


class BaseResource:
    """Base resource class that all resource classes inherit from."""

    def _get_provider(
        self, provider: str, model_name: str, provider_api_key: Optional[str] = None
    ):
        """
        Get a provider implementation.

        Args:
            provider: The provider ID.
            model_name: The model name.
            provider_api_key: Optional API key for the provider.

        Returns:
            A provider implementation.

        Raises:
            ProviderNotFoundError: If the provider is not found.
        """
        # If no API key is provided, try to get it from environment variables
        if not provider_api_key:
            provider_api_key = os.getenv(f"{provider.upper()}_API_KEY")

        # Get the provider implementation
        return get_provider(provider, provider_api_key, model_name)

    def _handle_provider_error(self, error: Exception):
        """
        Handle provider errors.

        Args:
            error: The error to handle.

        Raises:
            The appropriate exception based on the error.
        """
        # Log the error
        logger.error(f"Provider error: {error}")

        # Re-raise the error
        raise error

    def _update_user_credit(
        self,
        user_id: int,
        cost: float,
        endpoint: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
        model: str = "",
        provider: str = "",
    ):
        """
        Update a user's credit in the database.

        Args:
            user_id: The user ID.
            cost: The cost of the request.
            endpoint: The endpoint that was called.
            tokens_input: The number of input tokens.
            tokens_output: The number of output tokens.
            model: The model that was used.
            provider: The provider that was used.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Update the user's credit
            from app.db.database import update_user_credit

            success = update_user_credit(
                user_id=user_id,
                cost=cost,
                endpoint=endpoint,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                model=model,
                provider=provider,
            )

            if not success:
                logger.warning(f"Failed to update credit for user {user_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating user credit: {e}")
            return False
