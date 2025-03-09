"""
IndoxRouter Client Module

This module provides a client for interacting with the IndoxRouter API, which serves as a unified
interface to multiple AI providers and models. The client handles authentication, rate limiting,
error handling, and provides a standardized response format across different AI services.

The Client class offers methods for:
- Authentication and session management
- Making API requests with automatic token refresh
- Accessing AI capabilities: chat completions, text completions, embeddings, and image generation
- Retrieving information about available providers and models
- Monitoring usage statistics

Usage example:
    ```python
    from indoxRouter import Client

    # Initialize client with API key
    client = Client(api_key="your_api_key")

    # Get available models
    models = client.models()

    # Generate a chat completion
    response = client.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ], provider="openai", model="gpt-3.5-turbo")

    # Generate text embeddings
    embeddings = client.embeddings("This is a sample text")

    # Clean up resources when done
    client.close()
    ```

The client can also be used as a context manager:
    ```python
    with Client(api_key="your_api_key") as client:
        response = client.chat([{"role": "user", "content": "Hello!"}])
    ```
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import requests
import json
from uuid import uuid4

from .exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidParametersError,
)
from .constants import (
    DEFAULT_API_VERSION,
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
)

logger = logging.getLogger(__name__)


class Client:
    """
    Client for the IndoxRouter API that provides a unified interface to multiple AI providers.

    The Client class handles:
    - Authentication and token management with automatic refresh
    - Rate limiting and quota tracking
    - Standardized error handling across providers
    - Unified response format for all AI capabilities
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the IndoxRouter client.

        Args:
            api_key: API key for authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = DEFAULT_BASE_URL
        self.api_version = DEFAULT_API_VERSION
        self.timeout = timeout
        self.session = requests.Session()

        # Set API key
        self.api_key = api_key or os.environ.get("INDOXROUTER_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key must be provided either as an argument or as the INDOXROUTER_API_KEY environment variable"
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Any:
        """
        Make a request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            stream: Whether to stream the response

        Returns:
            Response data
        """
        url = f"{self.base_url}/api/{self.api_version}/{endpoint.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=self.timeout,
                stream=stream,
            )

            if stream and response.status_code == 200:
                return response

            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except (ValueError, AttributeError):
                pass

            status_code = getattr(e.response, "status_code", 500)
            error_message = error_data.get("detail", str(e))

            if status_code == 401:
                raise AuthenticationError(f"Authentication failed: {error_message}")
            elif status_code == 404:
                if "provider" in error_message.lower():
                    raise ProviderNotFoundError(error_message)
                elif "model" in error_message.lower():
                    raise ModelNotFoundError(error_message)
                else:
                    raise NetworkError(f"Resource not found: {error_message}")
            elif status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {error_message}")
            elif status_code == 400:
                raise InvalidParametersError(f"Invalid parameters: {error_message}")
            else:
                raise ProviderError(f"Provider error: {error_message}")
        except requests.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion.

        Args:
            messages: List of messages in the conversation
            provider: Provider to use (e.g., "openai", "anthropic")
            model: Model to use (e.g., "gpt-3.5-turbo", "claude-2")
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the provider

        Returns:
            Chat completion response
        """
        data = {
            "messages": messages,
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "additional_params": kwargs,
        }

        if stream:
            response = self._request("POST", "chat/completions", data, stream=True)
            return self._handle_streaming_response(response)
        else:
            return self._request("POST", "chat/completions", data)

    def completion(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a text completion.

        Args:
            prompt: Text prompt
            provider: Provider to use (e.g., "openai", "anthropic")
            model: Model to use (e.g., "gpt-3.5-turbo-instruct", "claude-instant-1")
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the provider

        Returns:
            Text completion response
        """
        data = {
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "additional_params": kwargs,
        }

        if stream:
            response = self._request("POST", "completions", data, stream=True)
            return self._handle_streaming_response(response)
        else:
            return self._request("POST", "completions", data)

    def embeddings(
        self,
        text: Union[str, List[str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate embeddings for text.

        Args:
            text: Text to embed (string or list of strings)
            provider: Provider to use (e.g., "openai", "cohere")
            model: Model to use (e.g., "text-embedding-ada-002")
            **kwargs: Additional parameters to pass to the provider

        Returns:
            Embeddings response
        """
        data = {
            "text": text,
            "provider": provider,
            "model": model,
            "additional_params": kwargs,
        }

        return self._request("POST", "embeddings", data)

    def images(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        size: str = "1024x1024",
        n: int = 1,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text prompt
            provider: Provider to use (e.g., "openai")
            model: Model to use (e.g., "dall-e-3")
            size: Image size (e.g., "1024x1024")
            n: Number of images to generate
            **kwargs: Additional parameters to pass to the provider

        Returns:
            Image generation response
        """
        data = {
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "size": size,
            "n": n,
            "additional_params": kwargs,
        }

        return self._request("POST", "images/generations", data)

    def models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available models.

        Args:
            provider: Provider to get models for

        Returns:
            List of available models
        """
        if provider:
            return self._request("GET", f"models/{provider}")
        else:
            return self._request("GET", "models")

    def _handle_streaming_response(self, response):
        """
        Handle a streaming response.

        Args:
            response: Streaming response

        Returns:
            Generator yielding response chunks
        """
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        yield {"text": data}

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()
