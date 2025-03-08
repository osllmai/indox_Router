# Configuration

This guide covers how to configure indoxRouter for your needs.

## API Key Configuration

### Setting Your indoxRouter API Key

The most important configuration is your indoxRouter API key, which you can set in several ways:

1. **Directly in the client initialization**:

```python
from indoxRouter import Client

client = Client(api_key="your-indoxrouter-api-key")
```

2. **Using an environment variable**:

```python
import os
os.environ["INDOX_ROUTER_API_KEY"] = "your-indoxrouter-api-key"

from indoxRouter import Client
client = Client()  # Will use the environment variable
```

## Client Configuration

When initializing the client, you can customize several parameters:

```python
client = Client(
    api_key="your-indoxrouter-api-key",
    base_url="https://api.indoxrouter.com/v1",  # Custom API endpoint
    timeout=30,  # Longer timeout (in seconds)
    auto_refresh=True  # Automatically refresh authentication tokens
)
```

### Parameters

| Parameter      | Type   | Default                            | Description                                            |
| -------------- | ------ | ---------------------------------- | ------------------------------------------------------ |
| `api_key`      | `str`  | `None`                             | Your indoxRouter API key                               |
| `base_url`     | `str`  | `"https://api.indoxrouter.com/v1"` | The base URL for the API                               |
| `timeout`      | `int`  | `15`                               | Request timeout in seconds                             |
| `auto_refresh` | `bool` | `True`                             | Whether to automatically refresh authentication tokens |

## Configuration File

indoxRouter also supports loading configuration from a file. The default location is `~/.indoxRouter/config.json`.

Example configuration file:

```json
{
  "provider_keys": {
    "openai": "sk-...",
    "anthropic": "sk-...",
    "mistral": "...",
    "cohere": "...",
    "google": "..."
  }
}
```

### Loading Configuration

The configuration is automatically loaded when you create a client. You can also access it directly:

```python
from indoxRouter.config import get_config

config = get_config()
openai_key = config.get_provider_key("openai")
```

### Setting Configuration

You can also set configuration values programmatically:

```python
from indoxRouter.config import get_config

config = get_config()
config.set_provider_key("openai", "sk-...")
config.save_config()
```

## Environment Variables

indoxRouter also supports configuration through environment variables:

| Environment Variable   | Description              |
| ---------------------- | ------------------------ |
| `INDOX_ROUTER_API_KEY` | Your indoxRouter API key |
| `OPENAI_API_KEY`       | Your OpenAI API key      |
| `ANTHROPIC_API_KEY`    | Your Anthropic API key   |
| `MISTRAL_API_KEY`      | Your Mistral API key     |
| `COHERE_API_KEY`       | Your Cohere API key      |
| `GOOGLE_API_KEY`       | Your Google API key      |

## Next Steps

Now that you've configured indoxRouter, you can:

- [Try the quick start guide](quickstart.md)
- [Learn about chat completions](chat.md)
- [Explore streaming responses](streaming.md)
