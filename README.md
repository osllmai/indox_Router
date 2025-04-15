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

## Automated Testing

IndoxRouter includes automated tests for both client and server components, ensuring high code quality and reliability.

### Client Tests

The client component includes:

- **Unit tests**: Test client functionality without requiring a live server
- **Integration tests**: Test client-server integration (requires a running server)

To run the client tests:

```bash
# Run all client tests (when server is available)
cd indoxRouter
python run_tests.py

# Run only unit tests (no server needed)
python run_tests.py --unit

# Run integration tests with a specific server
python run_tests.py --integration --server http://91.107.253.133:8000
```

See [IndoxRouter Client Tests](indoxRouter/tests/README.md) for more details.

### Continuous Integration

The project uses GitHub Actions for continuous integration:

- Automatically runs unit tests on push to main branches
- Tests across multiple Python versions (3.9, 3.10, 3.11)
- Can be configured to run integration tests with a live server (disabled by default)

To enable integration tests in GitHub Actions:

1. Set up your server at `91.107.253.133` (or any other location)
2. Configure GitHub repository secrets for server access
3. Uncomment the integration test section in `.github/workflows/python-tests.yml`

## Database Setup

IndoxRouter uses a hybrid database approach:

- **PostgreSQL**: User accounts, authentication, API keys
- **MongoDB**: Model data, conversation history, embeddings, caching

Both databases are automatically set up when using Docker for the server component.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
