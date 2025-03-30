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
- Monitoring usage statistics and credit consumption

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
    ], model="openai/gpt-4o-mini")

    # Generate text embeddings
    embeddings = client.embeddings("This is a sample text", model="openai/text-embedding-ada-002")

    # Clean up resources when done
    client.close()
    ```

The client can also be used as a context manager:
    ```python
    with Client(api_key="your_api_key") as client:
        response = client.chat([{"role": "user", "content": "Hello!"}], model="openai/gpt-4o-mini")
    ```
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import requests
import json

from .exceptions import (
    AuthenticationError,
    NetworkError,
    ProviderNotFoundError,
    ModelNotFoundError,
    InvalidParametersError,
    RateLimitError,
    ProviderError,
    InsufficientCreditsError,
)
from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_IMAGE_MODEL,
    CHAT_ENDPOINT,
    COMPLETION_ENDPOINT,
    EMBEDDING_ENDPOINT,
    IMAGE_ENDPOINT,
    MODEL_ENDPOINT,
    USAGE_ENDPOINT,
)

logger = logging.getLogger(__name__)


class Client:
    """
    Client for interacting with the IndoxRouter API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the client.

        Args:
            api_key: API key for authentication. If not provided, the client will look for the
                INDOX_ROUTER_API_KEY environment variable.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key or os.environ.get("INDOX_ROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as an argument or as the INDOX_ROUTER_API_KEY environment variable."
            )

        self.base_url = DEFAULT_BASE_URL
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def enable_debug(self, level=logging.DEBUG):
        """
        Enable debug logging for the client.

        Args:
            level: Logging level (default: logging.DEBUG)
        """
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.debug("Debug logging enabled")

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
        # Add API version prefix if not already present
        if not endpoint.startswith("api/v1/") and not endpoint.startswith("/api/v1/"):
            endpoint = f"api/v1/{endpoint}"

        # Remove any leading slash for consistent URL construction
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        # logger.debug(f"Making {method} request to {url}")
        # if data:
        #     logger.debug(f"Request data: {json.dumps(data, indent=2)}")

        # Diagnose potential issues with the request
        if method == "POST" and data:
            diagnosis = self.diagnose_request(endpoint, data)
            if not diagnosis["is_valid"]:
                issues_str = "\n".join([f"- {issue}" for issue in diagnosis["issues"]])
                logger.warning(f"Request validation issues:\n{issues_str}")
                # We'll still send the request, but log the issues

        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                json=data,
                timeout=self.timeout,
                stream=stream,
            )

            if stream:
                return response

            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
                logger.error(f"HTTP error response: {json.dumps(error_data, indent=2)}")
            except (ValueError, AttributeError):
                error_data = {"detail": str(e)}
                logger.error(f"HTTP error (no JSON response): {str(e)}")

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
                    raise NetworkError(
                        f"Resource not found: {error_message} (URL: {url})"
                    )
            elif status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {error_message}")
            elif status_code == 400:
                raise InvalidParametersError(f"Invalid parameters: {error_message}")
            elif status_code == 402:
                raise InsufficientCreditsError(f"Insufficient credits: {error_message}")
            elif status_code == 500:
                # Provide more detailed information for server errors
                error_detail = error_data.get("detail", "No details provided")
                # Include the request data in the error message for better debugging
                request_data_str = json.dumps(data, indent=2) if data else "None"
                raise ProviderError(
                    f"Server error (500): {error_detail}. URL: {url}.\n"
                    f"Request data: {request_data_str}\n"
                    f"This may indicate an issue with the server configuration or a problem with the provider service."
                )
            else:
                raise ProviderError(f"Provider error ({status_code}): {error_message}")
        except requests.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise NetworkError(f"Network error: {str(e)}")

    def _format_model_string(self, model: str) -> str:
        """
        Format the model string in a way that the server expects.

        The server might be expecting a different format than "provider/model".
        This method handles different formatting requirements.

        Args:
            model: Model string in the format "provider/model"

        Returns:
            Formatted model string
        """
        if not model or "/" not in model:
            return model

        # The standard format is "provider/model"
        # But the server might be expecting something different
        provider, model_name = model.split("/", 1)

        # For now, return the original format as it seems the server
        # is having issues with JSON formatted model strings
        return model

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion.

        Args:
            messages: List of messages in the conversation
            model: Model to use in the format "provider/model" (e.g., "openai/gpt-4o-mini")
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        data = {
            "messages": messages,
            "model": formatted_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "additional_params": filtered_kwargs,
        }

        if stream:
            response = self._request("POST", CHAT_ENDPOINT, data, stream=True)
            return self._handle_streaming_response(response)
        else:
            return self._request("POST", CHAT_ENDPOINT, data)

    def completion(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a text completion.

        Args:
            prompt: Text prompt
            model: Model to use in the format "provider/model" (e.g., "openai/gpt-4o-mini")
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        data = {
            "prompt": prompt,
            "model": formatted_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "additional_params": filtered_kwargs,
        }

        if stream:
            response = self._request("POST", COMPLETION_ENDPOINT, data, stream=True)
            return self._handle_streaming_response(response)
        else:
            return self._request("POST", COMPLETION_ENDPOINT, data)

    def embeddings(
        self,
        text: Union[str, List[str]],
        model: str = DEFAULT_EMBEDDING_MODEL,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate embeddings for text.

        Args:
            text: Text to embed (string or list of strings)
            model: Model to use in the format "provider/model" (e.g., "openai/text-embedding-ada-002")
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data with embeddings
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        data = {
            "input": text if isinstance(text, list) else [text],
            "model": formatted_model,
            "additional_params": filtered_kwargs,
        }

        return self._request("POST", EMBEDDING_ENDPOINT, data)

    def images(
        self,
        prompt: str,
        model: str = DEFAULT_IMAGE_MODEL,
        size: str = "1024x1024",
        n: int = 1,
        quality: str = "standard",
        style: str = "vivid",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate images from a prompt.

        Args:
            prompt: Text prompt
            model: Model to use in the format "provider/model" (e.g., "openai/dall-e-3")
            size: Image size (e.g., "1024x1024")
            n: Number of images to generate
            quality: Image quality (e.g., "standard", "hd")
            style: Image style (e.g., "vivid", "natural")
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data with image URLs
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        data = {
            "prompt": prompt,
            "model": formatted_model,
            "n": n,
            "size": size,
            "quality": quality,
            "style": style,
            "additional_params": filtered_kwargs,
        }

        return self._request("POST", IMAGE_ENDPOINT, data)

    def models(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available models.

        Args:
            provider: Provider to filter by

        Returns:
            List of available models with pricing information
        """
        endpoint = MODEL_ENDPOINT
        if provider:
            endpoint = f"{MODEL_ENDPOINT}/{provider}"

        return self._request("GET", endpoint)

    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            provider: Provider ID
            model: Model ID

        Returns:
            Model information including pricing
        """
        return self._request("GET", f"{MODEL_ENDPOINT}/{provider}/{model}")

    def get_usage(self) -> Dict[str, Any]:
        """
        Get usage statistics for the current user.

        Returns:
            Usage statistics
        """
        return self._request("GET", USAGE_ENDPOINT)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the server and return server status information.

        This method can be used to diagnose connection issues and verify that
        the server is accessible and properly configured.

        Returns:
            Dictionary containing server status information
        """
        try:
            # Try to access the base URL
            response = self.session.get(self.base_url, timeout=self.timeout)

            # Try to get server info if available
            server_info = {}
            try:
                if response.headers.get("Content-Type", "").startswith(
                    "application/json"
                ):
                    server_info = response.json()
            except:
                pass

            return {
                "status": "connected",
                "url": self.base_url,
                "status_code": response.status_code,
                "server_info": server_info,
                "headers": dict(response.headers),
            }
        except requests.RequestException as e:
            return {
                "status": "error",
                "url": self.base_url,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def diagnose_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose potential issues with a request before sending it to the server.

        This method checks for common issues like malformed model strings,
        invalid message formats, or missing required parameters.

        Args:
            endpoint: API endpoint
            data: Request data

        Returns:
            Dictionary with diagnosis results
        """
        issues = []
        warnings = []

        # Check if this is a chat request
        if endpoint == CHAT_ENDPOINT:
            # Check model format
            if "model" in data:
                model = data["model"]
                # Check if the model is already formatted as JSON
                if (
                    isinstance(model, str)
                    and model.startswith("{")
                    and model.endswith("}")
                ):
                    try:
                        model_json = json.loads(model)
                        if (
                            not isinstance(model_json, dict)
                            or "provider" not in model_json
                            or "model" not in model_json
                        ):
                            issues.append(f"Invalid model JSON format: {model}")
                    except json.JSONDecodeError:
                        issues.append(f"Invalid model JSON format: {model}")
                elif not isinstance(model, str):
                    issues.append(f"Model must be a string, got {type(model).__name__}")
                elif "/" not in model:
                    issues.append(
                        f"Model '{model}' is missing provider prefix (should be 'provider/model')"
                    )
                else:
                    provider, model_name = model.split("/", 1)
                    if not provider or not model_name:
                        issues.append(
                            f"Invalid model format: '{model}'. Should be 'provider/model'"
                        )
            else:
                warnings.append("No model specified, will use default model")

            # Check messages format
            if "messages" in data:
                messages = data["messages"]
                if not isinstance(messages, list):
                    issues.append(
                        f"Messages must be a list, got {type(messages).__name__}"
                    )
                elif not messages:
                    issues.append("Messages list is empty")
                else:
                    for i, msg in enumerate(messages):
                        if not isinstance(msg, dict):
                            issues.append(
                                f"Message {i} must be a dictionary, got {type(msg).__name__}"
                            )
                        elif "role" not in msg:
                            issues.append(f"Message {i} is missing 'role' field")
                        elif "content" not in msg:
                            issues.append(f"Message {i} is missing 'content' field")
            else:
                issues.append("No messages specified")

        # Check if this is a completion request
        elif endpoint == COMPLETION_ENDPOINT:
            # Check model format (same as chat)
            if "model" in data:
                model = data["model"]
                if not isinstance(model, str):
                    issues.append(f"Model must be a string, got {type(model).__name__}")
                elif "/" not in model:
                    issues.append(
                        f"Model '{model}' is missing provider prefix (should be 'provider/model')"
                    )
            else:
                warnings.append("No model specified, will use default model")

            # Check prompt
            if "prompt" not in data:
                issues.append("No prompt specified")
            elif not isinstance(data["prompt"], str):
                issues.append(
                    f"Prompt must be a string, got {type(data['prompt']).__name__}"
                )

        # Return diagnosis results
        return {
            "endpoint": endpoint,
            "issues": issues,
            "warnings": warnings,
            "is_valid": len(issues) == 0,
            "data": data,
        }

    def _handle_streaming_response(self, response):
        """
        Handle a streaming response.

        Args:
            response: Streaming response

        Returns:
            Generator yielding response chunks
        """
        try:
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
                            yield data
        finally:
            response.close()

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()
