# IndoxRouter API Reference

This document provides a reference for the IndoxRouter REST API endpoints.

## Authentication

All API requests require authentication using an API key. The API key should be included in the `X-API-Key` header.

```
X-API-Key: indox_your_api_key_here
```

## API Endpoints

### User Management

#### Get Current User

```
GET /api/v1/users/me
```

Returns information about the authenticated user.

**Response**

```json
{
  "id": "user_123456",
  "email": "user@example.com",
  "name": "Example User",
  "balance": 10.0,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### Get User Balance

```
GET /api/v1/users/me/balance
```

Returns the current balance of the authenticated user.

**Response**

```json
{
  "balance": 10.0
}
```

### API Keys

#### List API Keys

```
GET /api/v1/api-keys
```

Returns a list of API keys for the authenticated user.

**Response**

```json
{
  "api_keys": [
    {
      "id": "key_123456",
      "key": "indox_abcdef123456",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z",
      "last_used_at": "2023-01-02T00:00:00Z"
    }
  ]
}
```

#### Create API Key

```
POST /api/v1/api-keys
```

Creates a new API key for the authenticated user.

**Response**

```json
{
  "id": "key_123456",
  "key": "indox_abcdef123456",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "last_used_at": null
}
```

#### Deactivate API Key

```
DELETE /api/v1/api-keys/{key_id}
```

Deactivates an API key.

**Response**

```json
{
  "success": true,
  "message": "API key deactivated"
}
```

### Completions

#### Generate Completion

```
POST /api/v1/completions
```

Generates a completion using the specified provider and model.

**Request**

```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "prompt": "Explain quantum computing in simple terms",
  "max_tokens": 500,
  "temperature": 0.7,
  "top_p": 0.9,
  "system_prompt": "You are a helpful assistant."
}
```

**Response**

```json
{
  "text": "Quantum computing is like...",
  "cost": 0.05,
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 100,
    "total_tokens": 110
  },
  "remaining_credits": 9.95
}
```

### Models

#### List Available Models

```
GET /api/v1/models
```

Returns a list of available models across all providers.

**Response**

```json
{
  "models": [
    {
      "provider": "openai",
      "model": "gpt-4o",
      "description": "GPT-4o is OpenAI's most advanced model",
      "input_price_per_1k_tokens": 0.01,
      "output_price_per_1k_tokens": 0.03,
      "context_length": 128000
    },
    {
      "provider": "anthropic",
      "model": "claude-3-opus-20240229",
      "description": "Claude 3 Opus is Anthropic's most capable model",
      "input_price_per_1k_tokens": 0.015,
      "output_price_per_1k_tokens": 0.075,
      "context_length": 200000
    }
  ]
}
```

### Usage

#### Get Usage History

```
GET /api/v1/usage
```

Returns the usage history for the authenticated user.

**Query Parameters**

- `start_date` (optional): Start date for filtering (ISO format)
- `end_date` (optional): End date for filtering (ISO format)
- `provider` (optional): Filter by provider
- `model` (optional): Filter by model

**Response**

```json
{
  "usage": [
    {
      "id": "usage_123456",
      "provider": "openai",
      "model": "gpt-4o",
      "prompt_tokens": 10,
      "completion_tokens": 100,
      "total_tokens": 110,
      "cost": 0.05,
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total_cost": 0.05,
  "total_tokens": 110
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes and error messages in case of failure.

**Example Error Response**

```json
{
  "error": {
    "code": "insufficient_credits",
    "message": "Insufficient credits to complete the request",
    "details": {
      "required_credits": 0.05,
      "available_credits": 0.03
    }
  }
}
```

## Rate Limiting

The API is rate-limited to prevent abuse. The rate limits are as follows:

- 60 requests per minute per API key
- 1000 requests per hour per API key

When a rate limit is exceeded, the API returns a 429 Too Many Requests response with a Retry-After header indicating when the client can retry the request.
