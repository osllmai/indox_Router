# Local Testing Guide for IndoxRouter

This guide will help you test the IndoxRouter client and server locally using Docker before deploying to your production server.

## Prerequisites

- Docker installed on your local machine
- Python 3.8+ installed
- Git repository cloned locally

## Step 1: Set Up the IndoxRouter Server

### 1.1 Prepare the Environment File

First, create a `.env` file in the `indoxRouter_server` directory:

```bash
cd indoxRouter_server
cp .env.example .env
```

Edit the `.env` file to include your API keys for the providers you want to test:

```
# API settings
DEBUG=true

# Server settings
HOST=0.0.0.0
PORT=8000

# Security settings
SECRET_KEY=indoxrouter-local-dev-secret-2024
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS settings
CORS_ORIGINS=["*"]

# Provider API keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
COHERE_API_KEY=your-cohere-api-key
GOOGLE_API_KEY=your-google-api-key
MISTRAL_API_KEY=your-mistral-api-key

# Default provider and model
DEFAULT_PROVIDER=openai
DEFAULT_CHAT_MODEL=gpt-4o-mini
DEFAULT_COMPLETION_MODEL=gpt-4o-mini
DEFAULT_EMBEDDING_MODEL=text-embedding-ada-002

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD_SECONDS=60

# Test API key for local development
TEST_API_KEY=test-api-key-for-local-development
```

### 1.2 Install Required Packages

Make sure you have the required packages installed:

```bash
pip install pydantic-settings
```

### 1.3 Build and Run the Docker Container

Build and run the Docker container for the IndoxRouter server:

```bash
cd indoxRouter_server
docker build -t indoxrouter-server .
docker run -p 8000:8000 --name indoxrouter-server-container -v $(pwd)/.env:/app/.env -d indoxrouter-server
```

On Windows PowerShell, use this command instead:

```powershell
docker run -p 8000:8000 --name indoxrouter-server-container -v ${PWD}/.env:/app/.env -d indoxrouter-server
```

### 1.4 Verify the Server is Running

Check if the server is running by accessing the health check endpoint:

```bash
curl http://localhost:8000/
```

You should see a response like:

```json
{ "status": "ok", "message": "IndoxRouter Server is running" }
```

You can also check the logs:

```bash
docker logs indoxrouter-server-container
```

## Step 2: Configure the IndoxRouter Client

### 2.1 Update the Client Constants

For local testing, you need to update the `constants.py` file in the indoxrouter client to point to your local server:

```python
# API settings
DEFAULT_API_VERSION = "v1"
DEFAULT_BASE_URL = "http://localhost:8000"  # Point to local Docker container
DEFAULT_TIMEOUT = 60
```

### 2.2 Create a Test API Key

For testing purposes, you can create a simple API key. In a production environment, you would implement proper authentication, but for local testing, you can use a placeholder key.

Add this to your server's `.env` file (already added in step 1.1):

```
TEST_API_KEY=test-api-key-for-local-development
```

## Step 3: Create a Test Script

Create a test script to verify the client can communicate with your local server:

```python
# test_local.py
import os
from indoxrouter import Client

# Use a test API key
api_key = "test-api-key-for-local-development"

def test_health():
    """Test the health check endpoint."""
    try:
        client = Client(api_key=api_key)
        response = client._request("GET", "/")
        print("Health check response:", response)
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_models():
    """Test retrieving models."""
    try:
        client = Client(api_key=api_key)
        models = client.models()
        print(f"Retrieved {len(models)} models:")
        for model in models[:5]:  # Print first 5 models
            print(f"- {model.get('id', 'Unknown')}")
        return True
    except Exception as e:
        print(f"Models retrieval failed: {e}")
        return False

def test_chat():
    """Test chat completion."""
    try:
        client = Client(api_key=api_key)
        response = client.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ]
        )
        print("Chat response:")
        if "choices" in response and len(response["choices"]) > 0:
            print(response["choices"][0]["message"]["content"])
        else:
            print(response)
        return True
    except Exception as e:
        print(f"Chat completion failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing IndoxRouter client with local server")

    health_result = test_health()
    print("\nHealth check test:", "PASSED" if health_result else "FAILED")

    if health_result:
        models_result = test_models()
        print("\nModels test:", "PASSED" if models_result else "FAILED")

        chat_result = test_chat()
        print("\nChat test:", "PASSED" if chat_result else "FAILED")
```

## Step 4: Run the Tests

Run the test script:

```bash
python test_local.py
```

## Step 5: Test Specific Endpoints

### 5.1 Test Chat Completions

```python
from indoxrouter import Client

client = Client(api_key="test-api-key-for-local-development")

# Test with OpenAI
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    provider="openai",
    model="gpt-3.5-turbo"
)
print(response["choices"][0]["message"]["content"])
```

### 5.2 Test Embeddings

```python
from indoxrouter import Client

client = Client(api_key="test-api-key-for-local-development")

# Test embeddings
response = client.embeddings(
    text="This is a test sentence for embeddings.",
    provider="openai",
    model="text-embedding-ada-002"
)
print(f"Embedding dimensions: {response['dimensions']}")
print(f"First few values: {response['embeddings'][0][:5]}")
```

### 5.3 Test Image Generation

```python
from indoxrouter import Client

client = Client(api_key="test-api-key-for-local-development")

# Test image generation
response = client.images(
    prompt="A beautiful sunset over mountains",
    provider="openai",
    model="dall-e-3"
)
print(f"Image URL: {response['images'][0]['url']}")
```

## Step 6: Troubleshooting

### 6.1 Check Server Logs

If you encounter issues, check the server logs:

```bash
docker logs indoxrouter-server-container
```

### 6.2 Network Issues

If you're having network connectivity issues:

1. Make sure the port mapping is correct in your Docker run command
2. Check that the `DEFAULT_BASE_URL` in the client points to `http://localhost:8000`
3. Verify that the server is running with `curl http://localhost:8000/`

### 6.3 API Key Issues

If you're having authentication issues:

1. Check that the API key in your client matches what the server expects
2. For local testing, you might need to modify the server's authentication logic temporarily

### 6.4 Pydantic Version Issues

If you encounter errors related to Pydantic:

1. Make sure you have installed `pydantic-settings`:

   ```bash
   pip install pydantic-settings
   ```

2. Check that the imports in `app/core/config.py` are correct:

   ```python
   from pydantic import Field
   from pydantic_settings import BaseSettings
   ```

3. Ensure the model_config is properly set:
   ```python
   model_config = {
       "env_file": ".env",
       "case_sensitive": True
   }
   ```

## Step 7: Clean Up

When you're done testing, stop and remove the Docker container:

```bash
docker stop indoxrouter-server-container
docker rm indoxrouter-server-container
```

## Preparing for Production Deployment

Once your local tests are successful, you can prepare for production deployment:

1. Update the `constants.py` file in the indoxrouter client to point to your production server:

   ```python
   DEFAULT_BASE_URL = "http://91.107.253.133:8000"  # Your server IP
   ```

2. Follow the security guidelines in `API_KEY_SECURITY.md` to secure your API keys

3. Deploy the server to your production environment using Docker:
   ```bash
   docker-compose up -d
   ```

## Additional Notes

- For local testing, you don't need to encrypt your API keys, but for production deployment, follow the security guidelines
- The server is configured to run on port 8000 by default, but you can change this in the `.env` file
- Make sure your firewall allows connections to port 8000 on your production server
