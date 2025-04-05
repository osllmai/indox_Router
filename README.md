# IndoxRouter

A unified interface for LLM providers like OpenAI, Anthropic, Together.ai, and others.

## Project Structure

This repository contains two main components:

1. **indoxRouter_server**: A FastAPI server that provides a unified API for various LLM providers. This component is dockerized for easy deployment.
2. **indoxRouter_client**: A Python client library for interacting with the server.

## Server Component (Dockerized)

The server component can be run using Docker, making it easy to deploy on any system.

### Quick Start

```bash
# Go to the server directory
cd indoxRouter_server

# Run the server
./start-server.sh  # On Linux/Mac (you may need to make it executable with chmod +x start-server.sh)
# Or
start-server.bat   # On Windows
```

Other modes:

```bash
# Production mode
./start-server.sh prod  # Or start-server.bat prod

# Clean mode (reset containers and start fresh)
./start-server.sh clean  # Or start-server.bat clean
```

For more options:

```bash
./start-server.sh help  # Or start-server.bat help
```

### Production Deployment

```bash
# Deploy to a remote server
cd indoxRouter_server
./scripts/deploy.sh --user username --host your-server.com
```

See the [IndoxRouter Server README](indoxRouter_server/README.md) for more detailed instructions.

## Client Component

The client component is a Python library that can be installed on your system to interact with the server.

### Usage

```python
from indoxRouter_client import Client

# Connect to the server
client = Client(api_key="your-api-key")

# Generate a chat completion
response = client.chat([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Tell me a joke."}
], model="openai/gpt-4o-mini")

print(response.content)
```

## Database Setup

IndoxRouter uses a hybrid database approach:

- **PostgreSQL**: User accounts, authentication, API keys
- **MongoDB**: Model data, conversation history, embeddings, caching

Both databases are automatically set up when using Docker for the server component.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
