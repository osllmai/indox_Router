"""
Embedding resource module for indoxRouter.
This module contains the Embeddings resource class for embedding functionality.
"""

from typing import Dict, List, Any, Optional, Union
import os
from datetime import datetime
from .base import BaseResource
from ..models import EmbeddingResponse, Usage
from ..providers import get_provider
from ..constants import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_DIMENSIONS,
    ERROR_INVALID_PARAMETERS,
    ERROR_PROVIDER_NOT_FOUND
)
from ..exceptions import ProviderNotFoundError, InvalidParametersError


class Embeddings(BaseResource):
    """Resource class for embedding functionality."""

    def __call__(
        self,
        text: Union[str, List[str]],
        model: str,
        provider_api_key: Optional[str] = None,
        **kwargs,
    ) -> EmbeddingResponse:
        # Split provider and model name correctly
        try:
            provider, model_name = model.split("/", 1)
        except ValueError:
            raise InvalidParametersError(f"{ERROR_INVALID_PARAMETERS}: Model must be in format 'provider/model-name'")

        # Validate text parameter
        if not isinstance(text, (str, list)):
            raise InvalidParametersError(f"{ERROR_INVALID_PARAMETERS}: text must be a string or list of strings")
        
        if isinstance(text, list) and not all(isinstance(t, str) for t in text):
            raise InvalidParametersError(f"{ERROR_INVALID_PARAMETERS}: all items in text list must be strings")

        # Get the provider
        try:
            provider_instance = self._get_provider(provider, model_name, provider_api_key)
        except Exception as e:
            raise ProviderNotFoundError(f"{ERROR_PROVIDER_NOT_FOUND}: {str(e)}")

        # Make the request
        start_time = datetime.now()
        try:
            response = provider_instance.embed(text=text, **kwargs)
        except Exception as e:
            self._handle_provider_error(e)

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Create usage information
        usage = Usage(
            tokens_prompt=response.get("tokens_prompt", 0),
            tokens_completion=0,  # Embeddings don't have completion tokens
            tokens_total=response.get("tokens_total", 0),
            cost=response.get("cost", 0.0),
            latency=duration,
            timestamp=datetime.now(),
        )

        # Get dimensions from the response or use default
        dimensions = response.get("dimensions", DEFAULT_EMBEDDING_DIMENSIONS)

        # Create and return the response
        return EmbeddingResponse(
            data=response.get("embeddings", []),
            model=model_name,
            provider=provider,
            success=True,
            message="Successfully generated embeddings",
            usage=usage,
            dimensions=dimensions,
            raw_response=response,
        )
