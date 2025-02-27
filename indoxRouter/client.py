import json
import importlib
from pathlib import Path
from typing import Dict, Optional, List, Union
from openai import OpenAI as OpenAIClient
import anthropic
import google.generativeai as genai


class Client:
    PROVIDER_CLIENTS = {
        "openai": OpenAIClient,
        "anthropic": anthropic.Anthropic,
        "google": genai,
        # Add other providers as needed
    }

    PROVIDER_HANDLERS = {
        "openai": "handle_openai",
        "anthropic": "handle_anthropic",
        "google": "handle_google",
        # Add handlers for other providers
    }

    def __init__(self, model_name: str, api_key: str):
        """
        Initialize the LLM client with IndoxRouter API key and model name.

        Args:
            model_name (str): Model name in format 'provider/model-name'
            api_key (str): User's IndoxRouter API key
        """
        self.api_key = api_key
        self.model_name = model_name
        self.provider, self.model_part = self._parse_model_name()
        self.models = self._load_models()
        self.model_config = self._validate_model()
        self.client = self._initialize_client()
        self._validate_access()

    def _parse_model_name(self) -> tuple[str, str]:
        """Split and validate model name format"""
        if "/" not in self.model_name:
            raise ValueError("Model name must be in 'provider/model-name' format")

        provider, model_part = self.model_name.split("/", 1)
        return provider.lower(), model_part

    def _load_models(self) -> List[Dict]:
        """Load provider-specific model configurations"""
        models_path = (
            Path(__file__).parent.parent / "providers" / self.provider / "models.json"
        )

        try:
            with open(models_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Provider {self.provider} not supported")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid models file for {self.provider}")

    def _validate_model(self) -> Dict:
        """Verify model exists in provider's catalog"""
        for model in self.models:
            if model["modelName"] == self.model_part:
                return model
        raise ValueError(f"Model {self.model_part} not found in {self.provider}")

    def _initialize_client(self):
        """Initialize the appropriate client SDK"""
        if self.provider in self.PROVIDER_CLIENTS:
            client_class = self.PROVIDER_CLIENTS[self.provider]
            return client_class(api_key=self.api_key)

        raise NotImplementedError(f"Provider {self.provider} not implemented")

    def _validate_access(self):
        """Verify API key validity for the provider"""
        try:
            if self.provider == "openai":
                self.client.models.list()
            elif self.provider == "anthropic":
                self.client.models.get("claude-3-opus-20240229")
            elif self.provider == "google":
                genai.configure(api_key=self.api_key)
                list(genai.list_models())
        except Exception as e:
            raise ValueError(f"API key validation failed: {str(e)}")

    def format_prompt(self, prompt: str, system_prompt: str = None) -> str:
        """Apply provider-specific prompt formatting"""
        template = self.model_config["promptTemplate"]
        system = system_prompt or self.model_config.get("systemPrompt", "")

        if "{system}" in template and "{prompt}" in template:
            return template.format(system=system, prompt=prompt)
        return template.replace("%1", prompt)

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Dict:
        """Handle generation with provider-specific logic"""
        handler_name = self.PROVIDER_HANDLERS.get(self.provider)
        if not handler_name:
            raise NotImplementedError(f"No handler for {self.provider}")

        return getattr(self, handler_name)(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def handle_openai(self, **kwargs) -> Dict:
        """OpenAI generation handler"""
        formatted_prompt = self.format_prompt(kwargs["prompt"], kwargs["system_prompt"])

        response = self.client.chat.completions.create(
            model=self.model_part,
            messages=[{"role": "user", "content": formatted_prompt}],
            max_tokens=kwargs["max_tokens"],
            temperature=kwargs["temperature"],
        )

        return self.process_response(response, kwargs["prompt"])

    def handle_anthropic(self, **kwargs) -> Dict:
        """Anthropic Claude generation handler"""
        from anthropic.types import Message

        formatted_prompt = self.format_prompt(kwargs["prompt"], kwargs["system_prompt"])

        response: Message = self.client.messages.create(
            model=self.model_part,
            max_tokens=kwargs["max_tokens"],
            temperature=kwargs["temperature"],
            messages=[{"role": "user", "content": formatted_prompt}],
        )

        return self.process_response(response, kwargs["prompt"])

    def handle_google(self, **kwargs) -> Dict:
        """Google Gemini generation handler"""
        formatted_prompt = self.format_prompt(kwargs["prompt"], kwargs["system_prompt"])

        model = genai.GenerativeModel(self.model_part)
        response = model.generate_content(
            formatted_prompt,
            generation_config={
                "temperature": kwargs["temperature"],
                "max_output_tokens": kwargs["max_tokens"],
            },
        )

        return self.process_response(response, kwargs["prompt"])

    def process_response(self, response, original_prompt: str) -> Dict:
        """Universal response processing with cost calculation"""
        input_tokens = self.count_tokens(original_prompt)
        output_tokens = self.count_tokens(response.text)

        input_cost = (input_tokens / 1000) * self.model_config["inputPricePer1KTokens"]
        output_cost = (output_tokens / 1000) * self.model_config[
            "outputPricePer1KTokens"
        ]
        total_cost = round(input_cost + output_cost, 6)

        return {
            "text": response.text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost,
            "model": self.model_name,
            "provider": self.provider,
        }

    def count_tokens(self, text: str) -> int:
        """Provider-specific token counting"""
        if self.provider == "openai":
            return self.client.tokenizers.from_pretrained("gpt2").encode(text).ids
        elif self.provider == "anthropic":
            return self.client.count_tokens(text)
        elif self.provider == "google":
            return genai.count_tokens(text).total_tokens
        # Default approximation
        return len(text.split())
