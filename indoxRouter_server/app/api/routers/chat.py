"""
Chat router for the IndoxRouter server.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.api.dependencies import get_current_user, get_provider_api_key
from app.providers.factory import get_provider

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/completions", response_model=ChatResponse)
async def create_chat_completion(
    request: ChatRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a chat completion.

    Args:
        request: The chat completion request.
        current_user: The current user.

    Returns:
        The chat completion response.
    """
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Get provider and model
    provider_id = request.provider or settings.DEFAULT_PROVIDER
    model_id = request.model or settings.DEFAULT_CHAT_MODEL

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

        # Process messages
        messages = [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        # Create parameters
        params = {
            "temperature": request.temperature,
        }

        if request.max_tokens:
            params["max_tokens"] = request.max_tokens

        # Add any additional parameters
        if request.additional_params:
            params.update(request.additional_params)

        # Handle streaming if requested
        if request.stream:

            async def generate_stream():
                async for chunk in provider.chat_stream(messages, **params):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
            )

        # Get the chat completion
        result = provider.chat(messages, **params)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Format the response
        response = {
            "request_id": request_id,
            "created_at": datetime.utcnow().isoformat(),
            "duration_ms": duration_ms,
            "provider": provider_id,
            "model": model_id,
            "choices": result["choices"],
            "usage": result.get("usage"),
        }

        return response

    except Exception as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
