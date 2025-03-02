from typing import Dict, Optional, Any, List
import os
import sys
import json
import requests

# Add the parent directory to the path to make imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Use absolute imports
from indoxRouter.utils.auth import AuthManager
from indoxRouter.providers.base_provider import BaseProvider


class Client:
    """
    Client for making API requests to the IndoxRouter API.
    """

    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize the client.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API (default: http://localhost:8000)
        """
        self.api_key = api_key
        self.base_url = base_url or "http://localhost:8000"
        self.auth_manager = AuthManager()

        # Verify the API key
        self.user_data = self.auth_manager.verify_api_key(api_key)
        if not self.user_data:
            raise ValueError("Invalid API key")

    def generate(
        self,
        provider: str,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> str:
        """
        Generate a response from a model.

        Args:
            provider: Provider name
            model: Model name
            prompt: Prompt
            temperature: Temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            Model response
        """
        url = f"{self.base_url}/v1/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            error_message = (
                response.json().get("error", {}).get("message", "Unknown error")
            )
            raise Exception(f"Error: {error_message}")

        return response.json().get("choices", [{}])[0].get("text", "")

    def list_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available models.

        Args:
            provider: Provider name (optional)

        Returns:
            List of models
        """
        url = f"{self.base_url}/v1/models"

        if provider:
            url += f"?provider={provider}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            error_message = (
                response.json().get("error", {}).get("message", "Unknown error")
            )
            raise Exception(f"Error: {error_message}")

        return response.json().get("data", [])

    def list_providers(self) -> List[str]:
        """
        List available providers.

        Returns:
            List of providers
        """
        url = f"{self.base_url}/v1/providers"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            error_message = (
                response.json().get("error", {}).get("message", "Unknown error")
            )
            raise Exception(f"Error: {error_message}")

        return response.json().get("data", [])

    def _parse_model_name(self, model_name: str) -> tuple:
        """
        Parse model name into provider and model parts

        Args:
            model_name: Full model name (e.g., 'openai/gpt-4')

        Returns:
            Tuple of (provider_name, model_part)
        """
        if "/" not in model_name:
            raise ValueError(
                f"Invalid model name format: {model_name}. Expected format: 'provider/model'"
            )

        provider_name, model_part = model_name.split("/", 1)
        return provider_name, model_part

    def _load_provider_class(self, provider_name: str):
        """
        Dynamically load provider class

        Args:
            provider_name: Name of the provider

        Returns:
            Provider class
        """
        try:
            # Import the provider module dynamically
            module_path = f".providers.{provider_name}"
            provider_module = __import__(
                module_path, fromlist=["Provider"], globals=globals()
            )
            return provider_module.Provider
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Provider not supported: {provider_name}") from e

    def _get_provider(self, model_name: str) -> BaseProvider:
        """
        Get provider instance with cached credentials

        Args:
            model_name: Full model name (e.g., 'openai/gpt-4')

        Returns:
            Provider instance
        """
        if model_name in self.provider_cache:
            return self.provider_cache[model_name]

        provider_name, model_part = self._parse_model_name(model_name)
        provider_class = self._load_provider_class(provider_name)

        # Get provider API key from secure storage
        provider_api_key = self._get_provider_credentials(provider_name)

        instance = provider_class(api_key=provider_api_key, model_name=model_part)
        self.provider_cache[model_name] = instance
        return instance

    def _get_provider_credentials(self, provider_name: str) -> str:
        """
        Retrieve provider API key from secure storage

        Args:
            provider_name: Name of the provider

        Returns:
            Provider API key
        """
        # Implement your secure credential storage (e.g., AWS Secrets Manager)
        # Example using environment variables:
        env_var = f"{provider_name.upper()}_API_KEY"
        if env_var not in os.environ:
            raise ValueError(
                f"Missing API key for provider: {provider_name}. Set {env_var} environment variable."
            )

        return os.environ[env_var]

    def generate(self, model_name: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate completion with credit handling

        Args:
            model_name: Provider/model name (e.g., 'openai/gpt-4')
            prompt: User input prompt
            **kwargs: Generation parameters

        Returns:
            Dictionary with response and credit information
        """
        provider = self._get_provider(model_name)

        # Estimate max possible cost
        max_tokens = kwargs.get("max_tokens", 2048)
        estimated_cost = provider.estimate_cost(prompt, max_tokens)

        # Check balance
        if self.user_data["balance"] < estimated_cost:
            raise ValueError(
                f"Insufficient credits. Required: {estimated_cost:.6f}, Available: {self.user_data['balance']:.6f}"
            )

        # Make API call
        response = provider.generate(prompt, **kwargs)

        # Deduct actual cost
        success = self.auth_manager.deduct_credits(
            self.user_data["id"], response["cost"]
        )

        if not success:
            raise RuntimeError("Credit deduction failed")

        # Get updated user data
        self.user_data = self.auth_manager.get_user_by_id(self.user_data["id"])

        return {
            "text": response["text"],
            "cost": response["cost"],
            "remaining_credits": self.user_data["balance"],
            "model": model_name,
        }

    def get_balance(self) -> float:
        """
        Get current user balance

        Returns:
            Current credit balance
        """
        # Refresh user data to get the latest balance
        self.user_data = self.auth_manager.get_user_by_id(self.user_data["id"])
        return self.user_data["balance"]

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user information

        Returns:
            User information dictionary
        """
        # Refresh user data
        self.user_data = self.auth_manager.get_user_by_id(self.user_data["id"])
        return self.user_data
