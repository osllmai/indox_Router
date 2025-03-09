"""
Base provider module for indoxRouter server.
This module contains the base provider class that all providers will inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, AsyncGenerator


class BaseProvider(ABC):
    """Base provider class for all LLM providers."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the provider.

        Args:
            api_key: The API key for the provider.
            model_name: The name of the model to use.
        """
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to the provider.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            A dictionary containing the response from the provider.
        """
        pass

    @abstractmethod
    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Send a streaming chat request to the provider.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the provider.

        Yields:
            Chunks of the response from the provider.
        """
        pass

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a completion request to the provider.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            A dictionary containing the response from the provider.
        """
        pass

    @abstractmethod
    async def complete_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Send a streaming completion request to the provider.

        Args:
            prompt: The prompt to complete.
            **kwargs: Additional parameters to pass to the provider.

        Yields:
            Chunks of the response from the provider.
        """
        pass

    @abstractmethod
    def embed(self, text: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
        """
        Send an embedding request to the provider.

        Args:
            text: The text to embed. Can be a single string or a list of strings.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            A dictionary containing the embeddings from the provider.
        """
        pass

    @abstractmethod
    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an image from a prompt.

        Args:
            prompt: The prompt to generate an image from.
            **kwargs: Additional parameters to pass to the provider.

        Returns:
            A dictionary containing the image URL or data.
        """
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens in the text.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            A dictionary containing information about the model.
        """
        pass
