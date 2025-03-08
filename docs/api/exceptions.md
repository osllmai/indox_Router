# Exceptions API Reference

indoxRouter provides a comprehensive set of exceptions to handle various error scenarios. All exceptions inherit from the base `IndoxRouterError` class.

## Exception Hierarchy

```
IndoxRouterError
├── AuthenticationError
├── NetworkError
├── RateLimitError
├── InvalidParametersError
├── ProviderError
│   ├── ModelNotFoundError
│   └── ProviderNotFoundError
```

## Base Exception

### IndoxRouterError

```python
from indoxRouter.exceptions import IndoxRouterError
```

The base exception class for all indoxRouter exceptions.

**Attributes:**

- `message`: A string describing the error.

## Authentication Exceptions

### AuthenticationError

```python
from indoxRouter.exceptions import AuthenticationError
```

Raised when there's an issue with authentication, such as an invalid API key or expired token.

**Example:**

```python
try:
    client = Client(api_key="invalid-api-key")
except AuthenticationError as e:
    print(f"Authentication error: {e}")
```

## Network Exceptions

### NetworkError

```python
from indoxRouter.exceptions import NetworkError
```

Raised when there's a network-related issue, such as a connection error or timeout.

**Example:**

```python
try:
    response = client.chat(messages=[{"role": "user", "content": "Hello"}])
except NetworkError as e:
    print(f"Network error: {e}")
```

## Rate Limiting Exceptions

### RateLimitError

```python
from indoxRouter.exceptions import RateLimitError
```

Raised when the rate limit for an endpoint is exceeded.

**Attributes:**

- `message`: A string describing the error.
- `reset_time`: A datetime object indicating when the rate limit will reset.

**Example:**

```python
try:
    response = client.chat(messages=[{"role": "user", "content": "Hello"}])
except RateLimitError as e:
    print(f"Rate limit exceeded. Resets at {e.reset_time}")
```

## Parameter Exceptions

### InvalidParametersError

```python
from indoxRouter.exceptions import InvalidParametersError
```

Raised when invalid parameters are provided to a method.

**Example:**

```python
try:
    response = client.chat(messages=[{"invalid_key": "value"}])
except InvalidParametersError as e:
    print(f"Invalid parameters: {e}")
```

## Provider Exceptions

### ProviderError

```python
from indoxRouter.exceptions import ProviderError
```

Base class for provider-related exceptions.

**Example:**

```python
try:
    response = client.chat(messages=[{"role": "user", "content": "Hello"}])
except ProviderError as e:
    print(f"Provider error: {e}")
```

### ModelNotFoundError

```python
from indoxRouter.exceptions import ModelNotFoundError
```

Raised when a specified model is not found.

**Example:**

```python
try:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="nonexistent-model"
    )
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
```

### ProviderNotFoundError

```python
from indoxRouter.exceptions import ProviderNotFoundError
```

Raised when a specified provider is not found.

**Example:**

```python
try:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="nonexistent-provider/model"
    )
except ProviderNotFoundError as e:
    print(f"Provider not found: {e}")
```

## Handling Multiple Exceptions

You can handle multiple exceptions using a try-except block:

```python
from indoxRouter import Client
from indoxRouter.exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    InvalidParametersError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
)

try:
    client = Client(api_key="your-api-key")
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="openai/gpt-4o-mini"
    )
except AuthenticationError as e:
    print(f"Authentication error: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Resets at {e.reset_time}")
except InvalidParametersError as e:
    print(f"Invalid parameters: {e}")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except ProviderNotFoundError as e:
    print(f"Provider not found: {e}")
except ProviderError as e:
    print(f"Provider error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Specific to General**: Catch more specific exceptions before more general ones.
2. **Logging**: Log exceptions for debugging purposes.
3. **Retry Logic**: Implement retry logic for transient errors like network issues or rate limiting.
4. **User Feedback**: Provide meaningful error messages to users.

```python
import logging
import time
from indoxRouter.exceptions import NetworkError, RateLimitError

def make_request_with_retry(client, messages, max_retries=3, backoff_factor=1.5):
    retries = 0
    while retries < max_retries:
        try:
            return client.chat(messages=messages)
        except NetworkError as e:
            logging.warning(f"Network error: {e}. Retrying ({retries+1}/{max_retries})...")
            retries += 1
            time.sleep(backoff_factor ** retries)
        except RateLimitError as e:
            wait_time = (e.reset_time - datetime.now()).total_seconds()
            logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
            time.sleep(wait_time + 1)  # Add 1 second buffer
            retries += 1

    raise Exception(f"Failed after {max_retries} retries")
```
