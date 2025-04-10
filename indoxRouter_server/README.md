# IndoxRouter Server

A unified API server for various AI providers, including OpenAI, Anthropic, Cohere, Google, and Mistral.

## Features

- **Unified API**: Access multiple AI providers through a single API
- **Authentication**: Secure your API with JWT authentication
- **Rate Limiting**: Control API usage with rate limiting
- **Streaming**: Support for streaming responses
- **Docker Support**: Easy deployment with Docker
- **Credit System**: Track and manage user credits for API usage
- **Model Information**: Comprehensive information about available models

## Capabilities

- **Chat Completions**: Generate conversational responses
- **Text Completions**: Generate text completions
- **Embeddings**: Generate vector embeddings for text
- **Image Generation**: Generate images from text prompts

## Getting Started

### Prerequisites

- Python 3.8+
- Docker (optional)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/indoxRouter_server.git
cd indoxRouter_server
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment file:

```bash
# For development with Docker
cp development.env .env

# OR for production deployment
cp production.env .env
```

The server uses two environment configuration files:

- `production.env`: Production deployment settings
- `development.env`: Development settings for use with Docker containers

### Running the Server

```bash
uvicorn main:app --reload
```

The server will be available at http://localhost:8000.

### Docker Deployment

1. Build and run with Docker Compose:

```bash
docker-compose up -d
```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Comprehensive API documentation is also available in the `docs/api/` directory:

- [API Endpoints](docs/api/endpoints.md): Documentation for all API endpoints
- [Resources](docs/api/resources.md): Documentation for the resources module
- [Credit System](docs/guides/credit-system.md): Documentation for the credit system
- [Model Information](docs/guides/model-info.md): Documentation for the model information system

## Authentication

To use the API, you need to authenticate first:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

This will return a JWT token that you can use for subsequent requests:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/token`: Get an access token using form data
- `POST /api/v1/auth/login`: Get an access token using JSON

### Models

- `GET /api/v1/models/`: Get all available providers and models
- `GET /api/v1/models/{provider_id}`: Get information about a specific provider
- `GET /api/v1/models/{provider_id}/{model_id}`: Get information about a specific model

### Chat

- `POST /api/v1/chat/completions`: Create a chat completion

### Completions

- `POST /api/v1/completions`: Create a text completion

### Embeddings

- `POST /api/v1/embeddings`: Create embeddings for text

### Images

- `POST /api/v1/images/generations`: Generate images from a prompt

## Architecture

### Resources Module

The Resources module is a core component of IndoxRouter that handles the interaction with various AI providers. It provides a unified interface for making requests to different AI providers and models.

The Resources module consists of several resource classes, each responsible for a specific type of AI functionality:

- **Chat**: Handles chat completions (conversational AI)
- **Completions**: Handles text completions
- **Embeddings**: Handles text embeddings
- **Images**: Handles image generation

All resource classes inherit from the `BaseResource` class, which provides common functionality such as provider initialization, error handling, and user credit management.

### Credit System

IndoxRouter includes a credit system that tracks and manages user credits for API usage. Credits are calculated based on the model used, the number of tokens processed, and the operation type.

Credits are calculated in real-time using the pricing information from the provider's model configuration. The calculation is done in the following steps:

1. The resource class processes the request and gets the token usage from the provider's response.
2. The `calculate_cost` function calculates the cost based on the token usage and the pricing information in the provider's JSON configuration file.
3. The `_update_user_credit` method updates the user's credit in the database.

### Model Information System

IndoxRouter includes a model information system that provides information about AI models from various providers. The system loads model information from JSON files in the `providers/json` directory. Each provider has its own JSON file containing information about its models, including capabilities, pricing, and other metadata.

## Development

### Running Tests

```bash
pytest
```

### Adding a New Provider

To add a new provider, you need to:

1. Create a new provider class in `app/providers/` that implements the `BaseProvider` interface
2. Add the provider to the factory in `app/providers/factory.py`
3. Add the provider's API key to the settings in `app/core/config.py`
4. Add the provider's JSON configuration file to `app/providers/json/`

### Adding a New Model

To add a new model, you need to add it to the appropriate provider's JSON file in `app/providers/json/`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
