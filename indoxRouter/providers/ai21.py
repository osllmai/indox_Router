import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

from .base_provider import BaseProvider
from ..utils.exceptions import ModelNotFoundError, ProviderAPIError, RateLimitError


class Provider(BaseProvider):
    """
    AI21 Labs provider implementation
    """

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the AI21 Labs provider

        Args:
            api_key: AI21 Labs API key
            model_name: Model name (e.g., j2-ultra, j2-mid, jamba-instruct)
        """
        super().__init__(api_key, model_name)

        # Load model configuration
        self.model_config = self._load_model_config(model_name)

        # AI21 API base URL
        self.api_base = os.environ.get(
            "AI21_API_BASE", "https://api.ai21.com/studio/v1"
        )

        # Default generation parameters
        self.default_params = {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1024,
        }

    def _load_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        Load model configuration from the JSON file

        Args:
            model_name: Model name to load configuration for

        Returns:
            Model configuration dictionary

        Raises:
            ModelNotFoundError: If the model is not found in the configuration
        """
        config_path = Path(__file__).parent / "ai21.json"

        try:
            with open(config_path, "r") as f:
                models = json.load(f)

            for model in models:
                if model.get("modelName") == model_name:
                    return model

            raise ModelNotFoundError(
                f"Model {model_name} not found in AI21 Labs provider"
            )

        except FileNotFoundError:
            raise ModelNotFoundError(f"AI21 Labs provider configuration file not found")
        except json.JSONDecodeError:
            raise ModelNotFoundError(
                f"Invalid JSON in AI21 Labs provider configuration file"
            )

    def estimate_cost(self, prompt: str, max_tokens: int) -> float:
        """
        Estimate the cost of generating a completion

        Args:
            prompt: Prompt text
            max_tokens: Maximum number of tokens to generate

        Returns:
            Estimated cost in USD
        """
        # Count tokens in the prompt
        prompt_tokens = self.count_tokens(prompt)

        # Calculate cost based on input and output pricing
        input_cost = (prompt_tokens / 1000) * self.model_config.get(
            "inputPricePer1KTokens", 0
        )
        output_cost = (max_tokens / 1000) * self.model_config.get(
            "outputPricePer1KTokens", 0
        )

        return input_cost + output_cost

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        # AI21 doesn't provide a direct token counting API in their Python client
        # This is a rough approximation - in production, consider using a tokenizer library
        return len(text.split()) * 1.3  # Rough approximation

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a completion for the given prompt

        Args:
            prompt: Prompt text
            **kwargs: Additional parameters for the generation

        Returns:
            Dictionary containing the generated text, cost, and usage statistics

        Raises:
            ProviderAPIError: If there's an error with the provider API
            RateLimitError: If the provider's rate limit is exceeded
        """
        try:
            # Get generation parameters
            max_tokens = kwargs.get("max_tokens", self.default_params["max_tokens"])
            temperature = kwargs.get("temperature", self.default_params["temperature"])
            top_p = kwargs.get("top_p", self.default_params["top_p"])

            # Prepare system prompt if provided
            system_prompt = kwargs.get(
                "system_prompt", self.model_config.get("systemPrompt", "")
            )

            # Format the prompt using the template if available
            prompt_template = self.model_config.get("promptTemplate", "")
            if prompt_template and "%1" in prompt_template:
                formatted_prompt = prompt_template.replace("%1", prompt)
            else:
                formatted_prompt = prompt

            # Combine system prompt and user prompt if needed
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{formatted_prompt}"
            else:
                full_prompt = formatted_prompt

            # Check if this is a Jamba model (chat model)
            is_jamba = "jamba" in self.model_name.lower()

            if is_jamba:
                # Chat completion endpoint for Jamba models
                endpoint = f"{self.api_base}/chat/completions"

                # Prepare the request payload for chat
                payload = {
                    "model": self.model_name,
                    "messages": [],
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                }

                # Add system message if provided
                if system_prompt:
                    payload["messages"].append(
                        {"role": "system", "content": system_prompt}
                    )

                # Add user message
                payload["messages"].append(
                    {"role": "user", "content": formatted_prompt}
                )
            else:
                # Completion endpoint for Jurassic models
                endpoint = f"{self.api_base}/{self.model_name}/complete"

                # Prepare the request payload for completion
                payload = {
                    "prompt": full_prompt,
                    "temperature": temperature,
                    "topP": top_p,
                    "maxTokens": max_tokens,
                }

            # Make the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                endpoint, headers=headers, json=payload, timeout=60
            )

            # Check for errors
            if response.status_code != 200:
                error_message = response.json().get("detail", "Unknown error")

                if response.status_code == 429:
                    raise RateLimitError(
                        f"AI21 Labs API rate limit exceeded: {error_message}"
                    )
                else:
                    raise ProviderAPIError(f"AI21 Labs API error: {error_message}")

            # Parse the response
            response_data = response.json()

            # Extract the generated text based on model type
            if is_jamba:
                generated_text = (
                    response_data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )

                # Get token usage
                usage = response_data.get("usage", {})
                prompt_tokens = usage.get(
                    "prompt_tokens", self.count_tokens(formatted_prompt)
                )
                completion_tokens = usage.get(
                    "completion_tokens", self.count_tokens(generated_text)
                )
                total_tokens = usage.get(
                    "total_tokens", prompt_tokens + completion_tokens
                )
            else:
                generated_text = (
                    response_data.get("completions", [{}])[0]
                    .get("data", {})
                    .get("text", "")
                )

                # For Jurassic models, token counts are not directly provided
                prompt_tokens = self.count_tokens(full_prompt)
                completion_tokens = self.count_tokens(generated_text)
                total_tokens = prompt_tokens + completion_tokens

            # Calculate cost
            cost = self.estimate_cost(full_prompt, completion_tokens)

            # Prepare the response
            result = {
                "text": generated_text,
                "cost": cost,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                },
            }

            return self.validate_response(result)

        except RateLimitError:
            # Re-raise rate limit errors
            raise
        except Exception as e:
            # Handle other errors
            raise ProviderAPIError(
                f"Error generating completion with AI21 Labs API: {str(e)}", e
            )
