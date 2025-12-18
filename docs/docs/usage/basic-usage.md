# Basic Usage

This page covers the fundamental patterns and concepts for using indoxhub effectively.

## Client Initialization

```python
from indoxhub import Client

# Initialize with API key
client = Client(api_key="your_api_key")
```

## Model Specification

indoxhub uses a consistent format for specifying models: `provider/model_name`. This allows you to easily switch between providers while keeping your code structure the same.

Examples:

- `openai/gpt-4o-mini`
- `anthropic/claude-3-sonnet-20240229`
- `mistral/mistral-large-latest`
- `google/gemini-1.5-pro`

## Common Parameters

All API methods accept a set of common parameters:

- `model`: The model to use in format `provider/model_name`
- `temperature`: Controls randomness (0-1). Lower values = more deterministic. Default is 0.7
- `max_tokens`: Maximum number of tokens to generate

Additional parameters specific to each provider can be passed as keyword arguments.

## Response Structure

!!! note "Response Format Differences"
**Chat and Completions endpoints** use an OpenAI-compatible format with an `output` array. All other endpoints (embeddings, images, audio, etc.) use a standard format with a `data` field.

Chat and completion responses follow an OpenAI-compatible format:

```python
{
    'id': 'b881942c-e21d-4f9d-ad82-47344945c642',
    'object': 'response',
    'created_at': 1718456006,
    'model': 'gpt-4o-mini',
    'provider': 'openai',
    'duration_ms': 1737.61,
    'output': [
        {
            'type': 'message',
            'status': 'completed',
            'role': 'assistant',
            'content': [
                {
                    'type': 'output_text',
                    'text': 'The capital of France is Paris.',
                    'annotations': []
                }
            ]
        }
    ],
    'usage': {
        'input_tokens': 24,
        'input_tokens_details': {'cached_tokens': 0},
        'output_tokens': 7,
        'output_tokens_details': {'reasoning_tokens': 0},
        'total_tokens': 31
    },
    'status': 'completed'
}
```

To access the response text: `response['output'][0]['content'][0]['text']`

## Error Handling

The client provides a set of specific exception classes for different error types:

- `AuthenticationError`: Issues with API key or authentication
- `ProviderNotFoundError`: The requested provider doesn't exist
- `ModelNotFoundError`: The requested model doesn't exist
- `InvalidParametersError`: The provided parameters are invalid
- `RateLimitError`: The rate limit has been exceeded
- `ProviderError`: An error occurred with the provider's service
- `InsufficientCreditsError`: Not enough credits to complete the request
- `NetworkError`: Network connectivity issues

Example error handling:

```python
from indoxhub import Client, ModelNotFoundError, ProviderError

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

## Debugging

If you're experiencing issues, you can enable debug logging:

```python
import logging
from indoxhub import Client

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

client = Client(api_key="your_api_key")
client.enable_debug()  # This enables additional debugging information

# Your code here
```

You can also use the `diagnose_request` method to get detailed information about a request without actually sending it:

```python
diagnostic_info = client.diagnose_request(
    "chat/completions",
    {
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "openai/gpt-4o-mini"
    }
)
print(diagnostic_info)
```

## Next Steps

Now that you understand the basics, check out the detailed guides for each capability:

- [Chat Completions](chat.md)
- [Text Completions](completions.md)
- [Embeddings](embeddings.md)
- [Image Generation](images.md)
- [Video Generation](video.md)

_Last updated: Nov 16, 2025_
