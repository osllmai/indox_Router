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
import jwt
from uuid import uuid4

from .exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidParametersError
)
from .models import (
    ChatMessage,
    ChatResponse,
    CompletionResponse,
    EmbeddingResponse,
    ImageResponse,
    ModelInfo,
)
from .config import get_config
from .client_resourses import (
    Chat,
    Completions,
    Embeddings,
    Images,
    Models,
)
from .constants import (
    DEFAULT_API_VERSION,
    DEFAULT_TIMEOUT,
    DEFAULT_BASE_URL,
    ERROR_INVALID_API_KEY,
    ERROR_MODEL_NOT_FOUND,
    ERROR_PROVIDER_NOT_FOUND,
    ERROR_INVALID_PARAMETERS,
    ERROR_RATE_LIMIT,
    ERROR_REQUEST_FAILED,
)

logger = logging.getLogger(__name__)

class Client:
    """
    Client for the IndoxRouter API that provides a unified interface to multiple AI providers.
    
    The Client class handles:
    - Authentication and token management with automatic refresh
    - Rate limiting and quota tracking
    - Standardized error handling across providers
    - Consistent response formatting
    
    This client provides access to various AI capabilities including:
    - Chat completions (chat)
    - Text completions (completion)
    - Text embeddings (embeddings)
    - Image generation (image)
    
    It also offers methods to retrieve information about available providers and models,
    as well as usage statistics for the authenticated user.
    
    The client can be used directly or as a context manager with the 'with' statement.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = f"{DEFAULT_BASE_URL}/{DEFAULT_API_VERSION}",
        timeout: int = DEFAULT_TIMEOUT,
        auto_refresh: bool = True,
    ):
        """
        Initialize the client with authentication and session management

        Args:
            api_key: User's API key (default: INDOX_ROUTER_API_KEY env var)
            base_url: Base URL for the API server
            timeout: Request timeout in seconds
            auto_refresh: Enable automatic token refresh
        """
        # Authentication setup
        self.api_key = api_key or os.getenv("INDOX_ROUTER_API_KEY")
        if not self.api_key:
            raise AuthenticationError(ERROR_INVALID_API_KEY)

        self.base_url = base_url
        self.timeout = timeout
        self.auto_refresh = auto_refresh
        self.config = get_config()

        # Session state management
        self.session = requests.Session()
        self._auth_token = None
        self._token_expiry = None
        self.user_info = None
        self.rate_limits = {}

        # Initialize resources
        self._init_resources()
        self._authenticate()

    def _init_resources(self):
        """Initialize resource controllers"""
        self._chat = Chat(self)
        self._completions = Completions(self)
        self._embeddings = Embeddings(self)
        self._images = Images(self)
        self._models = Models(self)

        # Backward compatibility
        self.chat = self._chat
        self.completions = self._completions
        self.embeddings = self._embeddings
        self.images = self._images
        self.models = self._models

    def _authenticate(self):
        """Full authentication flow with the API server"""
        try:
            # Get authentication token
            auth_response = self.session.post(
                f"{self.base_url}/auth/token",
                json={"api_key": self.api_key},
                timeout=self.timeout
            )
            auth_response.raise_for_status()

            auth_data = auth_response.json()
            self._process_auth_data(auth_data)

            logger.info("Authenticated as user: %s", self.user_info['email'])

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Authentication failed: {str(e)}") from e
        except jwt.PyJWTError as e:
            raise AuthenticationError(f"Token validation failed: {str(e)}") from e
        except KeyError as e:
            raise AuthenticationError(f"Invalid auth response: {str(e)}") from e

    def _process_auth_data(self, auth_data: dict):
        """Process authentication response data"""
        # Validate and decode JWT
        decoded_token = jwt.decode(
            auth_data['access_token'],
            self.config.JWT_PUBLIC_KEY,
            algorithms=["RS256"],
            audience="indox-router-api"
        )

        # Update session state
        self._auth_token = auth_data['access_token']
        self._token_expiry = datetime.fromtimestamp(decoded_token['exp'])
        self.user_info = decoded_token['user']
        self.rate_limits = decoded_token.get('rate_limits', {})

        # Set default headers
        self.session.headers.update({
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json"
        })

    def _check_auth(self):
        """Validate authentication state"""
        if datetime.now() >= self._token_expiry:
            if self.auto_refresh:
                self._refresh_token()
            else:
                raise AuthenticationError("Session expired")

    def _refresh_token(self):
        """Refresh access token using refresh token"""
        try:
            refresh_response = self.session.post(
                f"{self.base_url}/auth/refresh",
                timeout=self.timeout
            )
            refresh_response.raise_for_status()

            refresh_data = refresh_response.json()
            self._process_auth_data(refresh_data)

            logger.debug("Successfully refreshed authentication token")

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}") from e

    def _check_rate_limit(self, endpoint: str):
        """Check rate limits for specific endpoint"""
        limits = self.rate_limits.get(endpoint, {})
        if limits.get('remaining', 1) <= 0:
            reset_time = datetime.fromtimestamp(limits.get('reset', datetime.now().timestamp()))
            raise RateLimitError(
                f"{ERROR_RATE_LIMIT} for {endpoint}. Resets at {reset_time}",
                reset_time=reset_time
            )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Unified request handler with:
        - Authentication checks
        - Rate limiting
        - Error handling
        - Response standardization
        """
        self._check_auth()
        self._check_rate_limit(endpoint)

        request_id = uuid4().hex
        url = f"{self.base_url}/{endpoint}"
        start_time = datetime.now()

        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            duration = (datetime.now() - start_time).total_seconds()

            # Update rate limits from headers
            self._update_rate_limits(response.headers)

            response.raise_for_status()
            return self._format_success(response.json(), request_id, duration, endpoint)

        except requests.exceptions.RequestException as e:
            error_response = self._format_error(e, request_id, duration, endpoint)
            
            # Map HTTP errors to appropriate exception types
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                error_data = {}
                
                try:
                    error_data = e.response.json().get('error', {})
                except ValueError:
                    pass
                
                error_type = error_data.get('type', '')
                
                if status_code == 404:
                    if 'provider' in error_type.lower():
                        raise ProviderNotFoundError(f"{ERROR_PROVIDER_NOT_FOUND}: {error_data.get('message', str(e))}")
                    elif 'model' in error_type.lower():
                        raise ModelNotFoundError(f"{ERROR_MODEL_NOT_FOUND}: {error_data.get('message', str(e))}")
                elif status_code == 400:
                    raise InvalidParametersError(f"{ERROR_INVALID_PARAMETERS}: {error_data.get('message', str(e))}")
                elif status_code == 429:
                    reset_time = datetime.fromtimestamp(error_data.get('reset', datetime.now().timestamp() + 60))
                    raise RateLimitError(f"{ERROR_RATE_LIMIT}: {error_data.get('message', str(e))}", reset_time=reset_time)
                elif status_code >= 500:
                    raise ProviderError(f"{ERROR_REQUEST_FAILED}: {error_data.get('message', str(e))}")
                
            raise NetworkError(f"Request failed: {str(e)}")

    def _update_rate_limits(self, headers: Dict[str, str]):
        """Update rate limits from response headers"""
        for key, value in headers.items():
            if key.startswith('X-Ratelimit-'):
                endpoint = key.split('-')[-1]
                self.rate_limits[endpoint] = {
                    'limit': int(headers[f'X-Ratelimit-Limit-{endpoint}']),
                    'remaining': int(headers[f'X-Ratelimit-Remaining-{endpoint}']),
                    'reset': int(headers[f'X-Ratelimit-Reset-{endpoint}'])
                }

    def _format_success(self, data: dict, request_id: str, duration: float, endpoint: str) -> Dict[str, Any]:
        """Standard success response format"""
        return {
            "request_id": request_id,
            "data": data.get('result'),
            "metadata": {
                "endpoint": endpoint,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                **data.get('metadata', {})
            },
            "error": None
        }

    def _format_error(self, error: Exception, request_id: str, duration: float, endpoint: str) -> Dict[str, Any]:
        """Standard error response format"""
        error_info = {
            "request_id": request_id,
            "data": None,
            "metadata": {
                "endpoint": endpoint,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            },
            "error": {
                "type": error.__class__.__name__,
                "message": str(error),
                "details": {}
            }
        }

        if isinstance(error, requests.exceptions.HTTPError):
            error_info["error"]["code"] = error.response.status_code
            error_info["error"]["details"] = error.response.json().get('error', {})

        logger.error("Request %s failed: %s", request_id, error)
        return error_info

    # Resource proxy methods
    def providers(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available AI providers.
        
        Returns:
            List[Dict[str, Any]]: A list of provider information dictionaries, each containing
            details such as provider ID, name, description, and supported features.
        
        Example:
            ```python
            providers = client.providers()
            for provider in providers:
                print(f"{provider['id']}: {provider['name']}")
            ```
        """
        return self._make_request('GET', 'providers')['data']

    def models(self, provider: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get available models, optionally filtered by provider.
        
        Args:
            provider (Optional[str]): Provider ID to filter models by. If None, returns models from all providers.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary mapping provider IDs to lists of model information.
            Each model information dictionary contains details such as model ID, name, capabilities, and pricing.
        
        Example:
            ```python
            # Get all models
            all_models = client.models()
            
            # Get models from a specific provider
            openai_models = client.models(provider="openai")
            ```
        """
        params = {"provider": provider} if provider else None
        return self._make_request('GET', 'models', params=params)['data']

    def model_info(self, provider: str, model: str) -> ModelInfo:
        """
        Get detailed information about a specific model.
        
        Args:
            provider (str): Provider ID (e.g., "openai", "anthropic")
            model (str): Model ID (e.g., "gpt-4", "claude-2")
        
        Returns:
            ModelInfo: Detailed information about the model, including capabilities,
            pricing, rate limits, and other provider-specific details.
        
        Raises:
            ModelNotFoundError: If the specified model doesn't exist or isn't available
            ProviderNotFoundError: If the specified provider doesn't exist
        
        Example:
            ```python
            model_details = client.model_info(provider="openai", model="gpt-4")
            print(f"Context window: {model_details.context_window} tokens")
            ```
        """
        try:
            return self._make_request('GET', f'models/{provider}/{model}')['data']
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ModelNotFoundError(f"{ERROR_MODEL_NOT_FOUND}: '{model}' for provider '{provider}'")
            raise

    def chat(self, messages: List[Union[Dict[str, str], ChatMessage]], **kwargs) -> ChatResponse:
        """
        Generate a chat completion from a series of messages.
        
        Args:
            messages (List[Union[Dict[str, str], ChatMessage]]): A list of messages, where each message
                is either a dictionary with 'role' and 'content' keys, or a ChatMessage object.
            **kwargs: Additional parameters to pass to the provider, such as:
                - provider (str): Provider ID (e.g., "openai", "anthropic")
                - model (str): Model ID (e.g., "gpt-4", "claude-2")
                - temperature (float): Controls randomness (0.0-1.0)
                - max_tokens (int): Maximum number of tokens to generate
                - stream (bool): Whether to stream the response
        
        Returns:
            ChatResponse: The generated chat completion response, containing the assistant's message,
            usage statistics, and other metadata.
        
        Example:
            ```python
            response = client.chat([
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me about AI."}
            ], provider="openai", model="gpt-4")
            
            print(response.message.content)
            ```
        """
        return self._chat(messages, **kwargs)

    def completion(self, prompt: str, **kwargs) -> CompletionResponse:
        """
        Generate a text completion from a prompt.
        
        Args:
            prompt (str): The text prompt to complete
            **kwargs: Additional parameters to pass to the provider, such as:
                - provider (str): Provider ID (e.g., "openai", "cohere")
                - model (str): Model ID (e.g., "text-davinci-003", "command")
                - temperature (float): Controls randomness (0.0-1.0)
                - max_tokens (int): Maximum number of tokens to generate
                - stream (bool): Whether to stream the response
        
        Returns:
            CompletionResponse: The generated completion response, containing the completed text,
            usage statistics, and other metadata.
        
        Example:
            ```python
            response = client.completion(
                "Once upon a time,", 
                provider="openai", 
                model="text-davinci-003"
            )
            
            print(response.text)
            ```
        """
        return self._completions(prompt, **kwargs)

    def embeddings(self, text: Union[str, List[str]], **kwargs) -> EmbeddingResponse:
        """
        Generate embeddings for text.
        
        Args:
            text (Union[str, List[str]]): Text or list of texts to generate embeddings for
            **kwargs: Additional parameters to pass to the provider, such as:
                - provider (str): Provider ID (e.g., "openai", "cohere")
                - model (str): Model ID (e.g., "text-embedding-ada-002")
                - dimensions (int): Desired dimensionality of the embeddings (if supported)
        
        Returns:
            EmbeddingResponse: The generated embeddings response, containing the vector representations,
            usage statistics, and other metadata.
        
        Example:
            ```python
            response = client.embeddings(
                ["Hello world", "AI is amazing"],
                provider="openai",
                model="text-embedding-ada-002"
            )
            
            for i, embedding in enumerate(response.embeddings):
                print(f"Embedding {i} has {len(embedding)} dimensions")
            ```
        """
        return self._embeddings(text, **kwargs)

    def image(self, prompt: str, **kwargs) -> ImageResponse:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt (str): The text description of the image to generate
            **kwargs: Additional parameters to pass to the provider, such as:
                - provider (str): Provider ID (e.g., "openai", "stability")
                - model (str): Model ID (e.g., "dall-e-3", "stable-diffusion-xl")
                - size (str): Image size (e.g., "1024x1024")
                - quality (str): Image quality (e.g., "standard", "hd")
                - style (str): Image style (e.g., "vivid", "natural")
                - response_format (str): Format of the response (e.g., "url", "b64_json")
        
        Returns:
            ImageResponse: The generated image response, containing the image data or URLs,
            usage statistics, and other metadata.
        
        Example:
            ```python
            response = client.image(
                "A serene landscape with mountains and a lake",
                provider="openai",
                model="dall-e-3",
                size="1024x1024"
            )
            
            print(f"Image URL: {response.url}")
            ```
        """
        return self._images(prompt, **kwargs)

    # Additional features
    def get_usage(self) -> Dict[str, Any]:
        """
        Get current usage statistics for the authenticated user.
        
        Returns:
            Dict[str, Any]: Usage statistics including token counts, request counts,
            billing information, and quota limits.
        
        Example:
            ```python
            usage = client.get_usage()
            print(f"Total tokens used: {usage['total_tokens']}")
            print(f"Remaining quota: {usage['remaining_quota']}")
            ```
        """
        return self._make_request('GET', 'usage')['data']

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            Dict[str, Any]: User information including ID, name, email, account type,
            subscription details, and other user-specific data.
        
        Example:
            ```python
            user = client.get_user_info()
            print(f"User ID: {user['id']}")
            print(f"Account type: {user['account_type']}")
            ```
        """
        return self.user_info.copy()

    def close(self):
        """
        Clean up client resources and close the session.
        
        This method should be called when the client is no longer needed to ensure
        proper cleanup of resources, particularly the HTTP session.
        
        Example:
            ```python
            client = Client(api_key="your_api_key")
            # Use the client...
            client.close()  # Clean up when done
            ```
        """
        self.session.close()
        logger.info("Client session closed")

    def __enter__(self):
        """
        Enter the context manager.
        
        This method enables the client to be used as a context manager with the 'with' statement.
        
        Returns:
            Client: The client instance.
        
        Example:
            ```python
            with Client(api_key="your_api_key") as client:
                # Use the client within this block
                response = client.chat([{"role": "user", "content": "Hello!"}])
            # Client is automatically closed when exiting the block
            ```
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager.
        
        This method is called when exiting a 'with' block. It ensures the client
        is properly closed, even if an exception occurs within the block.
        
        Args:
            exc_type: The exception type, if an exception was raised in the with block, otherwise None
            exc_val: The exception value, if an exception was raised in the with block, otherwise None
            exc_tb: The traceback, if an exception was raised in the with block, otherwise None
        """
        self.close()

# Backward compatibility
IndoxRouter = Client
