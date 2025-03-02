import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .base_provider import BaseProvider
from ..utils.exceptions import ModelNotFoundError, ProviderAPIError, RateLimitError


class Provider(BaseProvider):
    """
    Google Gemini provider implementation
    """

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the Google provider

        Args:
            api_key: Google API key
            model_name: Model name (e.g., gemini-1.5-pro)
        """
        super().__init__(api_key, model_name)

        # Configure the Google API client
        genai.configure(api_key=api_key)

        # Load model configuration
        self.model_config = self._load_model_config(model_name)

        # Set default generation config
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        # Set default safety settings (moderate filtering)
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
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
        config_path = Path(__file__).parent / "google.json"

        try:
            with open(config_path, "r") as f:
                models = json.load(f)

            for model in models:
                if model.get("modelName") == model_name:
                    return model

            raise ModelNotFoundError(f"Model {model_name} not found in Google provider")

        except FileNotFoundError:
            raise ModelNotFoundError(f"Google provider configuration file not found")
        except json.JSONDecodeError:
            raise ModelNotFoundError(
                f"Invalid JSON in Google provider configuration file"
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
        try:
            # Use Google's tokenizer if available
            model = genai.GenerativeModel(self.model_name)
            return model.count_tokens(text).total_tokens
        except Exception:
            # Fallback to approximate token counting
            return len(text.split())

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
            max_tokens = kwargs.get("max_tokens", 1024)
            temperature = kwargs.get("temperature", 0.7)
            top_p = kwargs.get("top_p", 0.95)
            top_k = kwargs.get("top_k", 40)

            # Update generation config
            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_tokens,
            }

            # Prepare system prompt if provided
            system_prompt = kwargs.get(
                "system_prompt", self.model_config.get("systemPrompt", "")
            )

            # Create the model
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
            )

            # Format the prompt using the template if available
            prompt_template = self.model_config.get("promptTemplate", "")
            if prompt_template and "%1" in prompt_template:
                formatted_prompt = prompt_template.replace("%1", prompt)
            else:
                formatted_prompt = prompt

            # Generate the completion
            if system_prompt:
                response = model.generate_content([system_prompt, formatted_prompt])
            else:
                response = model.generate_content(formatted_prompt)

            # Extract the generated text
            generated_text = response.text

            # Get token counts
            prompt_tokens = self.count_tokens(prompt)
            completion_tokens = self.count_tokens(generated_text)
            total_tokens = prompt_tokens + completion_tokens

            # Calculate cost
            cost = self.estimate_cost(prompt, completion_tokens)

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

        except Exception as e:
            error_message = str(e)

            # Handle rate limit errors
            if (
                "rate limit" in error_message.lower()
                or "quota" in error_message.lower()
            ):
                raise RateLimitError(f"Google API rate limit exceeded: {error_message}")

            # Handle other API errors
            raise ProviderAPIError(
                f"Error generating completion with Google API: {error_message}", e
            )
