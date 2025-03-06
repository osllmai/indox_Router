"""
Client module for indoxRouter.
This module contains the main Client class that users will interact with.
"""

import os
from typing import Dict, List, Any, Optional, Union, Generator

# Remove database import
# from .database import Database, get_database
from .exceptions import (
    AuthenticationError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidParametersError,
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


class Client:
    """
    Main client class for indoxRouter.

    This class provides a unified interface to interact with various LLM providers.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the client.

        Args:
            api_key: The API key for indoxRouter. If not provided, uses the INDOX_ROUTER_API_KEY environment variable.

        Raises:
            AuthenticationError: If the API key is invalid.
        """
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.environ.get("INDOX_ROUTER_API_KEY")

        if not api_key:
            raise AuthenticationError(
                "The api_key must be set either by passing api_key to the client or by setting the "
                "INDOX_ROUTER_API_KEY environment variable"
            )

        # Initialize configuration
        self.config = get_config()

        # Development mode - no database
        # Placeholder for user authentication
        # self.db = None
        # self.user = {
        #     "id": 1,
        #     "name": "Development User",
        #     "email": "dev@example.com",
        # }

        self.api_key = api_key

        # Initialize resource classes
        self._chat = Chat(self)
        self._completions = Completions(self)
        self._embeddings = Embeddings(self)
        self._images = Images(self)
        self._models = Models(self)

        # For backward compatibility
        self.chat = self._chat
        self.completions = self._completions
        self.embeddings = self._embeddings
        self.images = self._images
        self.models = self._models

    def providers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available providers.

        Returns:
            A list of provider dictionaries with information.
        """
        return self._models.list_providers()

    # For backward compatibility
    def list_providers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available providers.

        Returns:
            A list of provider dictionaries with information.
        """
        return self.providers()

    def models(self, provider: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a list of available models, optionally filtered by provider.

        Args:
            provider: The name of the provider to filter by. If None, lists models from all providers.

        Returns:
            A dictionary mapping provider names to lists of model dictionaries.

        Raises:
            ProviderNotFoundError: If the specified provider is not found.
        """
        return self._models.list(provider)

    # For backward compatibility
    def list_models(
        self, provider: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a list of available models, optionally filtered by provider.

        Args:
            provider: The name of the provider to filter by. If None, lists models from all providers.

        Returns:
            A dictionary mapping provider names to lists of model dictionaries.

        Raises:
            ProviderNotFoundError: If the specified provider is not found.
        """
        return self.models(provider)

    def model_info(self, provider: str, model: str) -> ModelInfo:
        """
        Get information about a specific model from a provider.

        Args:
            provider: The name of the provider.
            model: The name of the model.

        Returns:
            A ModelInfo object containing information about the model.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
        """
        return self._models.get(provider, model)

    # For backward compatibility
    def get_model_info(self, provider: str, model: str) -> ModelInfo:
        """
        Get information about a specific model from a provider.

        Args:
            model: The name of the model.

        Returns:
            A ModelInfo object containing information about the model.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
        """
        return self.model_info(provider, model)

    def completion(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        provider_api_key: Optional[str] = None,
        stream: bool = False,
        return_generator: bool = False,
        **kwargs,
    ) -> Union[CompletionResponse, Generator[str, None, None]]:
        """
        Generate text from a prompt.

        Args:
            prompt: The prompt to generate text from.
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
            A CompletionResponse object containing the response from the provider.
            If stream=True and return_generator=True, returns a generator that yields chunks of the response.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
            InvalidParametersError: If the parameters are invalid.
            RequestError: If the request to the provider fails.
        """
        return self._completions(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            provider_api_key=provider_api_key,
            stream=stream,
            return_generator=return_generator,
            **kwargs,
        )

    def chat(
        self,
        messages: List[Union[Dict[str, str], ChatMessage]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        provider_api_key: Optional[str] = None,
        stream: bool = False,
        return_generator: bool = False,
        **kwargs,
    ) -> Union[ChatResponse, Generator[str, None, None]]:
        """
        Generate a chat response from a list of messages.

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
        return self._chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            provider_api_key=provider_api_key,
            stream=stream,
            return_generator=return_generator,
            **kwargs,
        )

    def embeddings(
        self,
        text: Union[str, List[str]],
        model: str,
        provider_api_key: Optional[str] = None,
        **kwargs,
    ) -> EmbeddingResponse:
        """
        Generate embeddings for text.

        Args:
            text: The text to embed. Can be a single string or a list of strings.
            model: The model to use.
            provider_api_key: Optional API key for the provider. If not provided, uses the configured key.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            An EmbeddingResponse object containing the embeddings from the provider.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
            InvalidParametersError: If the parameters are invalid.
            RequestError: If the request to the provider fails.
        """
        return self._embeddings(
            text=text,
            model=model,
            provider_api_key=provider_api_key,
            **kwargs,
        )

    def image(
        self,
        prompt: str,
        model: str,
        size: Optional[str] = None,
        n: int = 1,
        provider_api_key: Optional[str] = None,
        **kwargs,
    ) -> ImageResponse:
        """
        Generate an image from a prompt.

        Args:
            prompt: The prompt to generate an image from.
            model: The model to use.
            size: The size of the image to generate.
            n: The number of images to generate.
            provider_api_key: Optional API key for the provider. If not provided, uses the configured key.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            An ImageResponse object containing the generated images.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
            InvalidParametersError: If the parameters are invalid.
            RequestError: If the request to the provider fails.
        """
        return self._images(
            prompt=prompt,
            model=model,
            size=size,
            n=n,
            provider_api_key=provider_api_key,
            **kwargs,
        )


# For backward compatibility
IndoxRouter = Client
