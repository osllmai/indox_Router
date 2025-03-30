# IndoxRouter API Endpoints

This document provides a comprehensive overview of all available endpoints in the IndoxRouter API.

## Table of Contents

- [Authentication](#authentication)
- [Chat Completions](#chat-completions)
- [Text Completions](#text-completions)
- [Embeddings](#embeddings)
- [Image Generation](#image-generation)
- [Models](#models)
- [Health Check](#health-check)

## Authentication

Authentication is required for all API endpoints. You can authenticate using either:

1. **API Key**: Pass your API key in the `Authorization` header as a Bearer token.
2. **JWT Token**: Obtain a JWT token using the `/auth/token` endpoint and pass it in the `Authorization` header.

### Get JWT Token

```
POST /auth/token
```

**Request Body:**

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Chat Completions

Generate chat completions using various AI models.

```
POST /chat/completions
```

**Request Body:**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "provider": "openai",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false,
  "additional_params": {}
}
```

**Response:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-10T12:34:56.789Z",
  "duration_ms": 1234.56,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "success": true,
  "message": "",
  "data": "I'm doing well, thank you for asking! How can I assist you today?",
  "finish_reason": "stop",
  "usage": {
    "tokens_prompt": 23,
    "tokens_completion": 15,
    "tokens_total": 38,
    "cost": 0.00045,
    "latency": 1.234,
    "timestamp": "2024-03-10T12:34:56.789Z"
  }
}
```

### Streaming Response

Set `stream: true` in the request to receive a streaming response. The response will be a stream of server-sent events (SSE).

## Text Completions

Generate text completions using various AI models.

```
POST /completions
```

**Request Body:**

```json
{
  "prompt": "Once upon a time",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false,
  "additional_params": {}
}
```

**Response:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-10T12:34:56.789Z",
  "duration_ms": 1234.56,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "success": true,
  "message": "",
  "data": "in a land far, far away, there lived a brave knight who...",
  "finish_reason": "length",
  "usage": {
    "tokens_prompt": 4,
    "tokens_completion": 100,
    "tokens_total": 104,
    "cost": 0.0006,
    "latency": 1.234,
    "timestamp": "2024-03-10T12:34:56.789Z"
  }
}
```

### Streaming Response

Set `stream: true` in the request to receive a streaming response. The response will be a stream of server-sent events (SSE).

## Embeddings

Generate embeddings for text using various AI models.

```
POST /embeddings
```

**Request Body:**

```json
{
  "text": "Hello, world!",
  "provider": "openai",
  "model": "text-embedding-ada-002",
  "additional_params": {}
}
```

**Response:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-10T12:34:56.789Z",
  "duration_ms": 123.45,
  "provider": "openai",
  "model": "text-embedding-ada-002",
  "success": true,
  "message": "Successfully generated embeddings",
  "data": [
    [0.0023064255, -0.009327292, ...]
  ],
  "dimensions": 1536,
  "usage": {
    "tokens_prompt": 3,
    "tokens_completion": 0,
    "tokens_total": 3,
    "cost": 0.0000003,
    "latency": 0.123,
    "timestamp": "2024-03-10T12:34:56.789Z"
  }
}
```

## Image Generation

Generate images from text prompts using various AI models.

```
POST /images/generations
```

**Request Body:**

```json
{
  "prompt": "A beautiful sunset over the ocean",
  "provider": "openai",
  "model": "dall-e-3",
  "size": "1024x1024",
  "n": 1,
  "additional_params": {
    "quality": "standard",
    "style": "vivid"
  }
}
```

**Response:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-10T12:34:56.789Z",
  "duration_ms": 3456.78,
  "provider": "openai",
  "model": "dall-e-3",
  "success": true,
  "message": "Successfully generated image",
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": null
    }
  ],
  "usage": {
    "tokens_prompt": 8,
    "tokens_completion": 0,
    "tokens_total": 8,
    "cost": 0.02,
    "latency": 3.456,
    "timestamp": "2024-03-10T12:34:56.789Z"
  }
}
```

## Models

Get information about available models.

### List All Models

```
GET /models
```

**Response:**

```json
{
  "providers": [
    {
      "id": "openai",
      "name": "OpenAI",
      "description": "OpenAI's models",
      "capabilities": ["chat", "completion", "embedding", "image"],
      "models": [
        {
          "id": "gpt-4o-mini",
          "name": "GPT-4o Mini",
          "provider": "openai",
          "capabilities": ["chat", "completion"],
          "description": "GPT-4o mini enables a broad range of tasks with its low cost and latency",
          "max_tokens": 128000,
          "pricing": {
            "input": 0.00015,
            "output": 0.0006
          }
        }
        // More models...
      ]
    }
    // More providers...
  ]
}
```

### Get Model Information

```
GET /models/{provider}/{model}
```

**Response:**

```json
{
  "id": "gpt-4o-mini",
  "name": "GPT-4o Mini",
  "provider": "openai",
  "capabilities": ["chat", "completion"],
  "description": "GPT-4o mini enables a broad range of tasks with its low cost and latency",
  "max_tokens": 128000,
  "pricing": {
    "input": 0.00015,
    "output": 0.0006
  }
}
```

## Health Check

Check if the API is running.

```
GET /
```

**Response:**

```json
{
  "status": "ok",
  "version": "0.2.0",
  "timestamp": "2024-03-10T12:34:56.789Z"
}
```

## Error Responses

All endpoints return a standard error response format:

```json
{
  "error": "error_code",
  "message": "Error message",
  "status_code": 400,
  "details": {
    // Additional error details
  }
}
```

Common error codes:

- `invalid_request`: The request is invalid
- `authentication_error`: Authentication failed
- `permission_denied`: Permission denied
- `not_found`: Resource not found
- `rate_limit_exceeded`: Rate limit exceeded
- `provider_error`: Error from the provider
- `insufficient_credits`: Insufficient credits

## Rate Limiting

The API has rate limiting in place to prevent abuse. Rate limits are applied per API key and are reset hourly.

## Credits

Each request consumes credits based on the model used, the number of tokens processed, and the operation type. Credit usage is calculated in real-time using the pricing information from the provider's model configuration.

## Support

For support, please contact support@indoxrouter.com or visit our [documentation](https://docs.indoxrouter.com).
