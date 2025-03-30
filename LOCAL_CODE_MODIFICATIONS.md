# Local Code Modifications for Testing

This guide shows minimal code modifications you can make to test indoxRouter locally without affecting production code.

## Approach

The key principle is to use environment variables or feature flags to control behavior, rather than changing the core code. This allows you to switch between local testing and production modes easily.

## Example Modifications

### 1. Database Connection (app/db/database.py)

Add a conditional check for a local testing environment variable:

```python
def init_db():
    """Initialize the database connection pool to the external website database."""
    global pool
    try:
        # Check if we're in local testing mode
        if os.environ.get("INDOXROUTER_LOCAL_TESTING") == "true":
            logger.info("Running in local testing mode")
            # You could add special handling for local testing here
            # For example, use a different connection method or mock the database

        # Create a connection pool to the external website database
        pool = ThreadedConnectionPool(
            minconn=settings.DB_MIN_CONNECTIONS,
            maxconn=settings.DB_MAX_CONNECTIONS,
            dsn=settings.DATABASE_URL,
        )
        logger.info("External database connection pool initialized")

        # Test the connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                logger.info("External database connection test successful")

        return True
    except Exception as e:
        logger.error(f"Failed to initialize external database connection: {e}")

        # In local testing mode, provide more detailed error information
        if os.environ.get("INDOXROUTER_LOCAL_TESTING") == "true":
            logger.error(f"Connection details: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")

        return False
```

### 2. API Key Validation (app/db/database.py)

Add a fallback for local testing:

```python
def validate_api_key(api_key: str) -> bool:
    """
    Validate if an API key exists and is active in the external website database.

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    # For local testing, accept a specific test API key
    if os.environ.get("INDOXROUTER_LOCAL_TESTING") == "true" and api_key == "test-api-key-for-local-development":
        logger.info("Using test API key for local development")
        return True

    user = get_user_by_api_key(api_key)
    return user is not None
```

### 3. Server Startup (main.py)

Add more graceful handling of database connection failures in local testing:

```python
@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    # Initialize connection to the external website database
    if settings.DATABASE_URL:
        if init_db():
            print(
                f"Successfully connected to external website database at {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}"
            )
        else:
            print("Error: Failed to connect to external website database.")

            # In local testing mode, continue despite database connection failure
            if os.environ.get("INDOXROUTER_LOCAL_TESTING") == "true":
                print("Running in local testing mode - continuing despite database error")
            else:
                import sys
                sys.exit(1)
    else:
        print(
            "Error: DATABASE_URL not set. Connection to external website database is required."
        )

        # In local testing mode, continue despite missing DATABASE_URL
        if os.environ.get("INDOXROUTER_LOCAL_TESTING") == "true":
            print("Running in local testing mode - continuing despite missing DATABASE_URL")
        else:
            import sys
            sys.exit(1)
```

### 4. Configuration (app/core/config.py)

Add local testing specific settings:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Local testing settings
    LOCAL_TESTING: bool = Field(default=False, env="INDOXROUTER_LOCAL_TESTING")
    LOCAL_TEST_API_KEY: str = Field(
        default="test-api-key-for-local-development",
        env="INDOXROUTER_LOCAL_TEST_API_KEY"
    )

    # ... rest of settings ...
```

## How to Use These Modifications

1. Create a `.env.local` file with your local testing settings:

   ```
   INDOXROUTER_LOCAL_TESTING=true
   INDOXROUTER_LOCAL_TEST_API_KEY=test-api-key-for-local-development
   ```

2. When running locally, load this file:

   ```bash
   # Linux/macOS
   export $(cat .env.local | xargs) && python -m uvicorn main:app --reload

   # Windows PowerShell
   Get-Content .env.local | ForEach-Object { $env:$($_.Split('=')[0])=$_.Split('=')[1] }; python -m uvicorn main:app --reload
   ```

3. For Docker, add these environment variables to your docker-compose.yml:
   ```yaml
   environment:
     - INDOXROUTER_LOCAL_TESTING=true
     - INDOXROUTER_LOCAL_TEST_API_KEY=test-api-key-for-local-development
   ```

## Best Practices

1. **Use environment variables** for configuration that changes between environments
2. **Add comments** explaining the purpose of local testing modifications
3. **Keep modifications minimal** and focused on specific areas
4. **Use feature flags** to enable/disable functionality
5. **Don't commit local testing changes** to production branches

## Reverting Changes for Production

Before deploying to production:

1. Remove any local testing environment variables
2. Ensure all code paths work correctly without local testing flags
3. Test with production-like settings

Remember that these modifications are meant to be temporary and should not be included in production code.
