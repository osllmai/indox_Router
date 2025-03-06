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
            raise InvalidParametersError(
                "Model must be in format 'provider/model-name'"
            )

        # Get provider implementation with proper model name
        provider_api_key = provider_api_key or os.getenv(f"{provider.upper()}_API_KEY")
        provider_impl = get_provider(provider, provider_api_key, model_name)

        response = provider_impl.embed(text=text, **kwargs)

        if isinstance(response, dict):
            # Create Usage object from response
            usage_data = response.get("usage", {})

            if isinstance(usage_data, dict):
                # Parse timestamp if it's a string
                timestamp = usage_data.get("timestamp")
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
                cost = usage_data.get("cost", 0.0)

                usage = Usage(
                    tokens_prompt=tokens_prompt,
                    tokens_completion=tokens_completion,
                    tokens_total=tokens_total,
                    cost=cost,
                    latency=usage_data.get("latency", 0.0),
                    timestamp=timestamp,
                )
            else:
                # Create default Usage object
                usage = Usage()

            # Calculate dimensions if possible
            dimensions = 0
            if (
                response.get("data")
                and isinstance(response["data"], list)
                and len(response["data"]) > 0
            ):
                if (
                    isinstance(response["data"][0], dict)
                    and "embedding" in response["data"][0]
                ):
                    dimensions = len(response["data"][0]["embedding"])
                elif isinstance(response["data"][0], list):
                    dimensions = len(response["data"][0])

            return EmbeddingResponse(
                data=response.get("data"),
                model=model_name,
                provider=provider,
                success=response.get("success", True),
                message=response.get("message", "Successfully generated embeddings"),
                usage=usage,
                dimensions=dimensions,
                raw_response=response.get("raw_response"),
            )

        return response
