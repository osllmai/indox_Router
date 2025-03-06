"""
Utilities module for indoxRouter.
This module contains utility functions used throughout the application.
"""

import os
import json
import time
import datetime
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from ..exceptions import ProviderNotFoundError, ModelNotFoundError


def load_provider_models(provider_name: str) -> List[Dict[str, Any]]:
    """
    Load models for a specific provider from the JSON file.

    Args:
        provider_name: The name of the provider.

    Returns:
        A list of model dictionaries.

    Raises:
        ProviderNotFoundError: If the provider JSON file is not found.
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    providers_dir = os.path.join(current_dir, "providers")
    provider_file = os.path.join(providers_dir, f"{provider_name}.json")
    if not os.path.exists(provider_file):
        raise ProviderNotFoundError(f"Provider '{provider_name}' not found.")

    with open(provider_file, "r") as f:
        return json.load(f)


def get_model_info(provider_name: str, model_name: str) -> Dict[str, Any]:
    """
    Get information about a specific model from a provider.

    Args:
        provider_name: The name of the provider.
        model_name: The name of the model.

    Returns:
        A dictionary containing information about the model.

    Raises:
        ProviderNotFoundError: If the provider is not found.
        ModelNotFoundError: If the model is not found.
    """
    models = load_provider_models(provider_name)

    for model in models:
        if model.get("modelName") == model_name:
            return model

    raise ModelNotFoundError(
        f"Model '{model_name}' not found for provider '{provider_name}'."
    )


# def calculate_cost(
#     provider_name: str, model_name: str, input_tokens: int, output_tokens: int
# ) -> float:
#     """
#     Calculate the cost of a request based on the provider, model, and token counts.

#     Args:
#         provider_name: The name of the provider.
#         model_name: The name of the model.
#         input_tokens: The number of input tokens.
#         output_tokens: The number of output tokens.

#     Returns:
#         The cost of the request.

#     Raises:
#         ProviderNotFoundError: If the provider is not found.
#         ModelNotFoundError: If the model is not found.
#     """
#     model_info = get_model_info(provider_name, model_name)

#     input_cost = model_info.get("inputPricePer1KTokens", 0) * (input_tokens / 1000)
#     output_cost = model_info.get("outputPricePer1KTokens", 0) * (output_tokens / 1000)

#     return input_cost + output_cost


def list_available_providers() -> List[str]:
    """
    List all available providers.

    Returns:
        A list of provider names.
    """
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    providers_dir = os.path.join(current_dir, "providers")

    providers = []
    for file in os.listdir(providers_dir):
        if file.endswith(".json"):
            providers.append(file[:-5])  # Remove .json extension

    return providers


def list_available_models(
    provider_name: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    List all available models, optionally filtered by provider.

    Args:
        provider_name: The name of the provider to filter by. If None, lists models from all providers.

    Returns:
        A dictionary mapping provider names to lists of model dictionaries.

    Raises:
        ProviderNotFoundError: If the specified provider is not found.
    """
    if provider_name:
        return {provider_name: load_provider_models(provider_name)}

    providers = list_available_providers()
    models = {}

    for provider in providers:
        try:
            models[provider] = load_provider_models(provider)
        except ProviderNotFoundError:
            continue

    return models


def count_tokens(text: Union[str, List[Dict[str, str]]]) -> int:
    """
    Count the number of tokens in a text or list of messages.

    This is a simplified placeholder implementation for development mode.
    In a production environment, you would use a proper tokenizer.

    Args:
        text: The text or list of messages to count tokens for.

    Returns:
        The estimated number of tokens.
    """
    if isinstance(text, str):
        # Very rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
    elif isinstance(text, list):
        # For chat messages, count tokens in each message
        total = 0
        for message in text:
            if isinstance(message, dict) and "content" in message:
                total += len(message["content"]) // 4
            elif hasattr(message, "content"):
                total += len(message.content) // 4
        return total
    return 0


def calculate_cost(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    """
    Calculate the cost of a request based on the provider/model and token counts.

    Args:
        model: Provider and model name in format "provider/model_name"
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens used

    Returns:
        The calculated cost in USD
    """
    try:
        provider, model_name = model.split("/", 1)
    except ValueError:
        raise ValueError(
            f"Invalid model format: {model}. Expected 'provider/model_name'"
        )

    # # Load provider's model data
    # json_path = Path(__file__).parent / "providers" / f"{provider}.json"
    # try:
    #     with open(json_path, "r") as f:
    #         models = json.load(f)
    # except FileNotFoundError:
    #     raise ValueError(f"Provider not found: {provider}")
    models = load_provider_models(provider_name=provider)

    # Find model in JSON data
    model_info: Optional[dict] = next(
        (m for m in models if m.get("modelName") == model_name), None
    )

    if not model_info:
        raise ValueError(f"Model not found: {model_name} in provider {provider}")

    # Handle different model types
    model_type = model_info.get("type", "Text Generation").lower()

    if "image" in model_type:
        # Image models - price per image
        # Assume inputPricePer1KTokens is price per image
        return input_tokens * model_info.get("inputPricePer1KTokens", 0.0)

    # Text models - price per token
    input_cost = (input_tokens / 1000) * model_info.get("inputPricePer1KTokens", 0.0)
    output_cost = (output_tokens / 1000) * model_info.get("outputPricePer1KTokens", 0.0)
    return input_cost + output_cost


def format_timestamp(timestamp: Union[int, float, datetime, None] = None) -> str:
    """
    Format a timestamp as a human-readable string.

    Args:
        timestamp: The timestamp to format. If None, uses the current time.

    Returns:
        A formatted timestamp string.
    """
    if timestamp is None:
        timestamp = time.time()

    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        dt = datetime.now()

    return dt.strftime("%Y-%m-%d %H:%M:%S")
