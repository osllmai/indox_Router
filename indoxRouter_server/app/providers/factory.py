"""
Provider factory for the IndoxRouter server.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from app.providers.base_provider import BaseProvider
from app.exceptions import ProviderNotFoundError


# Import provider implementations
# These will be implemented in separate files
def get_openai_provider(api_key: str, model: str) -> BaseProvider:
    """Get an OpenAI provider instance."""
    from app.providers.openai_provider import OpenAIProvider

    return OpenAIProvider(api_key, model)


def get_anthropic_provider(api_key: str, model: str) -> BaseProvider:
    """Get an Anthropic provider instance."""
    from app.providers.anthropic_provider import AnthropicProvider

    return AnthropicProvider(api_key, model)


def get_cohere_provider(api_key: str, model: str) -> BaseProvider:
    """Get a Cohere provider instance."""
    from app.providers.cohere_provider import CohereProvider

    return CohereProvider(api_key, model)


def get_google_provider(api_key: str, model: str) -> BaseProvider:
    """Get a Google provider instance."""
    from app.providers.google_provider import GoogleProvider

    return GoogleProvider(api_key, model)


def get_mistral_provider(api_key: str, model: str) -> BaseProvider:
    """Get a Mistral provider instance."""
    from app.providers.mistral_provider import MistralProvider

    return MistralProvider(api_key, model)


def get_deepseek_provider(api_key: str, model: str) -> BaseProvider:
    """Get a DeepSeek provider instance."""
    from app.providers.deepseek_provider import DeepSeekProvider

    return DeepSeekProvider(api_key, model)


# Provider factory mapping
PROVIDER_FACTORIES = {
    "openai": get_openai_provider,
    "anthropic": get_anthropic_provider,
    "cohere": get_cohere_provider,
    "google": get_google_provider,
    "mistral": get_mistral_provider,
    "deepseek": get_deepseek_provider,
}


def get_provider(provider_id: str, api_key: str, model: str) -> BaseProvider:
    """
    Get a provider instance based on the provider ID.

    Args:
        provider_id: The provider ID.
        api_key: The API key for the provider.
        model: The model to use.

    Returns:
        A provider instance.

    Raises:
        ProviderNotFoundError: If the provider is not found.
    """
    # Normalize provider_id to lowercase
    print(f"DEBUG: get_provider called with provider_id={provider_id}, model={model}")
    provider_id = provider_id.lower()

    # If the provider is not found, raise an error
    if provider_id not in PROVIDER_FACTORIES:
        available_providers = list(PROVIDER_FACTORIES.keys())
        raise ProviderNotFoundError(
            f"Provider '{provider_id}' not found. Available providers: {', '.join(available_providers)}"
        )

    try:
        # Get the factory function for the provider
        factory_func = PROVIDER_FACTORIES[provider_id]

        # Create the provider instance
        return factory_func(api_key, model)
    except Exception as e:
        # Re-raise with more context
        raise ProviderNotFoundError(
            f"Error creating provider '{provider_id}': {str(e)}"
        )
