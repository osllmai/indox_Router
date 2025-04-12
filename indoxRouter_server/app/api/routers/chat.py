"""
Chat router for the IndoxRouter server.
"""

import time
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.api.dependencies import get_current_user, get_provider_api_key
from app.resources import Chat

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/completions", response_model=ChatResponse)
async def create_chat_completion(
    request: Request,
    chat_request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a chat completion.

    Args:
        request: The FastAPI request object
        chat_request: The chat completion request.
        current_user: The current user.

    Returns:
        The chat completion response.
    """
    # Generate a unique request ID and session ID
    request_id = str(uuid.uuid4())
    session_id = chat_request.additional_params.get("session_id", str(uuid.uuid4()))
    start_time = time.time()

    # Get provider and model
    provider_id = chat_request.provider or settings.DEFAULT_PROVIDER
    model_id = chat_request.model or settings.DEFAULT_CHAT_MODEL

    # Check if model_id already includes provider info (e.g., "deepseek/deepseek-chat")
    if "/" in model_id:
        # Extract provider from model string if present
        extracted_provider, extracted_model = model_id.split("/", 1)
        provider_id = extracted_provider
        model_id = extracted_model

    model = f"{provider_id}/{model_id}"

    # Get API key for the provider
    api_key = get_provider_api_key(provider_id)

    if not api_key:
        available_providers = [
            p
            for p in ["openai", "mistral", "deepseek", "anthropic", "cohere", "google"]
            if getattr(settings, f"{p.upper()}_API_KEY", None)
        ]

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key not configured for provider '{provider_id}'. Available providers: {', '.join(available_providers)}",
        )

    # Capture client information
    client_info = {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "origin": request.headers.get("origin"),
        "referer": request.headers.get("referer"),
    }

    try:
        # Create a Chat resource instance
        chat_resource = Chat()

        # Handle streaming responses
        if chat_request.stream:
            # Create a streaming response
            async def generate_stream():
                # Call the Chat resource with streaming enabled
                try:
                    generator = chat_resource(
                        messages=chat_request.messages,
                        model=model,
                        temperature=chat_request.temperature,
                        max_tokens=chat_request.max_tokens,
                        provider_api_key=api_key,
                        stream=True,
                        user_id=current_user.get("id"),
                        api_key_id=current_user.get("api_key_id"),
                        client_info=client_info,
                        session_id=session_id,
                        **chat_request.additional_params,
                    )

                    # The generator we get back is already a synchronous generator
                    # that yields JSON-serialized strings
                    for chunk in generator:
                        # Simply yield the chunk with SSE format
                        yield f"data: {chunk}\n\n"

                except Exception as e:
                    # Handle any exceptions
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

                # End the stream
                yield "data: [DONE]\n\n"

            # Return a streaming response with proper headers
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        # Add processing time tracking
        processing_start = time.time()

        # Handle non-streaming responses
        response = chat_resource(
            messages=chat_request.messages,
            model=model,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            top_p=chat_request.top_p,
            frequency_penalty=chat_request.frequency_penalty,
            presence_penalty=chat_request.presence_penalty,
            provider_api_key=api_key,
            user_id=current_user.get("id"),
            api_key_id=current_user.get("api_key_id"),
            client_info=client_info,
            session_id=session_id,
            performance_metrics={
                "time_in_queue": processing_start - start_time,
            },
            **chat_request.additional_params,
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
        from app.exceptions import InsufficientCreditsError

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
