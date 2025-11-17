# Client API Reference

The `Client` class is the main entry point for interacting with the IndoxRouter API. This page documents all the methods and functionality provided by the client.

## Initialization

```python
from indoxrouter import Client

client = Client(
    api_key="your_api_key",
    timeout=30
)
```

### Parameters

- `api_key` (`str`, optional): Your API key for authentication. If not provided, the client will look for the `INDOX_ROUTER_API_KEY` environment variable.
- `timeout` (`int`, optional): Request timeout in seconds. Defaults to 30.

## Methods

### Authentication

```python
def _authenticate(self):
    """
    Authenticate with the server and get JWT tokens.
    This uses the /auth/token endpoint to get JWT tokens using the API key.
    """
```

This method is called automatically during initialization. It exchanges the API key for JWT tokens that are used for subsequent requests.

### Chat Completions

```python
def chat(
    self,
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """
    Generate a chat completion.

    Args:
        messages: A list of message objects with role and content keys.
        model: The model to use in format "provider/model_name".
        temperature: Controls randomness. Higher values (e.g., 0.8) make output more random,
                     lower values (e.g., 0.2) make it more deterministic.
        max_tokens: Maximum number of tokens to generate.
        stream: Whether to stream the response.
        **kwargs: Additional keyword arguments to pass to the API.

    Returns:
        A dictionary containing the API response.
    """
```

### Text Completions

```python
def completion(
    self,
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """
    Generate a text completion.

    Args:
        prompt: The prompt to complete.
        model: The model to use in format "provider/model_name".
        temperature: Controls randomness. Higher values make output more random,
                     lower values make it more deterministic.
        max_tokens: Maximum number of tokens to generate.
        stream: Whether to stream the response.
        **kwargs: Additional keyword arguments to pass to the API.

    Returns:
        A dictionary containing the API response.
    """
```

### Embeddings

```python
def embeddings(
    self,
    text: Union[str, List[str]],
    model: str = DEFAULT_EMBEDDING_MODEL,
    **kwargs,
) -> Dict[str, Any]:
    """
    Generate embeddings for the given text.

    Args:
        text: The text to embed. Can be a string or a list of strings.
        model: The model to use in format "provider/model_name".
        **kwargs: Additional keyword arguments to pass to the API.

    Returns:
        A dictionary containing the API response.
    """
```

### Image Generation

```python
def images(
    self,
    prompt: str,
    model: str = DEFAULT_IMAGE_MODEL,
    size: str = "1024x1024",
    n: int = 1,
    quality: str = "standard",
    style: str = "vivid",
    **kwargs,
) -> Dict[str, Any]:
    """
    Generate images from a text prompt.

    Args:
        prompt: The prompt to use for generating the image.
        model: The model to use in format "provider/model_name".
        size: The size of the image in format "widthxheight".
        n: The number of images to generate.
        quality: The quality of the image ("standard" or "hd").
        style: The style of the image ("vivid" or "natural").
        **kwargs: Additional keyword arguments to pass to the API.

    Returns:
        A dictionary containing the API response.
    """
```

### Model Information

```python
def models(self, provider: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about available models.

    Args:
        provider: Optional provider ID to filter by.

    Returns:
        A dictionary containing information about available models.
    """

def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
    """
    Get information about a specific model.

    Args:
        provider: The provider ID.
        model: The model ID.

    Returns:
        A dictionary containing information about the model.
    """
```

### Usage Information

```python
def get_usage(self) -> Dict[str, Any]:
    """
    Get usage information for the current user.

    Returns:
        A dictionary containing usage information.
    """
```

### Testing and Diagnostics

```python
def test_connection(self) -> Dict[str, Any]:
    """
    Test the connection to the server.

    Returns:
        A dictionary containing information about the connection.
    """

def diagnose_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Diagnose a request without sending it.

    Args:
        endpoint: The API endpoint (e.g., "chat/completions").
        data: The request data.

    Returns:
        A dictionary containing diagnostic information.
    """

def enable_debug(self, level=logging.DEBUG):
    """
    Enable debug logging.

    Args:
        level: The logging level to use.
    """
```

### Resource Management

```python
def close(self):
    """
    Close the client session and free up resources.
    """

def __enter__(self):
    """
    Enter the context manager.
    """
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """
    Exit the context manager and clean up resources.
    """
    self.close()
```

### Configuration

```python
def set_base_url(self, base_url: str) -> None:
    """
    Set the base URL for the API.

    Args:
        base_url: The base URL to use.
    """
```

_Last updated: Nov 16, 2025_