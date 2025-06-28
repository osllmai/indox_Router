# Basic Usage

This page covers the fundamental patterns and concepts for using IndoxRouter effectively.

## Client Initialization

```python
from indoxrouter import Client

# Initialize with API key
client = Client(api_key="your_api_key")
```

## Model Specification

IndoxRouter uses a consistent format for specifying models: `provider/model_name`. This allows you to easily switch between providers while keeping your code structure the same.

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

Responses from the API closely follow the OpenAI API response format, with some additions for consistency across providers:

```python
{'request_id': 'b881942c-e21d-4f9d-ad82-47344945c642',
 'created_at': '2025-06-15T09:53:26.130868',
 'duration_ms': 1737.612247467041,
 'provider': 'openai',
 'model': 'gpt-4o-mini',
 'success': True,
 'message': '',
 'usage': {'tokens_prompt': 24,
  'tokens_completion': 7,
  'tokens_total': 31,
  'cost': 7.8e-06,
  'latency': 1.629077672958374,
  'timestamp': '2025-06-15T09:53:26.114626',
  'cache_read_tokens': 0,
  'cache_write_tokens': 0,
  'reasoning_tokens': 0,
  'web_search_count': 0,
  'request_count': 1,
  'cost_breakdown': {'input_tokens': 3.6e-06,
   'output_tokens': 4.2e-06,
   'cache_read': 0.0,
   'cache_write': 0.0,
   'reasoning': 0.0,
   'web_search': 0.0,
   'request': 0.0}},
 'raw_response': None,
 'data': 'The capital of France is Paris.',
 'finish_reason': None}
```

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

## Debugging

If you're experiencing issues, you can enable debug logging:

```python
import logging
from indoxrouter import Client

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
- [Model Information](models.md)
