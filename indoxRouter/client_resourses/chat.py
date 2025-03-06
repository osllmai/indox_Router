"""
Chat resource module for indoxRouter.
This module contains the Chat resource class for chat-related functionality.
"""

import time
import os
from typing import Dict, List, Any, Optional, Union, Generator
from datetime import datetime
from .base import BaseResource
from ..models import ChatMessage, ChatResponse, Usage
from ..providers import get_provider
from ..constants import (
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    DEFAULT_FREQUENCY_PENALTY,
    DEFAULT_PRESENCE_PENALTY,
)
from ..exceptions import ProviderNotFoundError, InvalidParametersError


class Chat(BaseResource):
    """Resource class for chat-related functionality."""

    def __call__(
        self,
        messages: List[Union[Dict[str, str], ChatMessage]],
        model: str,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        top_p: float = DEFAULT_TOP_P,
        frequency_penalty: float = DEFAULT_FREQUENCY_PENALTY,
        presence_penalty: float = DEFAULT_PRESENCE_PENALTY,
        provider_api_key: Optional[str] = None,
        stream: bool = False,
        return_generator: bool = False,
        **kwargs,
    ) -> Union[ChatResponse, Generator[str, None, None]]:
        """
        Send a chat request to a provider.

        Args:
            messages: A list of messages to send to the provider.
            model: The model to use.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            top_p: The top_p value to use for generation.
            frequency_penalty: The frequency penalty to use for generation.
            presence_penalty: The presence penalty to use for generation.
            provider_api_key: Optional API key for the provider. If not provided, uses the configured key.
            stream: Whether to stream the response. Default is False.
            return_generator: Whether to return a generator that yields chunks of the response. Only applicable when stream=True.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            A ChatResponse object containing the response from the provider.
            If stream=True and return_generator=True, returns a generator that yields chunks of the response.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
            InvalidParametersError: If the parameters are invalid.
            RequestError: If the request to the provider fails.
        """
        # Convert messages to ChatMessage objects if they are dictionaries
        chat_messages = []
        for message in messages:
            if isinstance(message, dict):
                chat_messages.append(ChatMessage(**message))
            else:
                chat_messages.append(message)
        # Get the provider and model
        provider, model_name = model.split("/")

        # Get the provider API key
        provider_api_key = os.getenv(f"{provider.upper()}_API_KEY")
        # Get the provider implementation
        provider_impl = get_provider(provider, provider_api_key, model_name)

        # Send the request to the provider
        response = provider_impl.chat(
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
            return_generator=return_generator,
            **kwargs,
        )

        # If return_generator is True and we got a generator, return it directly
        if (
            return_generator
            and stream
            and hasattr(response, "__iter__")
            and hasattr(response, "__next__")
        ):
            # Return the generator directly - it's already a StreamingGenerator
            # that handles usage tracking internally
            return response

        # If the response is a dictionary, convert it to a ChatResponse object
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
            tokens_prompt = usage_data.get("tokens_prompt", 0)
            tokens_completion = usage_data.get("tokens_completion", 0)
            tokens_total = usage_data.get("tokens_total", 0)

            usage = Usage(
                tokens_prompt=tokens_prompt,
                tokens_completion=tokens_completion,
                tokens_total=tokens_total,
                cost=response.get("cost", 0.0),
                latency=0.0,  # We don't have latency in the dictionary
                timestamp=timestamp,
            )

            return ChatResponse(
                data=response.get("data", ""),
                model=response.get("model", model_name),
                provider=provider,
                success=response.get("success", False),
                message=response.get("message", ""),
                usage=usage,
                finish_reason=response.get("finish_reason", None),
                raw_response=response.get("raw_response", None),
            )
        return response
