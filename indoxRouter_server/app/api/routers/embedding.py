"""
Embedding router for the IndoxRouter server.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Union

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.models.schemas import EmbeddingRequest, EmbeddingResponse
from app.api.dependencies import get_current_user, get_provider_api_key
from app.resources import Embeddings
from app.exceptions import InsufficientCreditsError
from app.utils.cache import get_cached_response, cache_response

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


@router.post("", response_model=EmbeddingResponse)
async def create_embedding(
    request: EmbeddingRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create embeddings for text.

    Args:
        request: The embedding request.
        current_user: The current user.

    Returns:
        The embedding response.
    """
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Get provider and model
    provider_id = request.provider or settings.DEFAULT_PROVIDER
    model_id = request.model or settings.DEFAULT_EMBEDDING_MODEL

    # Check if model_id already includes provider info (e.g., "openai/text-embedding-ada-002")
    if "/" in model_id:
        # Extract provider from model string if present
        extracted_provider, extracted_model = model_id.split("/", 1)
        provider_id = extracted_provider
        model_id = extracted_model

    model = f"{provider_id}/{model_id}"

    # Check if response is cached
    cached_response = None
    if settings.ENABLE_RESPONSE_CACHE:
        cached_response = get_cached_response(
            endpoint="embeddings",
            provider=provider_id,
            model=model_id,
            input_data=request.text,
            params=request.additional_params,
        )

        if cached_response:
            # Add request_id and timing information
            cached_response["request_id"] = request_id
            cached_response["created_at"] = datetime.now().isoformat()
            cached_response["duration_ms"] = 0  # Effectively instant

            # Return cached response
            return cached_response

    # Get API key for the provider
    api_key = get_provider_api_key(provider_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key not configured for provider '{provider_id}'",
        )

    try:
        # Create an Embeddings resource instance
        embeddings_resource = Embeddings()

        # Get embeddings
        response = embeddings_resource(
            text=request.text,
            model=model,
            provider_api_key=api_key,
            user_id=current_user.get("id"),
            **request.additional_params,
        )

        # Calculate request duration
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Prepare the response
        result = {
            "request_id": request_id,
            "created_at": datetime.now().isoformat(),
            "duration_ms": duration,
            "provider": response.provider,
            "model": response.model,
            "success": response.success,
            "message": response.message,
            "data": response.data,
            "dimensions": response.dimensions,
            "usage": response.usage,
            "raw_response": response.raw_response,
        }

        # Cache the response if applicable
        if settings.ENABLE_RESPONSE_CACHE and response.success:
            cache_response(
                endpoint="embeddings",
                provider=provider_id,
                model=model_id,
                input_data=request.text,
                response=result,
                params=request.additional_params,
            )

        return result
    except Exception as e:
        # Handle specific errors
        if isinstance(e, InsufficientCreditsError):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits for this request",
            )

        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
