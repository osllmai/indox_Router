# API Reference

IndoxRouter exposes a REST API that closely follows the OpenAI API format, with extensions to support multiple providers. All API endpoints are available under the `/api/v1` prefix.

## Authentication

All API requests require authentication using an API key in the HTTP Authorization header:

```
Authorization: Bearer your_api_key
```

## Common Response Format

All API responses follow a common format:

```json
{
  "request_id": "req_123456789",
  "created_at": "2025-04-12T15:30:45Z",
  "duration_ms": 850,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "success": true,
  "message": "",
  "usage": {
    "tokens_prompt": 25,
    "tokens_completion": 75,
    "tokens_total": 100,
    "cost": 0.005,
    "latency": 850
  },
  "data": "..." // Endpoint-specific response data
}
```

## Endpoints

### Chat Completions

Generate a chat completion.

**Endpoint**: `POST /api/v1/chat/completions`

**Request Body**:

```json
{
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "Tell me a joke about programming." }
  ],
  "model": "openai/gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 500,
  "stream": false,
  "additional_params": {}
}
```

**Response**:

```json
{
  "request_id": "req_123456789",
  "created_at": "2025-04-12T15:30:45Z",
  "duration_ms": 850,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "success": true,
  "message": "",
  "usage": {
    "tokens_prompt": 25,
    "tokens_completion": 75,
    "tokens_total": 100,
    "cost": 0.005,
    "latency": 850
  },
  "data": "Why do programmers prefer dark mode? Because light attracts bugs!"
}
```

### Text Completions

Generate a text completion.

**Endpoint**: `POST /api/v1/completions`

**Request Body**:

```json
{
  "prompt": "Complete this sentence: The best way to learn programming is",
  "model": "openai/gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 100,
  "stream": false
}
```

**Response**:

```json
{
  "request_id": "req_987654321",
  "created_at": "2025-04-12T15:35:12Z",
  "duration_ms": 450,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "success": true,
  "message": "",
  "usage": {
    "tokens_prompt": 12,
    "tokens_completion": 32,
    "tokens_total": 44,
    "cost": 0.0022,
    "latency": 450
  },
  "data": " to practice by building real projects that solve problems you care about."
}
```

### Embeddings

Generate embeddings for text.

**Endpoint**: `POST /api/v1/embeddings`

**Request Body**:

```json
{
  "text": "This is a sample text to generate embeddings for.",
  "model": "openai/text-embedding-3-small"
}
```

**Response**:

```json
{
  "request_id": "req_456789123",
  "created_at": "2025-04-12T15:40:22Z",
  "duration_ms": 150,
  "provider": "openai",
  "model": "text-embedding-3-small",
  "success": true,
  "message": "",
  "usage": {
    "tokens_prompt": 10,
    "tokens_completion": 0,
    "tokens_total": 10,
    "cost": 0.0001,
    "latency": 150
  },
  "data": [
    [0.0123, 0.0456, 0.0789, ...]  // Vector of 1536 dimensions
  ],
  "dimensions": 1536
}
```

### Image Generation

Generate images from a text prompt.

**Endpoint**: `POST /api/v1/images/generations`

**Request Body**:

```json
{
  "prompt": "A serene mountain landscape with a lake at sunset",
  "model": "openai/dall-e-3",
  "size": "1024x1024",
  "n": 1
}
```

**Response**:

```json
{
  "request_id": "req_321654987",
  "created_at": "2025-04-12T15:45:33Z",
  "duration_ms": 3500,
  "provider": "openai",
  "model": "dall-e-3",
  "success": true,
  "message": "",
  "usage": {
    "tokens_prompt": 0,
    "tokens_completion": 0,
    "tokens_total": 0,
    "cost": 0.04,
    "latency": 3500
  },
  "data": [
    {
      "url": "https://cdn.example.com/images/123456.png",
      "b64_json": null
    }
  ]
}
```

### Models

Get information about available models.

**Endpoint**: `GET /api/v1/models`

**Response**:

```json
[
  {
    "id": "openai",
    "name": "OpenAI",
    "capabilities": ["chat", "completion", "embedding", "vision"],
    "models": [
      {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "openai",
        "capabilities": ["chat", "completion"],
        "max_tokens": 128000,
        "pricing": {
          "input": 0.0001,
          "output": 0.0003
        }
      },
      {
        "id": "text-embedding-3-small",
        "name": "Text Embedding 3 Small",
        "provider": "openai",
        "capabilities": ["embedding"],
        "pricing": {
          "input": 0.00002,
          "output": 0.0
        }
      }
    ]
  },
  {
    "id": "mistral",
    "name": "Mistral",
    "capabilities": ["chat", "completion", "embedding"],
    "models": [
      {
        "id": "mistral-large-latest",
        "name": "Mistral Large",
        "provider": "mistral",
        "capabilities": ["chat", "completion"],
        "max_tokens": 32000,
        "pricing": {
          "input": 0.00008,
          "output": 0.00024
        }
      }
    ]
  }
]
```

### User Usage Statistics

Get usage statistics for the authenticated user.

**Endpoint**: `GET /api/v1/user/usage`

**Query Parameters**:

- `start_date`: Optional start date for filtering (YYYY-MM-DD)
- `end_date`: Optional end date for filtering (YYYY-MM-DD)

**Response**:

```json
{
  "total_requests": 157,
  "total_cost": 0.2114,
  "remaining_credits": 999.7886,
  "total_tokens": {
    "input": 5918,
    "output": 13069,
    "total": 18987
  },
  "endpoints": {
    "chat": {
      "requests": 125,
      "cost": 0.1857,
      "tokens": {
        "input": 4500,
        "output": 11000,
        "total": 15500
      }
    },
    "embedding": {
      "requests": 32,
      "cost": 0.0257,
      "tokens": {
        "input": 1418,
        "output": 2069,
        "total": 3487
      }
    }
  },
  "providers": {
    "openai": {
      "requests": 122,
      "cost": 0.1726,
      "tokens": {
        "input": 4200,
        "output": 10000,
        "total": 14200
      }
    },
    "mistral": {
      "requests": 35,
      "cost": 0.0388,
      "tokens": {
        "input": 1718,
        "output": 3069,
        "total": 4787
      }
    }
  },
  "models": {
    "openai/gpt-4o-mini": {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "requests": 85,
      "cost": 0.1428,
      "tokens": {
        "input": 3200,
        "output": 8000,
        "total": 11200
      }
    },
    "openai/text-embedding-3-small": {
      "provider": "openai",
      "model": "text-embedding-3-small",
      "requests": 37,
      "cost": 0.0298,
      "tokens": {
        "input": 1000,
        "output": 2000,
        "total": 3000
      }
    },
    "mistral/mistral-large-latest": {
      "provider": "mistral",
      "model": "mistral-large-latest",
      "requests": 35,
      "cost": 0.0388,
      "tokens": {
        "input": 1718,
        "output": 3069,
        "total": 4787
      }
    }
  },
  "daily_usage": [
    {
      "date": "2025-04-12",
      "requests": 53,
      "cost": 0.1493,
      "tokens": {
        "input": 5236,
        "output": 12384,
        "total": 17620
      }
    },
    {
      "date": "2025-04-10",
      "requests": 26,
      "cost": 0.0568,
      "tokens": {
        "input": 647,
        "output": 667,
        "total": 1314
      }
    },
    {
      "date": "2025-04-09",
      "requests": 2,
      "cost": 0.0053,
      "tokens": {
        "input": 35,
        "output": 18,
        "total": 53
      }
    }
  ]
}
```
