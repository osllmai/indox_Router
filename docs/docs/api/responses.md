# Response Schemas

This page documents the response formats for all IndoxRouter API endpoints.

## Chat Completion Response

```python
{
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4",
    "provider": "openai",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you today?"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 12,
        "completion_tokens": 8,
        "total_tokens": 20,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "web_search_count": 0,
        "request_count": 1,
        "cost_breakdown": {
            "prompt_cost": 0.00036,
            "completion_cost": 0.00024,
            "cache_read_cost": 0.0,
            "cache_write_cost": 0.0,
            "reasoning_cost": 0.0,
            "web_search_cost": 0.0,
            "total_cost": 0.0006
        }
    }
}
```

## Text Completion Response

```python
{
    "id": "cmpl-123",
    "object": "text_completion",
    "created": 1677652288,
    "model": "gpt-3.5-turbo-instruct",
    "provider": "openai",
    "choices": [
        {
            "text": "This is a sample completion text.",
            "index": 0,
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 5,
        "completion_tokens": 7,
        "total_tokens": 12,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "web_search_count": 0,
        "request_count": 1,
        "cost_breakdown": {
            "prompt_cost": 0.000075,
            "completion_cost": 0.000105,
            "cache_read_cost": 0.0,
            "cache_write_cost": 0.0,
            "reasoning_cost": 0.0,
            "web_search_cost": 0.0,
            "total_cost": 0.00018
        }
    }
}
```

## Embedding Response

```python
{
    "object": "list",
    "data": [
        {
            "object": "embedding",
            "embedding": [0.0023064255, -0.009327292, ...],
            "index": 0
        }
    ],
    "model": "text-embedding-ada-002",
    "provider": "openai",
    "usage": {
        "prompt_tokens": 8,
        "total_tokens": 8,
        "request_count": 1,
        "cost_breakdown": {
            "total_cost": 0.0000032
        }
    }
}
```

## Image Generation Response

### URL-based Models (DALL-E 2, DALL-E 3)

```python
{
    "created": 1677652288,
    "data": [
        {
            "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/..."
        }
    ],
    "provider": "openai",
    "model": "dall-e-3",
    "usage": {
        "request_count": 1,
        "cost_breakdown": {
            "total_cost": 0.04
        }
    }
}
```

### Base64-based Models (GPT-Image-1)

```python
{
    "created": 1677652288,
    "data": [
        {
            "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        }
    ],
    "provider": "openai",
    "model": "gpt-image-1",
    "usage": {
        "request_count": 1,
        "cost_breakdown": {
            "total_cost": 0.02
        }
    }
}
```

## Model Information Response

```python
{
    "models": [
        {
            "id": "gpt-4",
            "object": "model",
            "created": 1677610602,
            "owned_by": "openai",
            "provider": "openai",
            "capabilities": ["chat", "completion"],
            "context_length": 8192,
            "pricing": {
                "prompt": 0.03,
                "completion": 0.06,
                "unit": "1K tokens"
            }
        }
    ]
}
```

## Usage Statistics Response

```python
{
    "total_requests": 1250,
    "total_tokens": 45000,
    "total_cost": 12.50,
    "current_period": {
        "requests": 150,
        "tokens": 5500,
        "cost": 1.75,
        "period_start": "2024-01-01T00:00:00Z",
        "period_end": "2024-01-31T23:59:59Z"
    },
    "by_provider": {
        "openai": {
            "requests": 800,
            "tokens": 28000,
            "cost": 8.40
        },
        "anthropic": {
            "requests": 300,
            "tokens": 12000,
            "cost": 2.88
        }
    },
    "by_model": {
        "gpt-4": {
            "requests": 400,
            "tokens": 15000,
            "cost": 4.50
        },
        "claude-3-sonnet": {
            "requests": 300,
            "tokens": 12000,
            "cost": 2.88
        }
    }
}
```

## Error Response

```python
{
    "error": {
        "message": "Invalid API key provided",
        "type": "invalid_request_error",
        "param": null,
        "code": "invalid_api_key"
    }
}
```

## Response Fields

### Usage Object

All API responses include a `usage` object with the following fields:

- **`prompt_tokens`** (integer): Number of tokens in the prompt
- **`completion_tokens`** (integer): Number of tokens in the completion
- **`total_tokens`** (integer): Total tokens used (prompt + completion)
- **`cache_read_tokens`** (integer): Tokens read from cache
- **`cache_write_tokens`** (integer): Tokens written to cache
- **`reasoning_tokens`** (integer): Tokens used for reasoning (reasoning models)
- **`web_search_count`** (integer): Number of web searches performed
- **`request_count`** (integer): Number of API requests made
- **`cost_breakdown`** (object): Detailed cost information

### Cost Breakdown Object

The `cost_breakdown` object provides detailed pricing:

- **`prompt_cost`** (float): Cost for prompt tokens
- **`completion_cost`** (float): Cost for completion tokens
- **`cache_read_cost`** (float): Cost for cache read operations
- **`cache_write_cost`** (float): Cost for cache write operations
- **`reasoning_cost`** (float): Cost for reasoning tokens
- **`web_search_cost`** (float): Cost for web search operations
- **`total_cost`** (float): Total cost for the request

### Finish Reasons

Possible values for `finish_reason`:

- **`stop`**: Natural stopping point or provided stop sequence
- **`length`**: Maximum token limit reached
- **`content_filter`**: Content filtered due to policy violations
- **`tool_calls`**: Model called a function/tool
- **`function_call`**: Model called a function (deprecated)

## HTTP Status Codes

- **200**: Success
- **400**: Bad Request - Invalid parameters
- **401**: Unauthorized - Invalid API key
- **403**: Forbidden - Insufficient permissions
- **429**: Too Many Requests - Rate limit exceeded
- **500**: Internal Server Error
- **502**: Bad Gateway - Provider error
- **503**: Service Unavailable - Temporary outage
