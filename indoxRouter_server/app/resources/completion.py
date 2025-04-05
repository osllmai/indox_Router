"""
Completion resource module for indoxRouter.
This module contains the Completions resource class for text completion functionality.
"""

from typing import Dict, List, Any, Optional, Union, Generator
import os
import time
from datetime import datetime
import uuid
from .base import BaseResource
from ..models import CompletionResponse, Usage
from ..providers import get_provider
from ..utils.model_info import calculate_cost
from ..constants import (
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    DEFAULT_FREQUENCY_PENALTY,
    DEFAULT_PRESENCE_PENALTY,
)
from ..exceptions import ProviderNotFoundError, InvalidParametersError


class Completions(BaseResource):
    """Resource class for text completion functionality."""

    def __call__(
        self,
        prompt: str,
        model: str,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        top_p: float = DEFAULT_TOP_P,
        frequency_penalty: float = DEFAULT_FREQUENCY_PENALTY,
        presence_penalty: float = DEFAULT_PRESENCE_PENALTY,
        provider_api_key: Optional[str] = None,
        stream: bool = False,
        # return_generator: bool = False,
        user_id: Optional[int] = None,
        api_key_id: Optional[int] = None,
        **kwargs,
    ) -> Union[CompletionResponse, Generator[str, None, None]]:
        """
        Send a completion request to a provider.

        Args:
            prompt: The prompt to complete.
            model: The model to use.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            top_p: The top_p value to use for generation.
            frequency_penalty: The frequency penalty to use for generation.
            presence_penalty: The presence penalty to use for generation.
            provider_api_key: Optional API key for the provider. If not provided, uses the configured key.
            stream: Whether to stream the response. Default is False.
            # return_generator: Whether to return a generator that yields chunks of the response. Only applicable when stream=True.
            user_id: Optional user ID for tracking usage and credits.
            api_key_id: Optional API key ID for tracking usage and credits.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            A CompletionResponse object containing the response from the provider.
            If stream=True and return_generator=True, returns a generator that yields chunks of the response.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
            InvalidParametersError: If the parameters are invalid.
            RequestError: If the request to the provider fails.
        """

        # Get the provider and model
        provider, model_name = model.split("/", 1)

        # Get the provider API key
        if not provider_api_key:
            provider_api_key = os.getenv(f"{provider.upper()}_API_KEY")

        # Get the provider implementation
        provider_impl = get_provider(provider, provider_api_key, model_name)

        # Send the request to the provider
        start_time = time.time()
        try:
            # Remove api_key_id from kwargs as it's not expected by the provider
            if "api_key_id" in kwargs:
                del kwargs["api_key_id"]

            response = provider_impl.complete(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=stream,
                # return_generator=return_generator,
                **kwargs,
            )
        except Exception as e:
            self._handle_provider_error(e)

        # Calculate request duration
        duration = time.time() - start_time

        # If return_generator is True and we got a generator, return it directly
        # if (
        #     return_generator
        #     and stream
        #     and hasattr(response, "__iter__")
        #     and hasattr(response, "__next__")
        # ):
        #     # Return the generator directly - it's already a StreamingGenerator
        #     # that handles usage tracking internally
        #     return response

        # If the response is a dictionary, convert it to a CompletionResponse object
        if isinstance(response, dict):
            # Create Usage object from response
            usage_data = response.get("usage", {})

            # Parse timestamp if it's a string
            timestamp = response.get("timestamp")
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()

            # Extract usage information with fallbacks for different formats
            tokens_prompt = usage_data.get("prompt_tokens", 0)
            tokens_completion = usage_data.get("completion_tokens", 0)
            tokens_total = usage_data.get("total_tokens", 0)

            # Calculate cost based on token usage and model information
            cost = calculate_cost(
                provider=provider,
                model_name=model_name,
                tokens_prompt=tokens_prompt,
                tokens_completion=tokens_completion,
            )

            usage = Usage(
                tokens_prompt=tokens_prompt,
                tokens_completion=tokens_completion,
                tokens_total=tokens_total,
                cost=cost,
                latency=duration,
                timestamp=timestamp,
            )

            # Extract content from the first choice if available
            data = ""
            choices = response.get("choices", [])
            if choices and len(choices) > 0:
                # Handle different response formats
                if "text" in choices[0]:
                    # OpenAI completion format
                    data = choices[0].get("text", "")
                elif "message" in choices[0]:
                    # Chat format
                    message = choices[0].get("message", {})
                    data = message.get("content", "")
                else:
                    # Try to get any text content
                    data = str(choices[0].get("content", ""))

            # Set success based on whether we have choices
            success = bool(choices)

            # Update user credit if user_id is provided
            if user_id:
                # Log the request in the database
                from app.db.database import log_api_request, log_model_usage

                # Generate a unique request ID for tracking
                request_id = str(uuid.uuid4())
                
                # Log to PostgreSQL
                log_api_request(
                    user_id=user_id,
                    api_key_id=api_key_id,
                    request_id=request_id,
                    endpoint="completion",
                    model=model_name,
                    provider=provider,
                    tokens_input=tokens_prompt,
                    tokens_output=tokens_completion,
                    cost=cost,
                    duration_ms=int(duration * 1000),
                    status_code=200,
                    response_summary=data[:100] if data else None,
                )
                
                # Log to MongoDB for usage analytics
                log_model_usage(
                    user_id=user_id,
                    provider=provider,
                    model=model_name,
                    tokens_prompt=tokens_prompt,
                    tokens_completion=tokens_completion,
                    cost=cost,
                    latency=duration,
                    request_id=request_id
                )

                # Update user credit
                self._update_user_credit(
                    user_id=user_id,
                    cost=cost,
                    endpoint="completion",
                    tokens_input=tokens_prompt,
                    tokens_output=tokens_completion,
                    model=model_name,
                    provider=provider,
                )

            return CompletionResponse(
                request_id=str(uuid.uuid4()),
                created_at=datetime.now().isoformat(),
                duration_ms=duration * 1000,  # Convert to milliseconds
                data=data,
                model=response.get("model", model_name),
                provider=provider,
                success=success,
                message=response.get("message", ""),
                usage=usage,
                finish_reason=response.get("finish_reason", None),
                raw_response=response.get("raw_response", None),
            )

        return response
