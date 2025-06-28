# IndoxRouter Client

A unified client for various AI providers, including OpenAI, anthropic, Google, and Mistral.

## Features

- **Unified API**: Access multiple AI providers through a single API
- **Simple Interface**: Easy-to-use methods for chat, completion, embeddings, and image generation
- **Error Handling**: Standardized error handling across providers
- **Authentication**: Secure cookie-based authentication

## Installation

```bash
pip install indoxrouter
```

## Usage

### Initialization

```python
from indoxrouter import Client

# Initialize with API key
client = Client(api_key="your_api_key")

# Using environment variables
# Set INDOX_ROUTER_API_KEY environment variable
import os
os.environ["INDOX_ROUTER_API_KEY"] = "your_api_key"
client = Client()

# Connect to a custom server
client = Client(
    api_key="your_api_key",
    base_url="https://your-indoxrouter-server.com"
)
```

### Authentication

IndoxRouter uses cookie-based authentication with JWT tokens. The client handles this automatically by:

1. Taking your API key and exchanging it for JWT tokens using the server's authentication endpoints
2. Storing the JWT tokens in cookies
3. Using the cookies for subsequent requests
4. Automatically refreshing tokens when they expire

```python
# Authentication is handled automatically when creating the client
client = Client(api_key="your_api_key")
```

### Testing Your API Key

The package includes a test script to verify your API key and connection:

```bash
# Run the test script with your API key
python -m indoxrouter.test_api_key --api-key YOUR_API_KEY

# Or set the environment variable and run
export INDOX_ROUTER_API_KEY=YOUR_API_KEY
python -m indoxrouter.test_api_key

# To see detailed debugging information
python -m indoxrouter.test_api_key --debug
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
# OpenAI Image Generation
response = client.images(
    prompt="A serene landscape with mountains and a lake",
    model="openai/dall-e-3",
    size="1024x1024",
    quality="standard",  # Options: standard, hd
    style="vivid"  # Options: vivid, natural
)

print(f"Image URL: {response['data'][0]['url']}")

# Google Imagen Image Generation
from indoxrouter.constants import GOOGLE_IMAGE_MODEL

response = client.images(
    prompt="A robot holding a red skateboard in a futuristic city",
    model=GOOGLE_IMAGE_MODEL,
    n=2,  # Generate 2 images
    negative_prompt="broken, damaged, low quality",
    guidance_scale=7.5,  # Control adherence to prompt
    seed=42,  # For reproducible results
)

# xAI Grok Image Generation
from indoxrouter.constants import XAI_IMAGE_MODEL

response = client.images(
    prompt="A cat in a tree",
    model=XAI_IMAGE_MODEL,
    n=1,
    response_format="b64_json"  # Get base64 encoded image
)

# Access base64 encoded image data
if "b64_json" in response["data"][0]:
    b64_data = response["data"][0]["b64_json"]
    # Use the base64 data (e.g., to display in HTML or save to file)
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
