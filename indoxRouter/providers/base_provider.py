from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseProvider(ABC):
    """
    Base class for all LLM providers

    All provider implementations should inherit from this class
    and implement the required methods.
    """

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the provider

        Args:
            api_key: Provider API key
            model_name: Model name to use
        """
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a completion for the given prompt

        Args:
            prompt: The prompt to generate a completion for
            **kwargs: Additional parameters for the generation

        Returns:
            Dictionary containing the response text, cost, and other metadata
        """
        pass

    @abstractmethod
    def estimate_cost(self, prompt: str, max_tokens: int) -> float:
        """
        Estimate the cost of generating a completion

        Args:
            prompt: The prompt to generate a completion for
            max_tokens: Maximum number of tokens to generate

        Returns:
            Estimated cost in credits
        """
        pass

    def validate_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and standardize the response from the provider

        Args:
            response: Raw response from the provider

        Returns:
            Standardized response dictionary
        """
        # Ensure the response has the required fields
        if "text" not in response:
            raise ValueError("Provider response missing 'text' field")

        if "cost" not in response:
            raise ValueError("Provider response missing 'cost' field")

        return response
