# Getting Started

This guide will help you get started with the IndoxRouter library, showing you how to install the package, set up your API key, and make your first API call.

## Installation

To install the IndoxRouter, use pip:

```bash
pip install indoxrouter
```

## Setting Up Your API Key

To use IndoxRouter, you need an API key from your IndoxRouter Server instance. There are several ways to configure your API key:

### Method 1: Directly in the Client constructor

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")
```

### Method 2: Using environment variables

You can set the `INDOX_ROUTER_API_KEY` environment variable and the client will use it automatically:

```python
# In your terminal or .env file
# export INDOX_ROUTER_API_KEY=your_api_key

# In your Python code
from indoxrouter import Client

client = Client()  # Will use the environment variable
```

### Method 3: Configuration file

Coming soon: Support for loading configuration from a file.

## Verifying Your API Key

You can verify that your API key is working correctly by using the test_connection method:

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")
try:
    result = client.test_connection()
    print("Connection successful!")
    print(f"Connected to server version: {result.get('version', 'unknown')}")
except Exception as e:
    print(f"Connection failed: {str(e)}")
```

## Making Your First API Call

Here's a simple example of making a chat completion request:

```python
from indoxrouter import Client

# Initialize the client
client = Client(api_key="your_api_key")

# Make a chat completion request
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you today?"}
    ],
    model="openai/gpt-4o-mini"
)

# Print the response
print(response["data"])
```

## Error Handling

IndoxRouter provides clear error handling. Here's an example of how to handle errors:

```python
from indoxrouter import Client, ModelNotFoundError, ProviderError, AuthenticationError

try:
    client = Client(api_key="your_api_key")
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="nonexistent-provider/nonexistent-model"
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except ProviderError as e:
    print(f"Provider error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

- Set appropriate timeouts for your use case
- Handle errors appropriately for your application
- Consider using environment variables for API keys rather than hardcoding them

## Next Steps

Now that you're set up, check out the Usage Guide for more detailed information on working with the different API capabilities:

- [Basic Usage](usage/basic-usage.md)
- [Chat Completions](usage/chat.md)
- [Text Completions](usage/completions.md)
- [Embeddings](usage/embeddings.md)
- [Image Generation](usage/images.md)
- [Video Generation](usage/video.md)

_Last updated: Nov 11, 2025_