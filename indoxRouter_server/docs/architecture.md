# Architecture

## System Architecture

IndoxRouter follows a layered architecture pattern with the following components:

```
┌───────────────┐
│  Client Apps  │
└───────┬───────┘
        │ HTTP/REST
┌───────▼───────┐
│  API Gateway  │ ◄── Authentication Middleware
└───────┬───────┘
        │
┌───────▼───────┐
│  API Routers  │ ◄── Routing Logic, Parameter Validation
└───────┬───────┘
        │
┌───────▼───────┐     ┌───────────────┐
│  Providers    │ ◄── │ Provider APIs │
└───────┬───────┘     └───────────────┘
        │
┌───────▼───────┐     ┌───────────────┐
│  Database     │ ◄── │ MongoDB       │
│  Layer        │ ◄── │ PostgreSQL    │
└───────────────┘     └───────────────┘
```

## Core Components

### API Gateway

The entry point for all requests, implemented in FastAPI. It:

- Handles request routing
- Applies authentication middleware
- Manages CORS settings
- Handles error responses

### API Routers

The API router modules handle specific endpoints:

- `/api/v1/chat/completions`: Chat model interactions
- `/api/v1/completions`: Text completion model interactions
- `/api/v1/embeddings`: Embedding model interactions
- `/api/v1/images/generations`: Image generation
- `/api/v1/models`: Model information and discovery
- `/api/v1/user`: User information and usage statistics

### Provider System

The provider system is responsible for integrating with third-party AI model providers. Each provider has its own implementation class that:

- Handles authentication with the provider's API
- Transforms requests to the provider's format
- Handles responses and error mapping
- Manages rate limiting and retry logic

### Database Layer

Two databases are used:

- **PostgreSQL**: Handles relational data including:
  - User accounts
  - API keys
  - Billing transactions
  - Aggregated usage statistics
- **MongoDB**: Handles document storage including:
  - Detailed usage logs
  - Model information
  - Provider configurations
  - Response caching
  - Conversations

## Data Flow

1. Client sends a request to one of the API endpoints
2. Authentication middleware validates the API key
3. Request is routed to the appropriate API router
4. API router validates the request parameters
5. Provider factory creates the appropriate provider instance
6. Provider processes the request and calls the external API
7. Response is processed and returned to the client
8. Usage statistics are logged to the databases

## Key Features Implementation

### Authentication

Authentication is implemented using API keys stored in the PostgreSQL database. The authentication middleware:

- Extracts the API key from the Authorization header
- Validates the key against the database
- Attaches the user information to the request context

### Usage Tracking

Usage tracking is implemented in two layers:

- Detailed usage logs in MongoDB record every request with full request/response details
- Aggregated daily summaries in PostgreSQL for efficient reporting

### Response Caching

Response caching is implemented using MongoDB to store:

- Request hash as the key
- Provider and model information
- Input data
- Output data
- Expiration time

### Provider Selection

Providers are selected based on the request parameters:

- Client can specify the provider/model directly (e.g., `openai/gpt-4o-mini`)
- Default providers can be configured for each endpoint type
