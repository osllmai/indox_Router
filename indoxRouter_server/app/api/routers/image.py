"""
Image router for the IndoxRouter server.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.models.schemas import ImageRequest, ImageResponse
from app.api.dependencies import get_current_user, get_provider_api_key
from app.providers.factory import get_provider

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/generations", response_model=ImageResponse)
async def create_image(
    request: ImageRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate images from a prompt.

    Args:
        request: The image generation request.
        current_user: The current user.

    Returns:
        The image generation response.
    """
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Get provider and model
    provider_id = request.provider or settings.DEFAULT_PROVIDER
    model_id = request.model or "dall-e-3"  # Default to DALL-E 3 if not specified

    # Get API key for the provider
    api_key = get_provider_api_key(provider_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key not configured for provider '{provider_id}'",
        )

    try:
        # Initialize the provider
        provider = get_provider(provider_id, api_key, model_id)

        # Create parameters
        params = {
            "size": request.size,
            "n": request.n,
        }

        # Add any additional parameters
        if request.additional_params:
            params.update(request.additional_params)

        # Generate the images
        result = provider.generate_image(request.prompt, **params)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Format the response
        response = {
            "request_id": request_id,
            "created_at": datetime.utcnow().isoformat(),
            "duration_ms": duration_ms,
            "provider": provider_id,
            "model": model_id,
            "images": result["images"],
            "usage": result.get("usage"),
        }

        return response

    except Exception as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
