from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    raise ImportError(
        "Anthropic package not installed. Install it with 'pip install anthropic'"
    )

from ..utils.exceptions import RateLimitError, ModelNotFoundError
from .base_provider import BaseProvider


class Provider(BaseProvider):
    """
    Anthropic (Claude) provider implementation
    """

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the Anthropic provider

        Args:
            api_key: Anthropic API key
            model_name: Model name to use (e.g., 'claude-3-opus-20240229')
        """
        super().__init__(api_key, model_name)

        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key)

        # Load model configuration
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
        config_path = Path(__file__).parent / "claude.json"

        # Load the configuration
        with open(config_path, "r") as f:
            models = json.load(f)

        # Find the model configuration
        for model in models:
            if model.get("modelName") == model_name:
                return model

        # If model not found, raise an error
        raise ModelNotFoundError(
            f"Model {model_name} not found in Anthropic configuration"
        )

    def estimate_cost(self, prompt: str, max_tokens: int) -> float:
        """
        Estimate the cost of generating a completion

        Args:
            prompt: The prompt to generate a completion for
            max_tokens: Maximum number of tokens to generate

        Returns:
            Estimated cost in credits
        """
        # Estimate token count (rough approximation)
        prompt_tokens = self.count_tokens(prompt)

        # Get pricing for the model
        input_price = self.model_config.get("inputPricePer1KTokens", 0)
        output_price = self.model_config.get("outputPricePer1KTokens", 0)

        # Calculate cost
        prompt_cost = (prompt_tokens / 1000) * input_price
        completion_cost = (max_tokens / 1000) * output_price

        return prompt_cost + completion_cost

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        try:
            # Use Anthropic's token counter if available
            return anthropic.count_tokens(text)
        except:
            # Fallback to simple approximation
            return len(text.split()) * 1.3

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a completion using Anthropic

        Args:
            prompt: The prompt to generate a completion for
            **kwargs: Additional parameters for the generation
                - max_tokens: Maximum number of tokens to generate
                - temperature: Sampling temperature (0.0 to 1.0)
                - top_p: Nucleus sampling parameter (0.0 to 1.0)

        Returns:
            Dictionary containing the response text, cost, and other metadata
        """
        try:
            # Extract parameters
            max_tokens = kwargs.get("max_tokens", 1024)
            temperature = kwargs.get("temperature", 0.7)
            top_p = kwargs.get("top_p", 1.0)

            # Format prompt using the template from model config
            prompt_template = self.model_config.get(
                "promptTemplate", "Human: %1\n\nAssistant: %2"
            )
            formatted_prompt = prompt_template.replace("%1", prompt).replace("%2", "")

            # Get system prompt if available
            system_prompt = self.model_config.get("systemPrompt", "")

            # Make API call
            response = self.client.messages.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                system=system_prompt if system_prompt else None,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )

            # Extract response text
            text = response.content[0].text

            # Calculate actual cost
            input_price = self.model_config.get("inputPricePer1KTokens", 0)
            output_price = self.model_config.get("outputPricePer1KTokens", 0)

            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens

            prompt_cost = (prompt_tokens / 1000) * input_price
            completion_cost = (completion_tokens / 1000) * output_price
            total_cost = prompt_cost + completion_cost

            # Return standardized response
            return {
                "text": text,
                "cost": total_cost,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
                "model": self.model_name,
            }

        except anthropic.RateLimitError as e:
            raise RateLimitError(f"Anthropic rate limit exceeded: {str(e)}")
        except anthropic.APIError as e:
            raise Exception(f"Anthropic API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating completion: {str(e)}")
