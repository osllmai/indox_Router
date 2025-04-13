# Authentication & Authorization

IndoxRouter uses API key-based authentication for all API endpoints. This document describes the authentication and authorization mechanisms implemented in the server.

## API Key Authentication

### API Key Format

API keys follow a specific format:

```
indox_<random-string>
```

Example: `indox_4mfg24GRj_qGaZ2-qXw-mXYqaNqMkyGkG1lncGUrRkA`

API keys are stored in the PostgreSQL database in the `api_keys` table, along with metadata such as the associated user, creation date, expiration date, and permissions.

### Authentication Flow

1. A client includes the API key in the Authorization header of the request:

```
Authorization: Bearer indox_4mfg24GRj_qGaZ2-qXw-mXYqaNqMkyGkG1lncGUrRkA
```

2. The authentication middleware extracts the API key from the header
3. The middleware validates the API key against the database
4. If the key is valid, the middleware attaches the user information to the request context
5. If the key is invalid, the middleware returns a 401 Unauthorized response

### API Key Validation

API keys are validated using the following criteria:

- The key must exist in the database
- The key must be active (`is_active = true`)
- The key must not be expired (either `expires_at IS NULL` or `expires_at > NOW()`)
- The associated user account must be active

## User Authentication

For admin and dashboard access, IndoxRouter provides traditional username/password authentication:

1. User submits credentials to the `/api/v1/auth/token` endpoint
2. Server validates the credentials against the database
3. If valid, the server generates a JWT token
4. The token is returned to the client and used for subsequent requests

```python
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: TokenRequest):
    """
    Authenticate user and return access token.
    """
    # Verify username and password
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    # Return token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
```

## Authorization

### API Key Permissions

API keys can have customized permissions through the `permissions` field in the `api_keys` table. This JSON field can specify:

- Allowed providers and models
- Request rate limits
- Maximum token usage
- Enabled endpoints

Example permissions structure:

```json
{
  "allowed_providers": ["openai", "mistral"],
  "allowed_models": ["openai/gpt-4o-mini", "mistral/mistral-large-latest"],
  "rate_limit": 100, // requests per minute
  "token_limit": 50000, // tokens per day
  "endpoints": {
    "chat": true,
    "completion": true,
    "embedding": true,
    "image": false
  }
}
```

### Implementation in Middleware

The authorization middleware checks these permissions against the current request:

```python
@app.middleware("http")
async def check_permissions(request: Request, call_next):
    """Check API key permissions."""
    # Skip for non-API routes
    if not request.url.path.startswith("/api/v1/"):
        return await call_next(request)

    # Get user and API key from request state
    user = request.state.user
    api_key_id = request.state.api_key_id
    permissions = request.state.permissions

    # Skip if no permissions defined
    if not permissions:
        return await call_next(request)

    # Check endpoint permission
    endpoint = get_endpoint_from_path(request.url.path)
    if endpoint and not permissions.get("endpoints", {}).get(endpoint, True):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": f"This API key does not have permission to access {endpoint} endpoint"},
        )

    # Check provider permission
    provider = get_provider_from_request(request)
    if provider and "allowed_providers" in permissions:
        if provider not in permissions["allowed_providers"]:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": f"This API key does not have permission to use {provider} provider"},
            )

    # Continue processing the request
    return await call_next(request)
```

## Credit System

In addition to authentication and authorization, IndoxRouter implements a credit system to control usage:

1. Each user account has a credit balance stored in the `credits` field of the `users` table
2. Each API request costs a certain amount of credits based on:
   - The provider and model used
   - The number of tokens processed
   - The endpoint type
3. Before processing a request, the system checks if the user has sufficient credits
4. If sufficient, the request is processed and the credits are deducted
5. If insufficient, the request is rejected with a 402 Payment Required response

This credit system allows for usage-based monetization and prevents abuse of the API.
