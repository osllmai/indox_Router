# Provider Integration

IndoxRouter is designed to integrate with multiple AI model providers through a plugin-based architecture. Each provider is implemented as a separate module that inherits from the `BaseProvider` class.

## Supported Providers

IndoxRouter currently supports the following providers:

- **OpenAI**: Full support for chat, completion, embedding, and image generation
- **Mistral**: Support for chat, completion, and embedding
- **DeepSeek**: Support for chat and completion
- **Anthropic**: Support for chat (Claude models)
- **Google**: Support for chat and embedding (Gemini models)
- **Cohere**: Support for chat, completion, and embedding

## Provider Architecture

### Base Provider

All provider implementations inherit from the `BaseProvider` class which defines the common interface and utility methods:

```python
class BaseProvider:
    """Base class for all providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.initialize_client()

    def initialize_client(self):
        """Initialize the provider client library."""
        raise NotImplementedError

    async def chat(self, messages, **kwargs):
        """Generate a chat completion."""
        raise NotImplementedError

    async def completion(self, prompt, **kwargs):
        """Generate a text completion."""
        raise NotImplementedError

    async def embedding(self, text, **kwargs):
        """Generate embeddings for the given text."""
        raise NotImplementedError

    async def image(self, prompt, **kwargs):
        """Generate an image from the given prompt."""
        raise NotImplementedError
```

### Provider Factory

Providers are instantiated through the provider factory pattern, which allows the application to dynamically select the appropriate provider based on the request:

```python
def get_provider(provider_id: str, api_key: str, model: str) -> BaseProvider:
    """Get a provider instance."""
    provider_id = provider_id.lower()

    # Check if provider is available
    if provider_id not in AVAILABLE_PROVIDERS:
        raise ProviderNotFoundError(f"Provider '{provider_id}' not available")

    # Get the factory function
    factory_func = PROVIDER_FACTORIES.get(provider_id)
    if not factory_func:
        raise ProviderNotFoundError(f"Provider '{provider_id}' not implemented")

    # Create and return the provider instance
    return factory_func(api_key, model)
```

## Provider Configuration

Provider-specific configuration is stored in the `.env` file or environment variables:

```env
# OpenAI configuration
OPENAI_API_KEY=sk-...

# Mistral configuration
MISTRAL_API_KEY=...

# DeepSeek configuration
DEEPSEEK_API_KEY=...

# Anthropic configuration
ANTHROPIC_API_KEY=...

# Google configuration
GOOGLE_API_KEY=...

# Cohere configuration
COHERE_API_KEY=...
```

Additionally, model information for each provider is stored in JSON files in the `app/providers/json/` directory:

```
app/providers/json/
  ├── openai.json
  ├── mistral.json
  ├── deepseek.json
  ├── claude.json
  ├── google.json
  ├── cohere.json
  └── ...
```

These files define the available models, their capabilities, and pricing information.

## Implementing a New Provider

To add a new provider to IndoxRouter:

1. Create a new provider module in `app/providers/` (e.g., `app/providers/new_provider.py`)
2. Implement the provider class, inheriting from `BaseProvider`
3. Create a JSON model definition file in `app/providers/json/` (e.g., `app/providers/json/new_provider.json`)
4. Add the provider to the factory mapping in `app/providers/factory.py`
5. Add the provider to the `AVAILABLE_PROVIDERS` list in `app/constants.py`

### Example Provider Implementation

Here's a simplified example of a provider implementation:

```python
from .base_provider import BaseProvider
from app.exceptions import ProviderError

class NewProvider(BaseProvider):
    """Implementation for New Provider."""

    def initialize_client(self):
        """Initialize the provider client."""
        try:
            from new_provider_library import Client
            self.client = Client(api_key=self.api_key)
        except ImportError:
            raise ProviderError("New Provider library not installed")
        except Exception as e:
            raise ProviderError(f"Failed to initialize New Provider client: {str(e)}")

    async def chat(self, messages, **kwargs):
        """Generate a chat completion."""
        try:
            # Extract parameters
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1000)

            # Convert to provider format
            provider_messages = self._convert_messages(messages)

            # Call provider API
            response = self.client.chat.create(
                model=self.model,
                messages=provider_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Convert response to standard format
            return {
                "data": response.choices[0].message.content,
                "usage": {
                    "tokens_prompt": response.usage.prompt_tokens,
                    "tokens_completion": response.usage.completion_tokens,
                    "tokens_total": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            raise ProviderError(f"New Provider chat error: {str(e)}")

    # Implement other methods: completion, embedding, image
```

## Request Transformation

Each provider implementation is responsible for transforming the standardized IndoxRouter request format into the provider-specific format, and transforming the provider's response back to the standardized format.

### Example Transformation Flow

1. Client sends a request to IndoxRouter in the standardized format
2. IndoxRouter routes the request to the appropriate provider
3. Provider transforms the request to the provider-specific format
4. Provider makes the API call to the external service
5. Provider transforms the response back to the standardized format
6. IndoxRouter returns the standardized response to the client

This approach allows clients to use a consistent API regardless of the underlying provider.
