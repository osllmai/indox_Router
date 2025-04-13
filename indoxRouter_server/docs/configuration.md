# Configuration

IndoxRouter is configured using environment variables, typically stored in a `.env` file. This document describes the available configuration options and their defaults.

## Core Configuration

| Variable                    | Default           | Description                                       |
| --------------------------- | ----------------- | ------------------------------------------------- |
| APP_NAME                    | IndoxRouter       | Application name                                  |
| APP_VERSION                 | 0.1.0             | Application version                               |
| DEBUG                       | false             | Enable debug mode                                 |
| LOG_LEVEL                   | info              | Log level (debug, info, warning, error, critical) |
| ENVIRONMENT                 | production        | Environment (development, staging, production)    |
| SECRET_KEY                  | random-string     | Secret key for token generation                   |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440              | JWT token expiration time in minutes              |
| DEFAULT_ADMIN_USERNAME      | admin             | Default admin username                            |
| DEFAULT_ADMIN_PASSWORD      | random-string     | Default admin password                            |
| DEFAULT_ADMIN_EMAIL         | admin@example.com | Default admin email                               |

## Server Configuration

| Variable        | Default               | Description                             |
| --------------- | --------------------- | --------------------------------------- |
| HOST            | 0.0.0.0               | Server host                             |
| PORT            | 8000                  | Server port                             |
| WORKERS         | 1                     | Number of worker processes              |
| CORS_ORIGINS    | \*                    | Allowed CORS origins (comma-separated)  |
| REQUEST_TIMEOUT | 300                   | Request timeout in seconds              |
| ENABLE_DOCS     | true                  | Enable Swagger/ReDoc documentation      |
| EXTERNAL_URL    | http://localhost:8000 | External URL for callbacks and webhooks |

## Database Configuration

| Variable           | Default                                                  | Description                  |
| ------------------ | -------------------------------------------------------- | ---------------------------- |
| DATABASE_URL       | postgresql://postgres:postgres@postgres:5432/indoxrouter | PostgreSQL connection string |
| DB_MIN_CONNECTIONS | 1                                                        | Minimum database connections |
| DB_MAX_CONNECTIONS | 10                                                       | Maximum database connections |
| MONGODB_URI        | mongodb://mongo:27017                                    | MongoDB connection string    |
| MONGODB_DATABASE   | indoxrouter                                              | MongoDB database name        |

## Provider Configuration

| Variable                 | Default                | Description                        |
| ------------------------ | ---------------------- | ---------------------------------- |
| OPENAI_API_KEY           | -                      | OpenAI API key                     |
| MISTRAL_API_KEY          | -                      | Mistral API key                    |
| DEEPSEEK_API_KEY         | -                      | DeepSeek API key                   |
| ANTHROPIC_API_KEY        | -                      | Anthropic API key                  |
| GOOGLE_API_KEY           | -                      | Google AI API key                  |
| COHERE_API_KEY           | -                      | Cohere API key                     |
| DEFAULT_PROVIDER         | openai                 | Default provider for API requests  |
| DEFAULT_CHAT_MODEL       | gpt-4o-mini            | Default model for chat completions |
| DEFAULT_COMPLETION_MODEL | gpt-4o-mini            | Default model for text completions |
| DEFAULT_EMBEDDING_MODEL  | text-embedding-3-small | Default model for embeddings       |
| DEFAULT_IMAGE_MODEL      | dall-e-3               | Default model for image generation |

## Feature Configuration

| Variable                  | Default | Description                              |
| ------------------------- | ------- | ---------------------------------------- |
| ENABLE_RESPONSE_CACHE     | true    | Enable response caching                  |
| CACHE_TTL_DAYS            | 7       | Cache TTL in days                        |
| ENABLE_ANALYTICS          | true    | Enable usage analytics                   |
| ENABLE_RATE_LIMITING      | true    | Enable rate limiting                     |
| RATE_LIMIT_REQUESTS       | 100     | Default rate limit (requests per minute) |
| ENABLE_CONTENT_MODERATION | false   | Enable content moderation                |
| ENABLE_STREAMING          | true    | Enable streaming responses               |

## Example Configuration

Here's an example `.env` file with typical configuration:

```env
# Core configuration
APP_NAME=IndoxRouter
APP_VERSION=0.1.0
DEBUG=false
LOG_LEVEL=info
ENVIRONMENT=production
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Server configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
CORS_ORIGINS=*
REQUEST_TIMEOUT=300
ENABLE_DOCS=true
EXTERNAL_URL=https://your-api-domain.com

# Database configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/indoxrouter
DB_MIN_CONNECTIONS=5
DB_MAX_CONNECTIONS=20
MONGODB_URI=mongodb://mongo:27017
MONGODB_DATABASE=indoxrouter

# Provider configuration
OPENAI_API_KEY=sk-...
MISTRAL_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
COHERE_API_KEY=...
DEFAULT_PROVIDER=openai
DEFAULT_CHAT_MODEL=gpt-4o-mini
DEFAULT_COMPLETION_MODEL=gpt-4o-mini
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
DEFAULT_IMAGE_MODEL=dall-e-3

# Feature configuration
ENABLE_RESPONSE_CACHE=true
CACHE_TTL_DAYS=7
ENABLE_ANALYTICS=true
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
ENABLE_CONTENT_MODERATION=false
ENABLE_STREAMING=true
```

## Configuration Loading

The application loads configuration in the following order of precedence:

1. Environment variables
2. `.env` file in the current directory
3. Default values

Configuration is handled by the `Settings` class in `app/core/config.py`:

```python
class Settings(BaseSettings):
    """Application settings."""

    # Core settings
    APP_NAME: str = "IndoxRouter"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "info"
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ... additional settings ...

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
```

## Development Environment

For development, you can use the `development.env` file which is preconfigured with development settings:

```bash
cp development.env .env
```

This file includes settings optimized for development, such as:

- DEBUG=true
- LOG_LEVEL=debug
- ENVIRONMENT=development
- ENABLE_DOCS=true
- CORS_ORIGINS=http://localhost:3000,http://localhost:8000
