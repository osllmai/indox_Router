"""
Image resource module for indoxRouter.
This module contains the Images resource class for image generation functionality.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseResource
from ..models import ImageResponse, Usage
from ..providers import get_provider
from ..constants import DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_COUNT
from ..exceptions import ProviderNotFoundError, InvalidParametersError


class Images(BaseResource):
    """Resource class for image generation functionality."""

    def __call__(
        self,
        prompt: str,
        model: str,
        size: Optional[str] = None,
        n: int = 1,
        provider_api_key: Optional[str] = None,
        **kwargs,
    ) -> ImageResponse:
        """
        Generate an image from a prompt.

        Args:
            prompt: The prompt to generate an image from.
            model: The model to use.
            size: The size of the image to generate.
            n: The number of images to generate.
            provider_api_key: Optional API key for the provider. If not provided, uses the configured key.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            An ImageResponse object containing the generated images.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
            InvalidParametersError: If the parameters are invalid.
            RequestError: If the request to the provider fails.
        """
        # Get the provider and model
        provider, model_name = model.split("/")

        # Get the provider API key
        provider_api_key = os.getenv(f"{provider.upper()}_API_KEY")
        # Get the provider implementation
        provider_impl = get_provider(provider, provider_api_key, model_name)

        # Send the request to the provider
        response = provider_impl.generate_image(prompt=prompt, size=size, n=n, **kwargs)

        # If the response is a dictionary, convert it to an ImageResponse object
        if isinstance(response, dict):
            # Create Usage object from response
            usage_data = response.get("usage", {})

            # Parse timestamp if it's a string
            timestamp = response.get("timestamp")
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()

            # Extract usage information with fallbacks for different formats
            tokens_prompt = usage_data.get("tokens_prompt", 0)
            tokens_completion = usage_data.get("tokens_completion", 0)
            tokens_total = usage_data.get("tokens_total", 0)

            usage = Usage(
                tokens_prompt=tokens_prompt,
                tokens_completion=tokens_completion,  # Images don't have completion tokens
                tokens_total=tokens_total,
                cost=response.get("cost", 0.0),
                latency=0.0,  # We don't have latency in the dictionary
                timestamp=timestamp,
            )

            return ImageResponse(
                images=response.get("data"),
                model=response.get("model", model_name),
                provider=provider,
                usage=usage,
                sizes=response.get(
                    "sizes", [size] * len(response.get("images", [])) if size else []
                ),
                formats=response.get("formats", []),
                raw_response=response.get("raw_response", None),
            )

        return response
