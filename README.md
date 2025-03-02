# IndoxRouter

A unified API for multiple LLM providers, allowing you to switch between different models seamlessly.

## Features

- Support for multiple providers (OpenAI, Anthropic, Mistral, Cohere, Google, Meta, AI21, Llama, NVIDIA, Deepseek, Databricks)
- Unified API for all providers
- User authentication and API key management
- Request logging and monitoring
- Dashboard for testing models
- Docker support for easy deployment

## Quick Start

### Local Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
pip install -r requirements.txt
```

3. Initialize the database:

```bash
python -m indoxRouter.init_db
```

4. Run the application:

```bash
python run.py
```

5. Access the application:
   - API: http://localhost:8000
   - Dashboard: http://localhost:7860

### Docker Installation

1. Clone the repository and configure:

```bash
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter
cp .env.example .env
# Edit .env with your configuration
```

2. Start with Docker Compose:

```bash
docker-compose up -d
```

3. Access the application:
   - API: http://localhost:8000
   - Dashboard: http://localhost:7860
   - pgAdmin: http://localhost:5050

## Detailed Documentation

For detailed deployment instructions, configuration options, and troubleshooting, please refer to the [Deployment Guide](DEPLOYMENT_GUIDE.md).

## API Usage

### Authentication

1. Register a new user through the dashboard or API.
2. Generate an API key for the user.
3. Use the API key in your requests.

### Making Requests

```python
import requests

api_key = "your_api_key"
url = "http://localhost:8000/v1/completions"

payload = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "prompt": "Hello, world!",
    "temperature": 0.7,
    "max_tokens": 100
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

## Client Library

IndoxRouter includes a Python client library for easy integration:

```python
from indoxRouter.client import Client

client = Client(api_key="your_api_key")

response = client.completions(
    provider="openai",
    model="gpt-3.5-turbo",
    prompt="Hello, world!",
    temperature=0.7,
    max_tokens=100
)

print(response)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
