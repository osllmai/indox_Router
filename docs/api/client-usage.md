# IndoxRouter Client Usage Guide

This guide provides examples of how to use the IndoxRouter client with the new resources module and credit system.

## Installation

```bash
pip install indoxrouter
```

## Initialization

```python
from indoxrouter import Client

# Initialize with API key
client = Client(api_key="your_api_key")

# Or use environment variable
# export INDOX_ROUTER_API_KEY=your_api_key
client = Client()

# You can also set a custom timeout
client = Client(api_key="your_api_key", timeout=30)  # 30 seconds timeout
```

## Chat Completions

Generate chat completions using various AI models:

```python
# Basic usage
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="openai/gpt-4o-mini"
)

print(response["data"])  # The assistant's response
print(response["usage"]["cost"])  # The cost of the request

# With additional parameters
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short poem about AI."}
    ],
    model="anthropic/claude-3-haiku",
    temperature=0.8,
    max_tokens=500
)

# Streaming response
for chunk in client.chat(
    messages=[
        {"role": "user", "content": "Tell me a story about a robot."}
    ],
    model="openai/gpt-4o-mini",
    stream=True
):
    print(chunk, end="", flush=True)
```

## Text Completions

Generate text completions:

```python
# Basic usage
response = client.completion(
    prompt="Once upon a time",
    model="openai/gpt-4o-mini"
)

print(response["data"])  # The completion
print(response["usage"]["cost"])  # The cost of the request

# With additional parameters
response = client.completion(
    prompt="Write a recipe for chocolate cake",
    model="anthropic/claude-3-haiku",
    temperature=0.7,
    max_tokens=1000
)

# Streaming response
for chunk in client.completion(
    prompt="Explain quantum computing in simple terms",
    model="openai/gpt-4o-mini",
    stream=True
):
    print(chunk, end="", flush=True)
```

## Embeddings

Generate embeddings for text:

```python
# Single text
response = client.embeddings(
    text="Hello, world!",
    model="openai/text-embedding-ada-002"
)

print(len(response["data"][0]))  # Number of dimensions
print(response["usage"]["cost"])  # The cost of the request

# Multiple texts
response = client.embeddings(
    text=["Hello, world!", "How are you?"],
    model="cohere/embed-english-v3.0"
)

# Access embeddings
for embedding in response["data"]:
    print(len(embedding))  # Number of dimensions
```

## Image Generation

Generate images from text prompts:

```python
# Basic usage
response = client.images(
    prompt="A beautiful sunset over the ocean",
    model="openai/dall-e-3"
)

print(response["data"][0]["url"])  # URL of the generated image
print(response["usage"]["cost"])  # The cost of the request

# With additional parameters
response = client.images(
    prompt="A futuristic city with flying cars",
    model="openai/dall-e-3",
    size="1024x1024",
    n=2,
    quality="hd",
    style="vivid"
)

# Access image URLs
for image in response["data"]:
    print(image["url"])
```

## Model Information

Get information about available models:

```python
# Get all models
models = client.models()

# Get models for a specific provider
openai_models = client.models("openai")

# Get information about a specific model
model_info = client.get_model_info("openai", "gpt-4o-mini")
print(model_info["inputPricePer1KTokens"])  # Input price per 1K tokens
print(model_info["outputPricePer1KTokens"])  # Output price per 1K tokens
```

## Usage Statistics

Get usage statistics for the current user:

```python
usage = client.get_usage()
print(usage["total_requests"])  # Total number of requests
print(usage["total_cost"])  # Total cost
print(usage["remaining_credits"])  # Remaining credits
```

## Error Handling

Handle errors gracefully:

```python
from indoxrouter import (
    AuthenticationError,
    NetworkError,
    ProviderNotFoundError,
    ModelNotFoundError,
    InvalidParametersError,
    RateLimitError,
    ProviderError,
    InsufficientCreditsError
)

try:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="nonexistent/model"
    )
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except ProviderNotFoundError as e:
    print(f"Provider not found: {e}")
except InsufficientCreditsError as e:
    print(f"Insufficient credits: {e}")
except InvalidParametersError as e:
    print(f"Invalid parameters: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except ProviderError as e:
    print(f"Provider error: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except AuthenticationError as e:
    print(f"Authentication error: {e}")
```

## Using as a Context Manager

Use the client as a context manager to automatically close the session:

```python
with Client(api_key="your_api_key") as client:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="openai/gpt-4o-mini"
    )
    print(response["data"])
```

## Best Practices

1. **Specify the model explicitly**: Always specify the model you want to use in the format `provider/model` to ensure consistent behavior.

2. **Handle errors gracefully**: Catch specific exceptions to handle different error scenarios.

3. **Monitor credit usage**: Keep track of your credit usage to avoid unexpected charges.

4. **Use streaming for long responses**: Use streaming for long responses to improve user experience.

5. **Close the client when done**: Use the client as a context manager or call `client.close()` when you're done to free up resources.

6. **Set appropriate timeouts**: Set appropriate timeouts to avoid hanging requests.

7. **Use environment variables for API keys**: Use environment variables for API keys to avoid hardcoding them in your code.
