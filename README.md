# indoxRouter

<p align="center">
  <img src="https://raw.githubusercontent.com/indoxrouter/indoxrouter/main/docs/assets/logo.png" alt="indoxRouter Logo" width="200"/>
</p>

<p align="center">
  <strong>A unified interface for various LLM providers</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/indoxRouter/"><img src="https://img.shields.io/pypi/v/indoxRouter.svg" alt="PyPI version"></a>
  <a href="https://github.com/indoxrouter/indoxrouter/blob/main/LICENSE"><img src="https://img.shields.io/github/license/indoxrouter/indoxrouter" alt="License"></a>
  <a href="https://github.com/indoxrouter/indoxrouter/stargazers"><img src="https://img.shields.io/github/stars/indoxrouter/indoxrouter" alt="GitHub stars"></a>
</p>

## Overview

indoxRouter is a powerful Python library that provides a unified interface to interact with various Large Language Model (LLM) providers. With a single API key, you can access models from OpenAI, Anthropic, Mistral, Google, and more, without having to manage multiple provider-specific API keys and implementations.

### Key Features

- **Single API for Multiple Providers**: Access models from OpenAI, Anthropic, Mistral, Google, and more with a single API key
- **Standardized Response Format**: Consistent response format across all providers
- **Streaming Support**: Stream responses for real-time applications
- **Cost Tracking**: Track token usage and costs across providers
- **Rate Limiting**: Built-in rate limiting to prevent exceeding provider quotas
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Authentication**: Secure authentication with JWT tokens
- **Type Hints**: Full type hints for better IDE support

## Installation

```bash
pip install indoxRouter
```

For development:

```bash
pip install indoxRouter[dev]
```

## Quick Start

```python
from indoxRouter import Client
from indoxRouter.models import ChatMessage

# Initialize the client with your API key
client = Client(api_key="your-api-key")

# Chat completion with OpenAI
response = client.chat(
    messages=[
        {"role": "user", "content": "What are three fun activities to do in New York?"}
    ],
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
)

print(response.data)
```

## Available Providers

indoxRouter supports the following providers:

- OpenAI
- Anthropic (Claude)
- Mistral
- Google
- Cohere

## Core Features

### Chat Completion

```python
response = client.chat(
    messages=[
        {"role": "user", "content": "What are three fun activities to do in New York?"}
    ],
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
)
```

### Text Completion

```python
response = client.completion(
    prompt="Write a short story about a robot learning to paint.",
    model="anthropic/claude-3-haiku",
    temperature=0.7,
    max_tokens=500,
)
```

### Embeddings

```python
response = client.embeddings(
    text="This is a sample text to embed.",
    model="openai/text-embedding-3-small",
)
```

### Image Generation

```python
response = client.image(
    prompt="A futuristic city with flying cars and neon lights",
    model="openai/dall-e-3",
    size="1024x1024",
)
```

### Streaming

```python
generator = client.chat(
    messages=[
        {"role": "user", "content": "Write a short story about a robot learning to paint."}
    ],
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
    stream=True,
    return_generator=True,
)

for chunk in generator:
    if isinstance(chunk, dict) and chunk.get("is_usage_info"):
        # This is the final usage info
        usage_info = chunk
    else:
        # This is a content chunk
        print(chunk, end="", flush=True)
```

## Provider and Model Information

```python
# List all available providers
providers = client.providers()

# List all available models
models = client.models()

# List models for a specific provider
openai_models = client.models(provider="openai")

# Get information about a specific model
model_info = client.model_info(provider="openai", model="gpt-4o-mini")
```

## Configuration

indoxRouter can be configured using environment variables or a configuration file:

```python
# Set API key via environment variable
import os
os.environ["INDOX_ROUTER_API_KEY"] = "your-api-key"

# Or provide it directly to the client
client = Client(api_key="your-api-key")
```

## Error Handling

indoxRouter provides comprehensive error handling:

```python
from indoxRouter import Client
from indoxRouter.exceptions import AuthenticationError, RateLimitError, ProviderError

try:
    client = Client(api_key="invalid-api-key")
except AuthenticationError as e:
    print(f"Authentication error: {e}")

try:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="nonexistent-model",
    )
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Documentation

For detailed documentation, visit [https://docs.indoxrouter.com](https://docs.indoxrouter.com).

## Examples

Check out the [examples](https://github.com/indoxrouter/indoxrouter/tree/main/examples) directory for more examples.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
