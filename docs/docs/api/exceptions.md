# Exceptions

IndoxRouter provides specific exception classes to help you handle different types of errors gracefully.

## Exception Hierarchy

```
IndoxRouterError (base exception)
├── AuthenticationError
├── RateLimitError
├── APIError
├── NetworkError
└── ValidationError
```

## Base Exception

### IndoxRouterError

The base exception class for all IndoxRouter-related errors.

```python
from indoxrouter import IndoxRouterError

try:
    response = client.chat(messages=[...], model="invalid/model")
except IndoxRouterError as e:
    print(f"An error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
```

## Specific Exceptions

### AuthenticationError

Raised when API key is invalid or missing.

```python
from indoxrouter import Client, AuthenticationError

try:
    client = Client(api_key="invalid_key")
    response = client.chat(messages=[...])
except AuthenticationError as e:
    print("Authentication failed. Please check your API key.")
    print(f"Error details: {e}")
```

### RateLimitError

Raised when you exceed the rate limits.

```python
from indoxrouter import RateLimitError
import time

try:
    response = client.chat(messages=[...])
except RateLimitError as e:
    print("Rate limit exceeded. Waiting before retry...")
    time.sleep(60)  # Wait 1 minute
    # Retry the request
```

### APIError

Raised for general API errors from the provider.

```python
from indoxrouter import APIError

try:
    response = client.chat(messages=[...])
except APIError as e:
    print(f"API error occurred: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Error message: {e.message}")
```

### NetworkError

Raised for network-related issues.

```python
from indoxrouter import NetworkError

try:
    response = client.chat(messages=[...])
except NetworkError as e:
    print("Network error occurred. Please check your connection.")
    print(f"Error details: {e}")
```

### ValidationError

Raised when request parameters are invalid.

```python
from indoxrouter import ValidationError

try:
    response = client.chat(
        messages=[],  # Empty messages list
        model="openai/gpt-4o-mini"
    )
except ValidationError as e:
    print("Invalid request parameters:")
    print(f"Error details: {e}")
```

## Error Handling Best Practices

### Comprehensive Error Handling

```python
from indoxrouter import (
    Client,
    AuthenticationError,
    RateLimitError,
    APIError,
    NetworkError,
    ValidationError,
    IndoxRouterError
)
import time

def robust_chat(client, messages, model, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat(messages=messages, model=model)
            return response

        except AuthenticationError:
            print("Authentication failed. Please check your API key.")
            return None

        except ValidationError as e:
            print(f"Invalid request parameters: {e}")
            return None

        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Rate limit hit. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print("Rate limit exceeded after all retries.")
                return None

        except NetworkError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Network error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print("Network error persists after all retries.")
                return None

        except APIError as e:
            print(f"API error: {e}")
            if e.status_code >= 500 and attempt < max_retries - 1:
                # Retry on server errors
                wait_time = 2 ** attempt
                print(f"Server error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                return None

        except IndoxRouterError as e:
            print(f"Unexpected IndoxRouter error: {e}")
            return None

    return None

# Usage
client = Client(api_key="your_api_key")
response = robust_chat(
    client,
    [{"role": "user", "content": "Hello!"}],
    "openai/gpt-4o-mini"
)

if response:
    print(response['choices'][0]['message']['content'])
else:
    print("Failed to get response after all attempts.")
```

### Logging Errors

```python
import logging
from indoxrouter import Client, IndoxRouterError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chat_with_logging(client, messages, model):
    try:
        response = client.chat(messages=messages, model=model)
        logger.info(f"Successfully generated response using {model}")
        return response

    except IndoxRouterError as e:
        logger.error(f"IndoxRouter error: {type(e).__name__}: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        raise

# Usage
client = Client(api_key="your_api_key")
try:
    response = chat_with_logging(
        client,
        [{"role": "user", "content": "Hello!"}],
        "openai/gpt-4o-mini"
    )
except IndoxRouterError:
    print("Failed to generate response due to IndoxRouter error.")
```

## Error Response Format

When an exception occurs, you can access additional information:

```python
try:
    response = client.chat(messages=[...])
except APIError as e:
    print(f"Status Code: {e.status_code}")
    print(f"Error Type: {e.error_type}")
    print(f"Message: {e.message}")
    print(f"Request ID: {e.request_id}")  # For debugging with support
```

_Last updated: Nov 08, 2025_