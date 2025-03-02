import os
import json
import requests
from typing import Dict, Any, Optional, List
from .base_provider import BaseProvider


class Provider(BaseProvider):
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the Deepseek provider with API key and model name.

        Args:
            api_key (str): The API key for authentication
            model_name (str): The name of the model to use
        """
        super().__init__(api_key, model_name)
        self.base_url = os.environ.get(
            "DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"
        )
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.model_config = self._load_model_config()

    def _load_model_config(self) -> Dict[str, Any]:
        """
        Load the model configuration from the JSON file.

        Returns:
            Dict[str, Any]: The model configuration
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "deepseek.json")

        with open(config_path, "r") as f:
            models = json.load(f)

        for model in models:
            if model["modelName"] == self.model_name:
                return model

        raise ValueError(f"Model {self.model_name} not found in configuration")

    def estimate_cost(self, prompt: str, max_tokens: int = 100) -> float:
        """
        Estimate the cost of generating a completion.

        Args:
            prompt (str): The prompt to generate a completion for
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.

        Returns:
            float: The estimated cost in USD
        """
        input_tokens = self.count_tokens(prompt)
        input_cost = (input_tokens / 1000) * self.model_config["inputPricePer1KTokens"]
        output_cost = (max_tokens / 1000) * self.model_config["outputPricePer1KTokens"]
        return input_cost + output_cost

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        This is a simple approximation. For more accurate counts, consider using a tokenizer.

        Args:
            text (str): The text to count tokens for

        Returns:
            int: The number of tokens
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4

    def generate(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a completion for the given prompt.

        Args:
            prompt (str): The prompt to generate a completion for
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.
            temperature (float, optional): The temperature for sampling. Defaults to 0.7.
            top_p (float, optional): The top-p value for nucleus sampling. Defaults to 1.0.
            frequency_penalty (float, optional): The frequency penalty. Defaults to 0.0.
            presence_penalty (float, optional): The presence penalty. Defaults to 0.0.
            stop (Optional[List[str]], optional): A list of stop sequences. Defaults to None.

        Returns:
            Dict[str, Any]: The generated completion
        """
        # Format the prompt according to the model's template
        prompt_template = self.model_config.get("promptTemplate", "%1%2")
        formatted_prompt = prompt_template.replace("%1", prompt).replace("%2", "")

        # Prepare the request payload
        payload = {
            "model": self.model_config.get("companyModelName", self.model_name),
            "prompt": formatted_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }

        if stop:
            payload["stop"] = stop

        # Make the API request
        try:
            response = requests.post(
                f"{self.base_url}/completions", headers=self.headers, json=payload
            )
            response.raise_for_status()
            result = response.json()

            # Calculate the cost
            input_tokens = result.get("usage", {}).get(
                "prompt_tokens", self.count_tokens(prompt)
            )
            output_tokens = result.get("usage", {}).get("completion_tokens", 0)
            input_cost = (input_tokens / 1000) * self.model_config[
                "inputPricePer1KTokens"
            ]
            output_cost = (output_tokens / 1000) * self.model_config[
                "outputPricePer1KTokens"
            ]
            total_cost = input_cost + output_cost

            # Format the response
            return self.validate_response(
                {
                    "text": result.get("choices", [{}])[0].get("text", ""),
                    "cost": total_cost,
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "input_cost": input_cost,
                        "output_cost": output_cost,
                    },
                    "raw_response": result,
                }
            )

        except requests.exceptions.RequestException as e:
            return {
                "text": f"Error: {str(e)}",
                "cost": 0,
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "input_cost": 0,
                    "output_cost": 0,
                },
                "error": str(e),
            }
