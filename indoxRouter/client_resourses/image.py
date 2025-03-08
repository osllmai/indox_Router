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
from ..constants import (
    DEFAULT_IMAGE_SIZE, 
    DEFAULT_IMAGE_COUNT,
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_IMAGE_STYLE,
    ERROR_INVALID_PARAMETERS,
    ERROR_PROVIDER_NOT_FOUND,
    ERROR_INVALID_IMAGE_SIZE
)
from ..exceptions import ProviderNotFoundError, InvalidParametersError


class Images(BaseResource):
    """Resource class for image generation functionality."""

    def __call__(
        self,
        prompt: str,
        model: str,
        size: str = DEFAULT_IMAGE_SIZE,
        n: int = DEFAULT_IMAGE_COUNT,
        quality: str = DEFAULT_IMAGE_QUALITY,
        style: str = DEFAULT_IMAGE_STYLE,
        provider_api_key: Optional[str] = None,
        **kwargs,
    ) -> ImageResponse:
        """
        Generate an image from a prompt.

        Args:
            prompt: The prompt to generate an image from.
            model: The model to use, in the format 'provider/model-name'.
            size: The size of the image to generate.
            n: The number of images to generate.
            quality: The quality of the image to generate.
            style: The style of the image to generate.
            provider_api_key: The API key to use for the provider.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            An ImageResponse object containing the generated images.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
            InvalidParametersError: If the parameters are invalid.
        """
        # Validate parameters
        if not isinstance(prompt, str):
            raise InvalidParametersError(f"{ERROR_INVALID_PARAMETERS}: prompt must be a string")

        # Split provider and model name correctly
        try:
            provider, model_name = model.split("/", 1)
        except ValueError:
            raise InvalidParametersError(f"{ERROR_INVALID_PARAMETERS}: Model must be in format 'provider/model-name'")

        # Validate image size
        valid_sizes = ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
        if size not in valid_sizes:
            raise InvalidParametersError(f"{ERROR_INVALID_IMAGE_SIZE} Valid sizes: {', '.join(valid_sizes)}")

        # Get the provider
        try:
            provider_instance = self._get_provider(provider, model_name, provider_api_key)
        except Exception as e:
            raise ProviderNotFoundError(f"{ERROR_PROVIDER_NOT_FOUND}: {str(e)}")

        # Make the request
        start_time = datetime.now()
        try:
            response = provider_instance.generate_image(
                prompt=prompt,
                size=size,
                n=n,
                quality=quality,
                style=style,
                **kwargs
            )
        except Exception as e:
            self._handle_provider_error(e)

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Create usage information
        usage = Usage(
            tokens_prompt=response.get("tokens_prompt", 0),
            tokens_completion=response.get("tokens_completion", 0),
            tokens_total=response.get("tokens_total", 0),
            cost=response.get("cost", 0.0),
            latency=duration,
            timestamp=datetime.now(),
        )

        # Create and return the response
        return ImageResponse(
            data=response.get("images", []),
            model=model_name,
            provider=provider,
            success=True,
            message="Successfully generated image",
            usage=usage,
            raw_response=response,
        )
