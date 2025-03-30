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
from app.resources import Images

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
    model_id = request.model or settings.DEFAULT_IMAGE_MODEL
    model = f"{provider_id}/{model_id}"

    # Get API key for the provider
    api_key = get_provider_api_key(provider_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key not configured for provider '{provider_id}'",
        )

    try:
        # Create an Images resource instance
        images_resource = Images()

        # Generate images
        response = images_resource(
            prompt=request.prompt,
            model=model,
            size=request.size,
            n=request.n,
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
            "usage": response.usage,
            "raw_response": response.raw_response,
        }
    except Exception as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
