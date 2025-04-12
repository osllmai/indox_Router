"""
Completion router for the IndoxRouter server.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.models.schemas import CompletionRequest, CompletionResponse
from app.api.dependencies import get_current_user, get_provider_api_key
from app.resources import Completions
from app.exceptions import InsufficientCreditsError

router = APIRouter(prefix="/completions", tags=["Completions"])


@router.post("", response_model=CompletionResponse)
async def create_completion(
    request: CompletionRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a text completion.

    Args:
        request: The completion request.
        current_user: The current user.

    Returns:
        The completion response.
    """
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Get provider and model
    model_id = request.model or settings.DEFAULT_COMPLETION_MODEL

    # Check if model already includes provider prefix
    if "/" in model_id:
        # Model includes provider, extract it
        provider_id, model_name = model_id.split("/", 1)
    else:
        # Use specified provider or default
        provider_id = request.provider or settings.DEFAULT_PROVIDER
        model_name = model_id

    # Construct full model string
    model = f"{provider_id}/{model_name}"

    # Get API key for the provider
    api_key = get_provider_api_key(provider_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key not configured for provider '{provider_id}'",
        )

    try:
        # Create a Completions resource instance
        completions_resource = Completions()

        # Handle streaming responses
        if request.stream:
            # Create a streaming response
            async def generate_stream():
                # Call the Completions resource with streaming enabled
                generator = completions_resource(
                    prompt=request.prompt,
                    model=model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_p=request.top_p,
                    frequency_penalty=request.frequency_penalty,
                    presence_penalty=request.presence_penalty,
                    provider_api_key=api_key,
                    stream=True,
                    # return_generator=True,
                    user_id=current_user.get("id"),
                    api_key_id=current_user.get("api_key_id"),
                    **request.additional_params,
                )

                # Yield each chunk from the generator
                for chunk in generator:
                    yield f"data: {chunk}\n\n"

                # End the stream
                yield "data: [DONE]\n\n"

            # Return a streaming response
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
            )

        # Handle non-streaming responses
        response = completions_resource(
            prompt=request.prompt,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            provider_api_key=api_key,
            user_id=current_user.get("id"),
            api_key_id=current_user.get("api_key_id"),
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
            "finish_reason": response.finish_reason,
            "usage": response.usage,
            "raw_response": response.raw_response,
        }
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
