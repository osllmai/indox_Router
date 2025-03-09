# IndoxRouter Client

A unified client for various AI providers, including OpenAI, Anthropic, Cohere, Google, and Mistral.

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

# Initialize with API key
client = Client(api_key="your_api_key", base_url="http://your-server-url:8000")

# Or initialize with username and password
client = Client(
    username="your_username",
    password="your_password",
    base_url="http://your-server-url:8000"
)

# Using environment variables
# Set INDOXROUTER_API_KEY or INDOXROUTER_USERNAME and INDOXROUTER_PASSWORD
client = Client(base_url="http://your-server-url:8000")
```

### Chat Completions

```python
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7
)

print(response["choices"][0]["message"]["content"])
```

### Text Completions

```python
response = client.completion(
    prompt="Once upon a time,",
    provider="openai",
    model="gpt-3.5-turbo-instruct",
    max_tokens=100
)

print(response["choices"][0]["text"])
```

### Embeddings

```python
response = client.embeddings(
    text=["Hello world", "AI is amazing"],
    provider="openai",
    model="text-embedding-ada-002"
)

print(f"Dimensions: {response['dimensions']}")
print(f"First embedding: {response['embeddings'][0][:5]}...")
```

### Image Generation

```python
response = client.images(
    prompt="A serene landscape with mountains and a lake",
    provider="openai",
    model="dall-e-3",
    size="1024x1024"
)

print(f"Image URL: {response['images'][0]['url']}")
```

### Streaming Responses

```python
for chunk in client.chat(
    messages=[{"role": "user", "content": "Write a short story."}],
    stream=True
):
    if "choices" in chunk and len(chunk["choices"]) > 0:
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
        print(f"  - {model['id']}: {model['name']}")

# Get models for a specific provider
openai_provider = client.models("openai")
print(f"OpenAI models: {[m['id'] for m in openai_provider['models']]}")
```

## Error Handling

```python
from indoxrouter import Client, ModelNotFoundError, ProviderError

try:
    client = Client(api_key="your_api_key", base_url="http://your-server-url:8000")
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        provider="nonexistent",
        model="nonexistent-model"
    )
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Context Manager

```python
with Client(api_key="your_api_key", base_url="http://your-server-url:8000") as client:
    response = client.chat([{"role": "user", "content": "Hello!"}])
    print(response["choices"][0]["message"]["content"])
# Client is automatically closed when exiting the block
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
