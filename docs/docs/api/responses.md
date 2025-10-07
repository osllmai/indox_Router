# Response Schemas

This page documents the response formats for all IndoxRouter API endpoints.

## Chat Completion Response

```python
{
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-10-07T10:30:00.000Z",
    "duration_ms": 1250.5,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "success": true,
    "message": "",
    "data": "Hello! How can I help you today?",
    "finish_reason": "stop",
    "usage": {
        "tokens_prompt": 12,
        "tokens_completion": 8,
        "tokens_total": 20,
        "cost": 0.0006,
        "latency": 1.25,
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
    },
    "raw_response": {...},
    "byok_api_key": false
}
```

## Text Completion Response

```python
{
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "created_at": "2024-10-07T10:30:00.000Z",
    "duration_ms": 890.2,
    "provider": "openai",
    "model": "gpt-3.5-turbo-instruct",
    "success": true,
    "message": "",
    "data": "This is a sample completion text.",
    "finish_reason": "stop",
    "usage": {
        "tokens_prompt": 5,
        "tokens_completion": 7,
        "tokens_total": 12,
        "cost": 0.00018,
        "latency": 0.89,
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
    },
    "raw_response": {...},
    "byok_api_key": false
}
```

## Embedding Response

```python
{
    "request_id": "550e8400-e29b-41d4-a716-446655440002",
    "created_at": "2024-10-07T10:30:00.000Z",
    "duration_ms": 450.8,
    "provider": "openai",
    "model": "text-embedding-ada-002",
    "success": true,
    "message": "",
    "data": [
        [0.0023064255, -0.009327292, ...],
        [0.001234567, 0.008765432, ...]
    ],
    "dimensions": 1536,
    "usage": {
        "tokens_prompt": 8,
        "tokens_completion": 0,
        "tokens_total": 8,
        "cost": 0.0000032,
        "latency": 0.45,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "web_search_count": 0,
        "request_count": 1,
        "cost_breakdown": {
            "prompt_cost": 0.0000032,
            "completion_cost": 0.0,
            "cache_read_cost": 0.0,
            "cache_write_cost": 0.0,
            "reasoning_cost": 0.0,
            "web_search_cost": 0.0,
            "total_cost": 0.0000032
        }
    },
    "raw_response": {...},
    "byok_api_key": false
}
```

## Image Generation Response

### URL-based Models (DALL-E 2, DALL-E 3)

```python
{
    "request_id": "550e8400-e29b-41d4-a716-446655440003",
    "created_at": "2024-10-07T10:30:00.000Z",
    "duration_ms": 3250.1,
    "provider": "openai",
    "model": "dall-e-3",
    "success": true,
    "message": "",
    "data": [
        {
            "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/...",
            "revised_prompt": "A beautiful sunset over mountains..."
        }
    ],
    "usage": {
        "tokens_prompt": 0,
        "tokens_completion": 0,
        "tokens_total": 0,
        "cost": 0.04,
        "latency": 3.25,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "web_search_count": 0,
        "request_count": 1,
        "cost_breakdown": {
            "prompt_cost": 0.0,
            "completion_cost": 0.0,
            "cache_read_cost": 0.0,
            "cache_write_cost": 0.0,
            "reasoning_cost": 0.0,
            "web_search_cost": 0.0,
            "total_cost": 0.04
        }
    },
    "raw_response": {...},
    "byok_api_key": false
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
    "total_cost": 12.50,
    "remaining_credits": 87.50,
    "total_tokens": {
        "input": 22500,
        "output": 22500,
        "total": 45000
    },
    "endpoints": {
        "chat": {
            "requests": 1000,
            "cost": 10.00,
            "tokens": {
                "input": 18000,
                "output": 18000,
                "total": 36000
            }
        },
        "embeddings": {
            "requests": 200,
            "cost": 2.00,
            "tokens": {
                "input": 4500,
                "output": 0,
                "total": 4500
            }
        },
        "images": {
            "requests": 50,
            "cost": 0.50,
            "tokens": {
                "input": 0,
                "output": 0,
                "total": 0
            }
        }
    },
    "providers": {
        "openai": {
            "requests": 800,
            "cost": 8.40,
            "tokens": {
                "input": 14000,
                "output": 14000,
                "total": 28000
            }
        },
        "anthropic": {
            "requests": 300,
            "cost": 2.88,
            "tokens": {
                "input": 6000,
                "output": 6000,
                "total": 12000
            }
        }
    },
    "models": {
        "gpt-4": {
            "requests": 400,
            "cost": 4.50,
            "tokens": {
                "input": 7500,
                "output": 7500,
                "total": 15000
            }
        },
        "claude-3-sonnet": {
            "requests": 300,
            "cost": 2.88,
            "tokens": {
                "input": 6000,
                "output": 6000,
                "total": 12000
            }
        }
    },
    "daily_usage": [
        {
            "date": "2024-10-01",
            "requests": 45,
            "cost": 1.25,
            "tokens": {
                "input": 1125,
                "output": 1125,
                "total": 2250
            }
        },
        {
            "date": "2024-10-02",
            "requests": 38,
            "cost": 0.95,
            "tokens": {
                "input": 950,
                "output": 950,
                "total": 1900
            }
        }
    ]
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

- **`tokens_prompt`** (integer): Number of tokens in the prompt/input
- **`tokens_completion`** (integer): Number of tokens in the completion/output
- **`tokens_total`** (integer): Total tokens used (prompt + completion)
- **`cost`** (float): Total cost for the request
- **`latency`** (float): Request latency in seconds
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
