"""
Image resource module for indoxRouter.
This module contains the Images resource class for image generation functionality.
"""

import os
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseResource
from ..models import ImageResponse, Usage
from ..providers import get_provider
from ..utils.model_info import calculate_cost, get_model_info
from ..constants import (
    DEFAULT_IMAGE_SIZE,
    DEFAULT_IMAGE_COUNT,
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_IMAGE_STYLE,
    ERROR_INVALID_PARAMETERS,
    ERROR_PROVIDER_NOT_FOUND,
    ERROR_INVALID_IMAGE_SIZE,
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
        user_id: Optional[int] = None,
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
            user_id: Optional user ID for tracking usage and credits.
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
            raise InvalidParametersError(
                f"{ERROR_INVALID_PARAMETERS}: prompt must be a string"
            )

        # Split provider and model name correctly
        try:
            provider, model_name = model.split("/", 1)
        except ValueError:
            raise InvalidParametersError(
                f"{ERROR_INVALID_PARAMETERS}: Model must be in format 'provider/model-name'"
            )

        # Validate image size
        valid_sizes = ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
        if size not in valid_sizes:
            raise InvalidParametersError(
                f"{ERROR_INVALID_IMAGE_SIZE} Valid sizes: {', '.join(valid_sizes)}"
            )

        # Get the provider API key
        if not provider_api_key:
            provider_api_key = os.getenv(f"{provider.upper()}_API_KEY")

        # Get the provider
        try:
            provider_instance = get_provider(provider, provider_api_key, model_name)
        except Exception as e:
            raise ProviderNotFoundError(f"{ERROR_PROVIDER_NOT_FOUND}: {str(e)}")

        # Make the request
        start_time = time.time()
        try:
            # Remove MongoDB logging specific parameters that shouldn't be passed to the provider
            mongo_specific_params = [
                "client_info",
                "session_id",
                "content_analysis",
                "performance_metrics",
            ]

            # Create a clean copy of kwargs without MongoDB-specific parameters
            filtered_kwargs = {
                k: v for k, v in kwargs.items() if k not in mongo_specific_params
            }

            response = provider_instance.generate_image(
                prompt=prompt,
                size=size,
                n=n,
                quality=quality,
                style=style,
                **filtered_kwargs,
            )
        except Exception as e:
            self._handle_provider_error(e)

        # Calculate duration
        duration = time.time() - start_time

        # For image generation, we need to calculate cost differently
        # Get model info to determine the cost per image
        model_info = get_model_info(provider, model_name)

        # Default cost if model info is not found
        cost = 0.02 * n  # Default cost per image

        # If model info is found, use the pricing from it
        if model_info:
            # Some providers have different pricing based on size and quality
            # For simplicity, we'll use a base cost and adjust based on size and quality
            base_cost = model_info.get("inputPricePer1KTokens", 0.0)

            # Adjust cost based on size
            size_multiplier = 1.0
            if size == "256x256":
                size_multiplier = 0.5
            elif size == "512x512":
                size_multiplier = 0.75
            elif size == "1024x1024":
                size_multiplier = 1.0
            elif size in ["1792x1024", "1024x1792"]:
                size_multiplier = 1.5

            # Adjust cost based on quality
            quality_multiplier = 1.0
            if quality == "hd":
                quality_multiplier = 1.5

            # Calculate final cost
            cost = base_cost * size_multiplier * quality_multiplier * n

            # If cost is still 0, use the default
            if cost == 0:
                cost = 0.02 * n

        # Create usage information
        tokens_prompt = response.get("tokens_prompt", 0)
        tokens_completion = response.get("tokens_completion", 0)
        tokens_total = response.get("total_tokens", tokens_prompt + tokens_completion)

        usage = Usage(
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            tokens_total=tokens_total,
            cost=cost,
            latency=duration,
            timestamp=datetime.now(),
        )

        # Update user credit if user_id is provided
        if user_id:
            # Import logging functions
            from app.db.database import log_api_request, log_model_usage

            # Generate a unique request ID for tracking
            request_id = str(uuid.uuid4())

            # Log to PostgreSQL
            log_api_request(
                user_id=user_id,
                api_key_id=None,
                request_id=request_id,
                endpoint="image",
                model=model_name,
                provider=provider,
                tokens_input=tokens_prompt,
                tokens_output=tokens_completion,
                cost=cost,
                duration_ms=int(duration * 1000),
                status_code=200,
                response_summary=f"Generated {n} images with prompt: {prompt[:50]}...",
            )

            # Log to MongoDB for usage analytics
            log_model_usage(
                user_id=user_id,
                provider=provider,
                model=model_name,
                tokens_prompt=tokens_prompt,
                tokens_completion=tokens_completion,
                cost=cost,
                latency=duration,
                request_id=request_id,
                # Add enhanced data for MongoDB
                session_id=kwargs.get("session_id", None),
                request_data={
                    "endpoint": "image",
                    "prompt": prompt,
                    "parameters": {
                        "size": size,
                        "n": n,
                        "quality": quality,
                        "style": style,
                        **kwargs,
                    },
                },
                response_data={
                    "status_code": 200,
                    "image_count": len(response.get("images", [])),
                    "image_format": response.get("format", "url"),
                },
                client_info=kwargs.get("client_info", None),
                performance_metrics={
                    "total_request_time": duration,
                    "model_inference_time": duration
                    * 0.98,  # Image generation is mostly inference
                    "processing_time": duration * 0.02,
                },
                content_analysis={
                    "prompt_type": "image_generation",
                    "prompt_length": len(prompt),
                },
            )

            # Update user credit
            self._update_user_credit(
                user_id=user_id,
                cost=cost,
                endpoint="image",
                tokens_input=tokens_prompt,
                tokens_output=tokens_completion,
                model=model_name,
                provider=provider,
            )

        # Create and return the response
        return ImageResponse(
            request_id=str(uuid.uuid4()),
            created_at=datetime.now().isoformat(),
            duration_ms=duration * 1000,  # Convert to milliseconds
            data=response.get("images", []),
            model=model_name,
            provider=provider,
            success=True,
            message="Successfully generated image",
            usage=usage,
            raw_response=response,
        )
