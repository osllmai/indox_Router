from typing import Dict, Any
import json
import os
from pathlib import Path
from openai import OpenAI as OpenAIClient
from .base_provider import BaseProvider


class Provider(BaseProvider):
    """
    OpenAI provider implementation
    """

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the OpenAI provider

        Args:
            api_key: OpenAI API key
            model_name: Model name to use (e.g., 'gpt-4')
        """
        super().__init__(api_key, model_name)
        self.client = OpenAIClient(api_key=api_key)
        self.model_config = self._load_model_config(model_name)

    def _load_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        Load model configuration from JSON file

        Args:
            model_name: Model name

        Returns:
            Model configuration dictionary
        """
        # Get the path to the model configuration file
        config_path = Path(__file__).parent / "openai.json"

        # Load the configuration
        with open(config_path, "r") as f:
            config = json.load(f)

        # Find the model configuration
        for model in config.get("models", []):
            if model.get("id") == model_name:
                return model

        # If model not found, raise an error
        raise ValueError(f"Model {model_name} not found in OpenAI configuration")

    def estimate_cost(self, prompt: str, max_tokens: int) -> float:
        """
        Estimate the cost of generating a completion

        Args:
            prompt: The prompt to generate a completion for
            max_tokens: Maximum number of tokens to generate

        Returns:
            Estimated cost in credits
        """
        input_tokens = self.count_tokens(prompt)
        max_output_tokens = min(
            max_tokens, self.model_config.get("max_output_tokens", 4096)
        )
        return (
            input_tokens * self.model_config["inputPricePer1KTokens"] / 1000
            + max_output_tokens * self.model_config["outputPricePer1KTokens"] / 1000
        )

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        # Simple approximation - in production, use tiktoken or similar
        return len(text.split()) * 1.3

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a completion using OpenAI

        Args:
            prompt: The prompt to generate a completion for
            **kwargs: Additional parameters for the generation

        Returns:
            Dictionary containing the response text, cost, and other metadata
        """
        # Make API call
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )

        # Calculate cost
        input_cost = (response.usage.prompt_tokens / 1000) * self.model_config[
            "inputPricePer1KTokens"
        ]
        output_cost = (response.usage.completion_tokens / 1000) * self.model_config[
            "outputPricePer1KTokens"
        ]
        total_cost = input_cost + output_cost

        # Return standardized response
        return {
            "text": response.choices[0].message.content,
            "cost": total_cost,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.prompt_tokens
                + response.usage.completion_tokens,
            },
            "model": self.model_name,
        }
