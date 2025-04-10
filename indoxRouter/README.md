# IndoxRouter Client

A unified client for various AI providers, including OpenAI, Anthropic, Google, and Mistral.

## Features

- **Unified API**: Access multiple AI providers through a single API
- **Simple Interface**: Easy-to-use methods for chat, completion, embeddings, and image generation
- **Error Handling**: Standardized error handling across providers
- **Authentication**: Automatic token management

## Installation

```bash
pip install indoxrouter
```

## Usage

### Initialization

```python
from indoxrouter import Client

# Initialize with API key (default connects to localhost:8000)
client = Client(api_key="your_api_key")

# Or specify a custom server URL
client = Client(
    api_key="your_api_key",
    base_url="http://your-server-url:8000"
)

# Connect to Docker container inside the Docker network
client = Client(
    api_key="your_api_key",
    base_url="http://indoxrouter-server:8000"
)

# Using environment variables
# Set INDOX_ROUTER_API_KEY environment variable
import os
os.environ["INDOX_ROUTER_API_KEY"] = "your_api_key"
client = Client()
```

### Chat Completions

```python
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
    model="openai/gpt-4o-mini",  # Provider/model format
    temperature=0.7
)

print(response["choices"][0]["message"]["content"])
```

### Text Completions

```python
response = client.completion(
    prompt="Once upon a time,",
    model="openai/gpt-4o-mini",
    max_tokens=100
)

print(response["choices"][0]["text"])
```

### Embeddings

```python
response = client.embeddings(
    text=["Hello world", "AI is amazing"],
    model="openai/text-embedding-3-small"
)

print(f"Dimensions: {len(response['data'][0]['embedding'])}")
print(f"First embedding: {response['data'][0]['embedding'][:5]}...")
```

### Image Generation

```python
response = client.images(
    prompt="A serene landscape with mountains and a lake",
    model="openai/dall-e-3",
    size="1024x1024"
)

print(f"Image URL: {response['data'][0]['url']}")
```

### Streaming Responses

```python
for chunk in client.chat(
    messages=[{"role": "user", "content": "Write a short story."}],
    model="openai/gpt-4o-mini",
    stream=True
):
    if chunk.get("choices") and len(chunk["choices"]) > 0:
        content = chunk["choices"][0].get("delta", {}).get("content", "")
        print(content, end="", flush=True)
```

### Getting Available Models

```python
# Get all providers and models
providers = client.models()
for provider in providers:
    print(f"Provider: {provider['name']}")
    for model in provider["models"]:
        print(f"  - {model['id']}: {model['description'] or ''}")

# Get models for a specific provider
openai_provider = client.models("openai")
print(f"OpenAI models: {[m['id'] for m in openai_provider['models']]}")
```

## Error Handling

```python
from indoxrouter import Client, ModelNotFoundError, ProviderError

try:
    client = Client(api_key="your_api_key")
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="nonexistent-provider/nonexistent-model"
    )
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Context Manager

```python
with Client(api_key="your_api_key") as client:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello!"}],
        model="openai/gpt-4o-mini"
    )
    print(response["choices"][0]["message"]["content"])
# Client is automatically closed when exiting the block
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
