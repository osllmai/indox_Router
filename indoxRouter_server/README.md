# IndoxRouter Server

A unified API server for various AI providers, including OpenAI, Anthropic, Cohere, Google, and Mistral.

## Features

- **Unified API**: Access multiple AI providers through a single API
- **Authentication**: Secure your API with JWT authentication
- **Rate Limiting**: Control API usage with rate limiting
- **Streaming**: Support for streaming responses
- **Docker Support**: Easy deployment with Docker

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

3. Create a `.env` file with your API keys:

```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
COHERE_API_KEY=your-cohere-api-key
GOOGLE_API_KEY=your-google-api-key
MISTRAL_API_KEY=your-mistral-api-key
```

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
4. Add the provider's JSON configuration file to `app/providers/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
