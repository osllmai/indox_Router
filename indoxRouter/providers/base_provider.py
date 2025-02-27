from abc import ABC, abstractmethod
from pathlib import Path
import json
from typing import Dict, List


class BaseProvider(ABC):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.models = self._load_models()
        self.model_config = self._validate_model()
        self.client = self._initialize_client()

        if not self._validate_access():
            raise ValueError("Invalid API key or unauthorized access")

    def _load_models(self) -> List[Dict]:
        """Load models from provider's JSON file"""
        provider_name = self.__class__.__name__.lower()
        models_path = (
            Path(__file__).parent.parent / "providers" / provider_name / "models.json"
        )

        try:
            with open(models_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Models file not found for {provider_name}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {provider_name} models file")

    def _validate_model(self) -> Dict:
        """Validate model exists in provider's catalog"""
        for model in self.models:
            if model["modelName"] == self.model_name:
                return model
        raise ValueError(f"Model {self.model_name} not found")

    @abstractmethod
    def _initialize_client(self):
        """Initialize provider-specific client"""
        pass

    @abstractmethod
    def _validate_access(self) -> bool:
        """Validate API key access"""
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict:
        """Generate completion from model"""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens for text"""
        pass

    def get_model_info(self) -> Dict:
        """Get model configuration details"""
        return {
            "name": self.model_config["name"],
            "description": self.model_config["description"],
            "input_price": self.model_config["inputPricePer1KTokens"],
            "output_price": self.model_config["outputPricePer1KTokens"],
            "context_window": self.model_config["contextWindows"],
        }
