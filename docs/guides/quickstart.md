# Quick Start Guide

This guide will help you get started with indoxRouter quickly. We'll cover the basics of setting up the client and making your first API calls.

## Installation

First, make sure you have indoxRouter installed:

```bash
pip install indoxRouter
```

For more detailed installation instructions, see the [Installation Guide](installation.md).

## Setting Up the Client

To use indoxRouter, you'll need to create a client instance with your API key:

```python
from indoxRouter import Client

# Initialize the client with your API key
client = Client(api_key="your-api-key")
```

You can also set your API key as an environment variable:

```python
import os
os.environ["INDOX_ROUTER_API_KEY"] = "your-api-key"

# Initialize the client without explicitly providing the API key
from indoxRouter import Client
client = Client()
```

## Basic Usage

### Chat Completion

Here's a simple example of using the chat completion API:

```python
# Define your messages
messages = [
    {"role": "user", "content": "What are three fun activities to do in New York?"}
]

# Make the API call
response = client.chat(
    messages=messages,
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
)

# Print the response
print(response.data)
```

### Text Completion

For simple text completion:

```python
response = client.completion(
    prompt="Write a short story about a robot learning to paint.",
    model="anthropic/claude-3-haiku",
    temperature=0.7,
    max_tokens=500,
)

print(response.data)
```

### Embeddings

Generate embeddings for text:

```python
response = client.embeddings(
    text="This is a sample text to embed.",
    model="openai/text-embedding-3-small",
)

print(response.data)
```

### Image Generation

Generate images from text prompts:

```python
response = client.image(
    prompt="A futuristic city with flying cars and neon lights",
    model="openai/dall-e-3",
    size="1024x1024",
)

print(response.data)
```

## Exploring Available Models

You can list all available providers and models:

```python
# List all providers
providers = client.providers()
print(f"Available providers: {[p['id'] for p in providers]}")

# List all models
models = client.models()
print(f"Available models: {models}")

# Get information about a specific model
model_info = client.model_info(provider="openai", model="gpt-4o-mini")
print(model_info)
```

## Next Steps

Now that you've made your first API calls, you can explore more advanced features:

- [Chat Completion Guide](chat.md)
- [Streaming Responses](streaming.md)
- [Configuration Options](configuration.md)
- [Error Handling](../examples/errors.md)

For more examples, check out the [Examples](../examples/) section.
