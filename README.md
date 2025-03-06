# indoxRouter

A unified interface for various LLM providers including OpenAI, Anthropic, Mistral, and more.

## Features

- **Unified API**: Consistent interface for multiple LLM providers
- **Model Management**: Easy access to model information and capabilities
- **Text Generation**: Generate text completions from prompts
- **Chat Generation**: Support for chat-based interactions
- **Embedding Generation**: Generate embeddings for text
- **Image Generation**: Create images from text prompts
- **Detailed Metrics**: Track token usage, latency, and costs
- **Error Handling**: Consistent error handling across providers

## Installation

```bash
pip install indoxRouter
```

## Quick Start

```python
from indoxRouter import Client, ChatMessage

# Initialize the client with just your API key
client = Client(api_key="your_indox_router_api_key")

# Simple chat example
messages = [
    ChatMessage(role="system", content="You are a helpful assistant."),
    ChatMessage(role="user", content="What is machine learning?")
]

response = client.generate_chat(
    messages=messages,
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=150
)

print("Response:", response.content)
print("Tokens:", response.usage.total_tokens)
print("Cost:", response.usage.cost)
print("Latency (s):", response.metrics.latency)
```

## Provider API Keys

You can configure provider API keys in several ways:

### 1. Environment Variables

```python
import os

# Set environment variables
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
os.environ["ANTHROPIC_API_KEY"] = "your_anthropic_api_key"
os.environ["MISTRAL_API_KEY"] = "your_mistral_api_key"

# Initialize client
client = Client(api_key="your_indox_router_api_key")
```

### 2. Configuration File

Create a configuration file at `~/.indoxRouter/config.json`:

```json
{
  "provider_keys": {
    "openai": "your_openai_api_key",
    "anthropic": "your_anthropic_api_key",
    "mistral": "your_mistral_api_key"
  }
}
```

Then initialize the client:

```python
client = Client(api_key="your_indox_router_api_key")
```

### 3. Direct API Key Usage

```python
response = client.generate_chat(
    messages=[ChatMessage(role="user", content="Hello!")],
    provider="openai",
    model="gpt-3.5-turbo",
    provider_api_key="your_openai_api_key"
)
```

## Working with Providers and Models

### List Available Providers

```python
providers = client.providers()
print("Available providers:", providers)
```

### List Models for a Provider

```python
openai_models = client.models("openai")
print("OpenAI models:", openai_models["openai"])
```

### Get Model Information

```python
model_info = client.model_info("openai", "gpt-3.5-turbo")
print(f"Model: {model_info.name}")
print(f"Type: {model_info.type}")
print(f"Context Window: {model_info.context_window}")
print(f"Input Price: ${model_info.input_price_per_1k_tokens}/1K tokens")
print(f"Output Price: ${model_info.output_price_per_1k_tokens}/1K tokens")
```

## Text Generation

```python
prompt = "Write a haiku about programming:"

response = client.generate_text(
    prompt=prompt,
    provider="openai",
    model="gpt-3.5-turbo-instruct",
    temperature=0.7,
    max_tokens=50
)

print("Response:", response.content)
print("Tokens:", response.usage.total_tokens)
print("Cost:", response.usage.cost)
print("Latency (s):", response.metrics.latency)
```

## Chat Generation

### Simple Chat

```python
messages = [
    ChatMessage(role="system", content="You are a helpful assistant."),
    ChatMessage(role="user", content="What is machine learning?")
]

response = client.generate_chat(
    messages=messages,
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=150
)

print("Response:", response.content)
print("Metrics:", {
    "tokens_prompt": response.metrics.tokens_prompt,
    "tokens_completion": response.metrics.tokens_completion,
    "tokens_total": response.usage.total_tokens,
    "cost": response.usage.cost,
    "latency": response.metrics.latency
})
```

### Multi-turn Conversation

```python
conversation = [
    ChatMessage(role="system", content="You are a math tutor."),
    ChatMessage(role="user", content="Can you explain what a derivative is?"),
    ChatMessage(role="assistant", content="A derivative measures the rate of change of a function at a specific point. It tells you how fast a function is increasing or decreasing."),
    ChatMessage(role="user", content="Can you give me an example?")
]

response = client.generate_chat(
    messages=conversation,
    provider="openai",
    model="gpt-4",
    temperature=0.5
)

print("Response:", response.content)
print("Raw provider response:", response.raw_response)  # Access the original provider response
```

## Embedding Generation

### Single Text Embedding

```python
text = "This is a sample text for embedding."

response = client.generate_embeddings(
    text=text,
    provider="openai",
    model="text-embedding-ada-002"
)

print(f"Embedding dimensions: {len(response.embeddings[0])}")
print(f"First 5 values: {response.embeddings[0][:5]}")
print(f"Tokens:", response.usage.total_tokens)
```

### Batch Embeddings

```python
texts = [
    "The quick brown fox",
    "jumps over the lazy dog",
    "A common pangram in English"
]

response = client.generate_embeddings(
    text=texts,
    provider="openai",
    model="text-embedding-ada-002"
)

print(f"Number of embeddings: {len(response.embeddings)}")
print(f"Dimensions per embedding: {len(response.embeddings[0])}")
print(f"Latency (s): {response.metrics.latency}")
```

## Image Generation

```python
prompt = "A serene lake surrounded by mountains at sunset"

response = client.generate_image(
    prompt=prompt,
    provider="openai",
    model="dall-e-2",
    size="512x512",
    n=1
)

print(f"Generated image URL: {response.images[0]}")
print(f"Image size: {response.sizes[0]}")
print(f"Cost:", response.usage.cost)
```

## Error Handling

```python
from indoxRouter.exceptions import (
    ProviderNotFoundError,
    ModelNotFoundError,
    InvalidParametersError
)

try:
    response = client.generate_chat(
        messages=[ChatMessage(role="user", content="Hello!")],
        provider="nonexistent_provider",
        model="nonexistent_model"
    )
except ProviderNotFoundError as e:
    print(f"Provider error: {e}")
except ModelNotFoundError as e:
    print(f"Model error: {e}")
except InvalidParametersError as e:
    print(f"Parameter error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Smart Model Selection

```python
def get_best_model(client, provider: str, max_cost_per_1k: float = 0.01):
    """Find the best model within a cost constraint."""
    models = client.models(provider)
    best_model = None
    best_score = float('inf')

    for model_data in models.get(provider, []):
        model_info = client.model_info(provider, model_data['modelName'])
        if model_info.input_price_per_1k_tokens <= max_cost_per_1k:
            score = model_info.input_price_per_1k_tokens
            if score < best_score:
                best_score = score
                best_model = model_info

    return best_model

# Use the function
best_model = get_best_model(client, "openai")
if best_model:
    print(f"Best model: {best_model.name}")
    print(f"Price per 1K tokens: ${best_model.input_price_per_1k_tokens}")
```

### Batch Processing with Rate Limiting

```python
import time
from typing import List

def process_batch_with_rate_limit(
    client,
    texts: List[str],
    provider: str,
    model: str,
    batch_size: int = 10,
    delay_seconds: float = 1.0
):
    """Process a large batch of texts with rate limiting."""
    results = []
    total_tokens = 0
    total_cost = 0
    total_latency = 0

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        try:
            response = client.generate_embeddings(
                text=batch,
                provider=provider,
                model=model
            )
            results.extend(response.embeddings)

            # Track metrics
            total_tokens += response.usage.total_tokens
            total_cost += response.usage.cost
            total_latency += response.metrics.latency

            # Rate limiting delay
            if i + batch_size < len(texts):
                time.sleep(delay_seconds)

        except Exception as e:
            print(f"Error processing batch {i//batch_size}: {e}")

    print(f"Processed {len(results)} embeddings")
    print(f"Total tokens: {total_tokens}")
    print(f"Total cost: ${total_cost:.6f}")
    print(f"Average latency: {total_latency/len(results):.2f} s")

    return results

# Example usage
texts = ["Text " + str(i) for i in range(100)]
embeddings = process_batch_with_rate_limit(
    client,
    texts,
    provider="openai",
    model="text-embedding-ada-002"
)
```

## License

MIT
