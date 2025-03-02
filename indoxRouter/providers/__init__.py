# Import all provider modules
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Dictionary to store provider modules
PROVIDERS = {}

# Import providers with graceful error handling
try:
    from . import openai

    PROVIDERS["openai"] = openai
except ImportError as e:
    logger.warning(f"OpenAI provider not available: {e}")

try:
    from . import claude

    PROVIDERS["claude"] = claude
except ImportError as e:
    logger.warning(f"Claude provider not available: {e}")

try:
    from . import mistral

    PROVIDERS["mistral"] = mistral
except ImportError as e:
    logger.warning(f"Mistral provider not available: {e}")

try:
    from . import cohere

    PROVIDERS["cohere"] = cohere
except ImportError as e:
    logger.warning(f"Cohere provider not available: {e}")

try:
    from . import google

    PROVIDERS["google"] = google
except ImportError as e:
    logger.warning(f"Google provider not available: {e}")

try:
    from . import meta

    PROVIDERS["meta"] = meta
except ImportError as e:
    logger.warning(f"Meta provider not available: {e}")

try:
    from . import ai21

    PROVIDERS["ai21"] = ai21
except ImportError as e:
    logger.warning(f"AI21 provider not available: {e}")

try:
    from . import llama

    PROVIDERS["llama"] = llama
except ImportError as e:
    logger.warning(f"Llama provider not available: {e}")

try:
    from . import nvidia

    PROVIDERS["nvidia"] = nvidia
except ImportError as e:
    logger.warning(f"NVIDIA provider not available: {e}")

try:
    from . import deepseek

    PROVIDERS["deepseek"] = deepseek
except ImportError as e:
    logger.warning(f"Deepseek provider not available: {e}")

try:
    from . import databricks

    PROVIDERS["databricks"] = databricks
except ImportError as e:
    logger.warning(f"Databricks provider not available: {e}")


def get_provider(provider_name, api_key, model_name):
    """
    Get a provider instance by name.

    Args:
        provider_name (str): The name of the provider
        api_key (str): The API key for the provider
        model_name (str): The name of the model to use

    Returns:
        BaseProvider: An instance of the provider

    Raises:
        ValueError: If the provider is not found
    """
    if provider_name not in PROVIDERS:
        raise ValueError(f"Provider {provider_name} not found or not available")

    provider_module = PROVIDERS[provider_name]
    return provider_module.Provider(api_key, model_name)
