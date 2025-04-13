# IndoxRouter Server Documentation

## Overview

IndoxRouter is an AI model routing server that provides a unified API interface to multiple AI model providers, including OpenAI, Mistral, DeepSeek, Anthropic, Google, and Cohere. It acts as a proxy between client applications and AI service providers, providing consistent API endpoints for:

- Chat completions
- Text completions
- Embeddings
- Image generation

IndoxRouter adds several key features on top of raw provider APIs:

- Unified API format across providers
- Multi-provider support through a single API key
- User management and authentication
- Credit tracking and usage monitoring
- Request logging and analytics
- Response caching
- Model information and discovery

## Table of Contents

- [Architecture](architecture.md)
- [API Reference](api-reference.md)
- [Database Schema](database-schema.md)
- [Provider Integration](provider-integration.md)
- [Authentication & Authorization](authentication.md)
- [Configuration](configuration.md)
- [Deployment](deployment.md)
- [Contributing](contributing.md)

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start the MongoDB and PostgreSQL databases:
   ```
   ./run_local_db.sh
   ```
4. Configure your `.env` file with provider API keys
5. Run the server:
   ```
   python main.py
   ```

## Tech Stack

- **FastAPI**: Web framework
- **PostgreSQL**: Relational database for user data, API keys, and aggregated usage stats
- **MongoDB**: Document database for detailed request logs, model info, and response caching
- **Docker**: Containerization for deployment
- **Pydantic**: Data validation and schema definition
