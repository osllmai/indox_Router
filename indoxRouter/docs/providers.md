# Provider Configuration

This document describes how to configure and use the different LLM providers supported by IndoxRouter.

## Supported Providers

IndoxRouter supports the following providers:

1. **OpenAI** - GPT-3.5, GPT-4, GPT-4o
2. **Anthropic** - Claude 3 (Opus, Sonnet, Haiku)
3. **Google** - Gemini 1.0 and 1.5 models
4. **Meta** - Llama 2 and Llama 3 models
5. **Mistral** - Mistral 7B, 8x7B, Medium, Large
6. **Cohere** - Command, Command R, Command R+
7. **AI21 Labs** - Jurassic-2, Jamba
8. **Llama** - Llama 3 (8B, 70B, 405B) models
9. **NVIDIA** - TensorRT-LLM Mixtral, Nemotron, NeMo Sirius
10. **Deepseek** - LLM, Coder, Math, Vision models
11. **Databricks** - DBRX, Mosaic models

## Provider API Keys

To use a provider, you need to set the corresponding API key. You can set API keys in two ways:

### 1. Environment Variables

Set the API keys as environment variables:

```bash
export OPENAI_API_KEY=sk-your-openai-api-key
export ANTHROPIC_API_KEY=sk-your-anthropic-api-key
export MISTRAL_API_KEY=your-mistral-api-key
export COHERE_API_KEY=your-cohere-api-key
export GOOGLE_API_KEY=your-google-api-key
export META_API_KEY=your-meta-api-key
export AI21_API_KEY=your-ai21-api-key
export LLAMA_API_KEY=your-llama-api-key
export NVIDIA_API_KEY=your-nvidia-api-key
export DEEPSEEK_API_KEY=your-deepseek-api-key
export DATABRICKS_API_KEY=your-databricks-api-key
```

### 2. Configuration File

Alternatively, you can set the API keys in the configuration file:

```json
{
  "providers": {
    "openai": {
      "api_key": "sk-your-openai-api-key"
    },
    "anthropic": {
      "api_key": "sk-your-anthropic-api-key"
    },
    "mistral": {
      "api_key": "your-mistral-api-key"
    },
    "cohere": {
      "api_key": "your-cohere-api-key"
    },
    "google": {
      "api_key": "your-google-api-key"
    },
    "meta": {
      "api_key": "your-meta-api-key"
    },
    "ai21": {
      "api_key": "your-ai21-api-key"
    },
    "llama": {
      "api_key": "your-llama-api-key"
    },
    "nvidia": {
      "api_key": "your-nvidia-api-key"
    },
    "deepseek": {
      "api_key": "your-deepseek-api-key"
    },
    "databricks": {
      "api_key": "your-databricks-api-key"
    }
  }
}
```

## Provider-Specific Configuration

Each provider can be further configured with provider-specific settings:

### OpenAI

```json
{
  "providers": {
    "openai": {
      "api_key": "sk-your-openai-api-key",
      "api_base": "https://api.openai.com/v1",
      "default_model": "gpt-4o",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Anthropic

```json
{
  "providers": {
    "anthropic": {
      "api_key": "sk-your-anthropic-api-key",
      "api_base": "https://api.anthropic.com/v1",
      "default_model": "claude-3-opus-20240229",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Google

```json
{
  "providers": {
    "google": {
      "api_key": "your-google-api-key",
      "api_base": "https://generativelanguage.googleapis.com/v1",
      "default_model": "gemini-1.5-pro",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Meta

```json
{
  "providers": {
    "meta": {
      "api_key": "your-meta-api-key",
      "api_base": "https://api.meta.ai/v1",
      "default_model": "llama-3-70b-instruct",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Mistral

```json
{
  "providers": {
    "mistral": {
      "api_key": "your-mistral-api-key",
      "api_base": "https://api.mistral.ai/v1",
      "default_model": "mistral-large-latest",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Cohere

```json
{
  "providers": {
    "cohere": {
      "api_key": "your-cohere-api-key",
      "api_base": "https://api.cohere.ai/v1",
      "default_model": "command-r-plus",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### AI21 Labs

```json
{
  "providers": {
    "ai21": {
      "api_key": "your-ai21-api-key",
      "api_base": "https://api.ai21.com/studio/v1",
      "default_model": "jamba-instruct",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Llama

```json
{
  "providers": {
    "llama": {
      "api_key": "your-llama-api-key",
      "api_base": "https://llama-api.meta.ai/v1",
      "default_model": "meta-llama-3-70b-instruct",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### NVIDIA

```json
{
  "providers": {
    "nvidia": {
      "api_key": "your-nvidia-api-key",
      "api_base": "https://api.nvidia.com/v1",
      "default_model": "nvidia-tensorrt-llm-mixtral-8x7b-instruct",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Deepseek

```json
{
  "providers": {
    "deepseek": {
      "api_key": "your-deepseek-api-key",
      "api_base": "https://api.deepseek.com/v1",
      "default_model": "deepseek-llm-67b-chat",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Databricks

```json
{
  "providers": {
    "databricks": {
      "api_key": "your-databricks-api-key",
      "api_base": "https://api.databricks.com/v1",
      "default_model": "databricks-dbrx-instruct",
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

## Model Configuration

Each provider has a set of supported models with specific configurations. These configurations are stored in JSON files in the `providers` directory.

For example, the OpenAI models are defined in `providers/openai.json`:

```json
[
  {
    "modelName": "gpt-4o",
    "displayName": "GPT-4o",
    "description": "GPT-4o is OpenAI's most advanced model",
    "inputPricePer1KTokens": 0.01,
    "outputPricePer1KTokens": 0.03,
    "contextLength": 128000,
    "systemPrompt": "You are a helpful assistant."
  },
  {
    "modelName": "gpt-4-turbo",
    "displayName": "GPT-4 Turbo",
    "description": "GPT-4 Turbo with improved capabilities",
    "inputPricePer1KTokens": 0.01,
    "outputPricePer1KTokens": 0.03,
    "contextLength": 128000,
    "systemPrompt": "You are a helpful assistant."
  }
]
```

## Using Providers in Code

### Client API

```python
from indoxRouter.client import Client

# Initialize the client with your API key
client = Client(api_key="your_api_key")

# Generate a completion using OpenAI
response_openai = client.generate(
    provider="openai",
    model="gpt-4o",
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)

# Generate a completion using Anthropic
response_anthropic = client.generate(
    provider="anthropic",
    model="claude-3-opus-20240229",
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)

# Generate a completion using Google
response_google = client.generate(
    provider="google",
    model="gemini-1.5-pro",
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)

# Generate a completion using NVIDIA
response_nvidia = client.generate(
    provider="nvidia",
    model="nvidia-tensorrt-llm-mixtral-8x7b-instruct",
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)

# Generate a completion using Deepseek
response_deepseek = client.generate(
    provider="deepseek",
    model="deepseek-llm-67b-chat",
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)

# Generate a completion using Llama
response_llama = client.generate(
    provider="llama",
    model="meta-llama-3-70b-instruct",
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)

# Generate a completion using Databricks
response_databricks = client.generate(
    provider="databricks",
    model="databricks-dbrx-instruct",
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)
```

### Direct Provider API

You can also use the provider classes directly:

```python
from indoxRouter.providers.openai import Provider as OpenAIProvider
from indoxRouter.providers.anthropic import Provider as AnthropicProvider
from indoxRouter.providers.google import Provider as GoogleProvider

# Initialize the OpenAI provider
openai_provider = OpenAIProvider(
    api_key="your_openai_api_key",
    model_name="gpt-4o"
)

# Generate a completion
response = openai_provider.generate(
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)

print(response["text"])
print(f"Cost: ${response['cost']}")
```

## Adding a New Provider

To add a new provider to IndoxRouter, you need to:

1. Create a JSON configuration file in the `providers` directory (e.g., `providers/new_provider.json`)
2. Implement the provider class in a Python file (e.g., `providers/new_provider.py`)
3. Update the client to support the new provider

The provider class should inherit from `BaseProvider` and implement the required methods:

```python
from .base_provider import BaseProvider

class Provider(BaseProvider):
    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        # Provider-specific initialization

    def _load_model_config(self, model_name: str):
        # Load model configuration from JSON file

    def estimate_cost(self, prompt: str, max_tokens: int) -> float:
        # Estimate the cost of generating a completion

    def count_tokens(self, text: str) -> int:
        # Count the number of tokens in a text

    def generate(self, prompt: str, **kwargs) -> dict:
        # Generate a completion for the given prompt
```

## Troubleshooting

### API Key Issues

If you encounter issues with API keys, check:

1. The API key is correctly set in the environment or configuration file
2. The API key is valid and has not expired
3. The API key has the necessary permissions

### Rate Limiting

If you encounter rate limiting issues:

1. Check the provider's rate limits
2. Implement exponential backoff and retry logic
3. Consider using multiple API keys or providers

### Model Not Found

If you encounter "Model not found" errors:

1. Check that the model name is correct
2. Verify that the model is supported by the provider
3. Check that the model configuration file exists and is correctly formatted
