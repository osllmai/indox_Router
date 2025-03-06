"""
Models resource module for indoxRouter.
This module contains the Models resource class for model-related functionality.
"""

from typing import Dict, List, Any, Optional

from .base import BaseResource
from ..models import ModelInfo
from ..utils import list_available_providers, list_available_models, get_model_info
from ..exceptions import ProviderNotFoundError, ModelNotFoundError


class Models(BaseResource):
    """Resource class for model-related functionality."""

    def list_providers(self) -> List[Dict[str, Any]]:
        """
        List all available providers.

        Returns:
            A list of provider dictionaries with information.
        """
        providers = list_available_providers()
        result = []

        for provider in providers:
            # Get the first model to extract provider information
            try:
                models = list_available_models(provider)
                if provider in models and models[provider]:
                    model_info = models[provider][0]
                    result.append(
                        {
                            "id": provider,
                            "name": provider.capitalize(),
                            "description": model_info.get(
                                "providerDescription",
                                f"{provider.capitalize()} AI provider",
                            ),
                            "website": model_info.get("providerWebsite", ""),
                            "model_count": len(models[provider]),
                        }
                    )
                else:
                    result.append(
                        {
                            "id": provider,
                            "name": provider.capitalize(),
                            "description": f"{provider.capitalize()} AI provider",
                            "website": "",
                            "model_count": 0,
                        }
                    )
            except Exception:
                # If there's an error, still include the provider with minimal info
                result.append(
                    {
                        "id": provider,
                        "name": provider.capitalize(),
                        "description": f"{provider.capitalize()} AI provider",
                        "website": "",
                        "model_count": 0,
                    }
                )

        return result

    def list(self, provider: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all available models, optionally filtered by provider.

        Args:
            provider: The name of the provider to filter by. If None, lists models from all providers.

        Returns:
            A dictionary mapping provider names to lists of model dictionaries.

        Raises:
            ProviderNotFoundError: If the specified provider is not found.
        """
        return list_available_models(provider)

    def get(self, provider: str, model: str) -> ModelInfo:
        """
        Get information about a specific model from a provider.

        Args:
            provider: The name of the provider.
            model: The name of the model.

        Returns:
            A ModelInfo object containing information about the model.

        Raises:
            ProviderNotFoundError: If the provider is not found.
            ModelNotFoundError: If the model is not found.
        """
        model_data = get_model_info(provider, model)

        return ModelInfo(
            name=model_data.get("modelName", model),
            provider=provider,
            type=model_data.get("type", "Unknown"),
            description=model_data.get("description"),
            input_price_per_1k_tokens=model_data.get("inputPricePer1KTokens", 0.0),
            output_price_per_1k_tokens=model_data.get("outputPricePer1KTokens", 0.0),
            context_window=model_data.get("contextWindow"),
            max_output_tokens=model_data.get("maxOutputTokens"),
            recommended=model_data.get("recommended", False),
            commercial=model_data.get("commercial", False),
            pricey=model_data.get("pricey", False),
            raw_info=model_data,
        )
