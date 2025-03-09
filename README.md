# IndoxRouter

A unified interface for various AI providers, including OpenAI, Anthropic, Cohere, Google, and Mistral.

## Project Structure

This repository contains two main components:

1. **indoxrouter**: A Python client library for interacting with the IndoxRouter server.
2. **indoxrouter_server**: A FastAPI server that provides a unified API for various AI providers.

## IndoxRouter Client

The IndoxRouter client is a Python library that provides a simple interface for interacting with the IndoxRouter server. It handles authentication, request formatting, and response parsing.

### Installation

```bash
pip install indoxrouter
```

### Usage

```python
from indoxrouter import Client

# Initialize client with API key
client = Client(api_key="your_api_key", base_url="http://your-server-url:8000")

# Generate a chat completion
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
    provider="openai",
    model="gpt-3.5-turbo"
)

print(response["choices"][0]["message"]["content"])
```

For more examples, see the [examples](indoxrouter/examples) directory.

## IndoxRouter Server

The IndoxRouter server is a FastAPI application that provides a unified API for various AI providers. It handles authentication, rate limiting, and provider-specific implementations.

### Installation

```bash
pip install indoxrouter-server
```

### Running the Server

```bash
# Create a .env file with your API keys
echo "OPENAI_API_KEY=your-openai-api-key" > .env

# Run the server
indoxrouter-server
```

### Docker Deployment

```bash
# Clone the repository
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter/indoxrouter_server

# Create a .env file with your API keys
echo "OPENAI_API_KEY=your-openai-api-key" > .env

# Build and run with Docker Compose
docker-compose up -d
```

For more information, see the [indoxrouter_server README](indoxrouter_server/README.md).

## Development

### Setting Up the Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter

# Install the client in development mode
cd indoxrouter
pip install -e ".[dev]"

# Install the server in development mode
cd ../indoxrouter_server
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run client tests
cd indoxrouter
pytest

# Run server tests
cd ../indoxrouter_server
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
