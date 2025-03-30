"""
Model information utilities for indoxRouter server.
"""

import os
import json
from typing import Dict, List, Any, Optional

# Path to the JSON files
JSON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "providers", "json")

# Cache for model information
_model_info_cache = {}


def load_provider_models(provider: str) -> List[Dict[str, Any]]:
    """
    Load model information for a provider from its JSON file.

    Args:
        provider: The provider ID.

    Returns:
        A list of model information dictionaries.
    """
    # Check if the provider is already in the cache
    if provider in _model_info_cache:
        return _model_info_cache[provider]

    # Map provider IDs to JSON file names
    provider_map = {
        "openai": "openai.json",
        "anthropic": "claude.json",
        "cohere": "cohere.json",
        "google": "google.json",
        "mistral": "mistral.json",
        "meta": "meta.json",
        "nvidia": "nvidia.json",
        "databricks": "databricks.json",
        "ai21labs": "ai21labs.json",
        "qwen": "qwen.json",
        "deepseek": "deepseek.json",
    }

    # Get the JSON file name for the provider
    json_file = provider_map.get(provider.lower())
    if not json_file:
        return []

    # Load the JSON file
    try:
        with open(os.path.join(JSON_DIR, json_file), "r") as f:
            models = json.load(f)

        # Cache the models
        _model_info_cache[provider] = models

        return models
    except Exception as e:
        print(f"Error loading model information for {provider}: {e}")
        return []


def get_model_info(provider: str, model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific model.

    Args:
        provider: The provider ID.
        model_name: The name of the model.

    Returns:
        A dictionary containing information about the model, or None if not found.
    """
    models = load_provider_models(provider)

    # Find the model in the list
    for model in models:
        if model.get("modelName") == model_name:
            return model

    return None


def calculate_cost(
    provider: str, model_name: str, tokens_prompt: int, tokens_completion: int
) -> float:
    """
    Calculate the cost of a request based on token usage.

    Args:
        provider: The provider ID.
        model_name: The name of the model.
        tokens_prompt: The number of tokens in the prompt.
        tokens_completion: The number of tokens in the completion.

    Returns:
        The cost of the request in USD.
    """
    model_info = get_model_info(provider, model_name)
    if not model_info:
        # Default to a reasonable cost if model info is not found
        return (tokens_prompt + tokens_completion) * 0.0001

    # Get the input and output prices per 1K tokens
    input_price = model_info.get("inputPricePer1KTokens", 0.0)
    output_price = model_info.get("outputPricePer1KTokens", 0.0)

    # Calculate the cost
    input_cost = (tokens_prompt / 1000) * input_price
    output_cost = (tokens_completion / 1000) * output_price

    return input_cost + output_cost
