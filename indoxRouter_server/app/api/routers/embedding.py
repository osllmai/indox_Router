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
    model = f"{provider_id}/{model_id}"

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

        # Return the response
        return {
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
    except Exception as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
