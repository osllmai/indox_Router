# Client API Reference

The `Client` class is the main entry point for interacting with indoxRouter. It provides methods for making requests to various LLM providers through a unified interface.

## Initialization

```python
from indoxRouter import Client

client = Client(
    api_key="your-api-key",
    base_url="https://api.indoxrouter.com/v1",
    timeout=15,
    auto_refresh=True
)
```

### Parameters

| Parameter      | Type   | Default                            | Description                                                                                                          |
| -------------- | ------ | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `api_key`      | `str`  | `None`                             | Your indoxRouter API key. If not provided, the client will look for the `INDOX_ROUTER_API_KEY` environment variable. |
| `base_url`     | `str`  | `"https://api.indoxrouter.com/v1"` | The base URL for the indoxRouter API.                                                                                |
| `timeout`      | `int`  | `15`                               | Request timeout in seconds.                                                                                          |
| `auto_refresh` | `bool` | `True`                             | Whether to automatically refresh the authentication token when it expires.                                           |

## Core Methods

### Chat Completion

```python
response = client.chat(
    messages=[{"role": "user", "content": "Hello, world!"}],
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
    stream=False,
    return_generator=False,
    **kwargs
)
```

Generate a chat completion response.

#### Parameters

| Parameter          | Type                                       | Default  | Description                                                                               |
| ------------------ | ------------------------------------------ | -------- | ----------------------------------------------------------------------------------------- |
| `messages`         | `List[Union[Dict[str, str], ChatMessage]]` | Required | A list of messages to send to the model. Each message should have a `role` and `content`. |
| `model`            | `str`                                      | Required | The model to use, in the format `provider/model`.                                         |
| `temperature`      | `float`                                    | `0.7`    | Controls randomness. Higher values produce more random outputs.                           |
| `max_tokens`       | `int`                                      | `None`   | The maximum number of tokens to generate.                                                 |
| `stream`           | `bool`                                     | `False`  | Whether to stream the response.                                                           |
| `return_generator` | `bool`                                     | `False`  | If `stream=True`, whether to return a generator that yields chunks of the response.       |
| `**kwargs`         |                                            |          | Additional parameters to pass to the provider.                                            |

#### Returns

A `ChatResponse` object with the following attributes:

- `data`: The generated text.
- `model`: The model used.
- `provider`: The provider used.
- `success`: Whether the request was successful.
- `message`: A message describing the result.
- `usage`: A `Usage` object with token usage information.
- `finish_reason`: The reason the generation stopped.
- `raw_response`: The raw response from the provider.

### Text Completion

```python
response = client.completion(
    prompt="Once upon a time",
    model="anthropic/claude-3-haiku",
    temperature=0.7,
    max_tokens=500,
    stream=False,
    return_generator=False,
    **kwargs
)
```

Generate a text completion response.

#### Parameters

| Parameter          | Type    | Default  | Description                                                                         |
| ------------------ | ------- | -------- | ----------------------------------------------------------------------------------- |
| `prompt`           | `str`   | Required | The prompt to complete.                                                             |
| `model`            | `str`   | Required | The model to use, in the format `provider/model`.                                   |
| `temperature`      | `float` | `0.7`    | Controls randomness. Higher values produce more random outputs.                     |
| `max_tokens`       | `int`   | `None`   | The maximum number of tokens to generate.                                           |
| `stream`           | `bool`  | `False`  | Whether to stream the response.                                                     |
| `return_generator` | `bool`  | `False`  | If `stream=True`, whether to return a generator that yields chunks of the response. |
| `**kwargs`         |         |          | Additional parameters to pass to the provider.                                      |

#### Returns

A `CompletionResponse` object with similar attributes to `ChatResponse`.

### Embeddings

```python
response = client.embeddings(
    text="This is a sample text to embed.",
    model="openai/text-embedding-3-small",
    **kwargs
)
```

Generate embeddings for text.

#### Parameters

| Parameter  | Type                    | Default  | Description                                                     |
| ---------- | ----------------------- | -------- | --------------------------------------------------------------- |
| `text`     | `Union[str, List[str]]` | Required | The text to embed. Can be a single string or a list of strings. |
| `model`    | `str`                   | Required | The model to use, in the format `provider/model`.               |
| `**kwargs` |                         |          | Additional parameters to pass to the provider.                  |

#### Returns

An `EmbeddingResponse` object with the following attributes:

- `data`: The embeddings.
- `model`: The model used.
- `provider`: The provider used.
- `success`: Whether the request was successful.
- `message`: A message describing the result.
- `usage`: A `Usage` object with token usage information.
- `dimensions`: The number of dimensions in the embeddings.
- `raw_response`: The raw response from the provider.

### Image Generation

```python
response = client.image(
    prompt="A futuristic city with flying cars and neon lights",
    model="openai/dall-e-3",
    size="1024x1024",
    **kwargs
)
```

Generate images from text prompts.

#### Parameters

| Parameter  | Type  | Default     | Description                                       |
| ---------- | ----- | ----------- | ------------------------------------------------- |
| `prompt`   | `str` | Required    | The prompt to generate an image from.             |
| `model`    | `str` | Required    | The model to use, in the format `provider/model`. |
| `size`     | `str` | `"512x512"` | The size of the image to generate.                |
| `**kwargs` |       |             | Additional parameters to pass to the provider.    |

#### Returns

An `ImageResponse` object with the following attributes:

- `data`: A list of image URLs or base64-encoded images.
- `model`: The model used.
- `provider`: The provider used.
- `success`: Whether the request was successful.
- `message`: A message describing the result.
- `usage`: A `Usage` object with token usage information.
- `raw_response`: The raw response from the provider.

## Provider and Model Information

### List Providers

```python
# List all providers
providers = client.providers()
```

Returns a list of available providers.

### List Models

```python
# List all models
models = client.models()

# List models for a specific provider
openai_models = client.models(provider="openai")
```

Returns a dictionary mapping provider names to lists of model dictionaries.

### Get Model Information

```python
# Get information about a specific model
model_info = client.model_info(provider="openai", model="gpt-4o-mini")
```

Returns a `ModelInfo` object with information about the model.

## Usage and User Information

### Get Usage Statistics

```python
# Get usage statistics
usage = client.get_usage()
```

Returns a dictionary with usage statistics.

### Get User Information

```python
# Get user information
user_info = client.get_user_info()
```

Returns a dictionary with user information.

## Resource Management

The `Client` class implements the context manager protocol, so you can use it with a `with` statement to automatically close the client when you're done with it.

```python
# Using a context manager
with Client(api_key="your-api-key") as client:
    response = client.chat(messages=[{"role": "user", "content": "Hello, world!"}])

# Manually closing the client
client = Client(api_key="your-api-key")
response = client.chat(messages=[{"role": "user", "content": "Hello, world!"}])
client.close()
```

## Error Handling

The `Client` class raises various exceptions when errors occur. See the [Exceptions API Reference](exceptions.md) for more information.
