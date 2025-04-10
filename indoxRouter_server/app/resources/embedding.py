"""
Embedding resource module for indoxRouter.
This module contains the Embeddings resource class for embedding functionality.
"""

from typing import Dict, List, Any, Optional, Union
import os
import time
from datetime import datetime
from .base import BaseResource
from ..models import EmbeddingResponse, Usage
from ..providers import get_provider
from ..utils.model_info import calculate_cost
from ..constants import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_DIMENSIONS,
    ERROR_INVALID_PARAMETERS,
    ERROR_PROVIDER_NOT_FOUND,
)
from ..exceptions import ProviderNotFoundError, InvalidParametersError
import uuid
from app.db.database import log_api_request, log_model_usage


class Embeddings(BaseResource):
    """Resource class for embedding functionality."""

    def __call__(
        self,
        text: Union[str, List[str]],
        model: str,
        provider_api_key: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> EmbeddingResponse:
        """
        Generate embeddings for text.

        Args:
            text: The text to embed. Can be a string or list of strings.
            model: The model to use, in the format 'provider/model-name'.
            provider_api_key: Optional API key for the provider. If not provided, uses the configured key.
            user_id: Optional user ID for tracking usage and credits.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            An EmbeddingResponse object containing the embeddings.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
            InvalidParametersError: If the parameters are invalid.
        """
        # Split provider and model name correctly
        try:
            provider, model_name = model.split("/", 1)
        except ValueError:
            raise InvalidParametersError(
                f"{ERROR_INVALID_PARAMETERS}: Model must be in format 'provider/model-name'"
            )

        # Validate text parameter
        if not isinstance(text, (str, list)):
            raise InvalidParametersError(
                f"{ERROR_INVALID_PARAMETERS}: text must be a string or list of strings"
            )

        if isinstance(text, list) and not all(isinstance(t, str) for t in text):
            raise InvalidParametersError(
                f"{ERROR_INVALID_PARAMETERS}: all items in text list must be strings"
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

            response = provider_instance.embed(text=text, **filtered_kwargs)
        except Exception as e:
            self._handle_provider_error(e)

        # Calculate duration
        duration = time.time() - start_time

        # Extract usage information
        tokens_prompt = response.get("tokens_prompt", 0)
        tokens_total = response.get("total_tokens", tokens_prompt)

        # Calculate cost based on token usage and model information
        cost = calculate_cost(
            provider=provider,
            model_name=model_name,
            tokens_prompt=tokens_prompt,
            tokens_completion=0,  # Embeddings don't have completion tokens
        )

        # Create usage information
        usage = Usage(
            tokens_prompt=tokens_prompt,
            tokens_completion=0,  # Embeddings don't have completion tokens
            tokens_total=tokens_total,
            cost=cost,
            latency=duration,
            timestamp=datetime.now(),
        )

        # Update user credit if user_id is provided
        if user_id:
            # Generate a unique request ID for tracking
            request_id = str(uuid.uuid4())

            # Log to PostgreSQL
            log_api_request(
                user_id=user_id,
                api_key_id=None,
                request_id=request_id,
                endpoint="embedding",
                model=model_name,
                provider=provider,
                tokens_input=tokens_total,
                tokens_output=0,
                cost=cost,
                duration_ms=int(duration * 1000),
                status_code=200,
                response_summary=f"Embedding dimensions: {response.get('dimensions', DEFAULT_EMBEDDING_DIMENSIONS)}",
            )

            # Log to MongoDB for usage analytics
            log_model_usage(
                user_id=user_id,
                provider=provider,
                model=model_name,
                tokens_prompt=tokens_total,
                tokens_completion=0,
                cost=cost,
                latency=duration,
                request_id=request_id,
                # Add enhanced data for MongoDB
                session_id=kwargs.get("session_id", None),
                request_data={
                    "endpoint": "embedding",
                    "text": (
                        text
                        if isinstance(text, str)
                        else f"[Array of {len(text)} texts]"
                    ),
                    "text_count": 1 if isinstance(text, str) else len(text),
                    "parameters": kwargs,
                },
                response_data={
                    "status_code": 200,
                    "dimensions": response.get(
                        "dimensions", DEFAULT_EMBEDDING_DIMENSIONS
                    ),
                    "embeddings_count": len(response.get("embeddings", [])),
                },
                client_info=kwargs.get("client_info", None),
                performance_metrics={
                    "total_request_time": duration,
                    "model_inference_time": duration * 0.95,  # Estimated inference time
                    "processing_time": duration * 0.05,  # Estimated processing time
                },
                content_analysis=None,  # Embeddings typically don't have content analysis
            )

            # Update user credit
            self._update_user_credit(
                user_id=user_id,
                cost=cost,
                endpoint="embedding",
                tokens_input=tokens_total,
                tokens_output=0,
                model=model_name,
                provider=provider,
            )

        # Get dimensions from the response or use default
        dimensions = response.get("dimensions", DEFAULT_EMBEDDING_DIMENSIONS)

        # Create and return the response
        return EmbeddingResponse(
            request_id=str(uuid.uuid4()),
            created_at=datetime.now().isoformat(),
            duration_ms=duration * 1000,  # Convert to milliseconds
            data=response.get("embeddings", []),
            model=model_name,
            provider=provider,
            success=True,
            message="Successfully generated embeddings",
            usage=usage,
            dimensions=dimensions,
            raw_response=response,
        )
