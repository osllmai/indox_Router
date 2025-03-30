# Resources Module

The Resources module is a core component of IndoxRouter that handles the interaction with various AI providers. It provides a unified interface for making requests to different AI providers and models.

## Overview

The Resources module consists of several resource classes, each responsible for a specific type of AI functionality:

- **Chat**: Handles chat completions (conversational AI)
- **Completions**: Handles text completions
- **Embeddings**: Handles text embeddings
- **Images**: Handles image generation

All resource classes inherit from the `BaseResource` class, which provides common functionality such as provider initialization, error handling, and user credit management.

## BaseResource

The `BaseResource` class is the base class for all resource classes. It provides the following methods:

- `_get_provider(provider, model_name, provider_api_key)`: Gets a provider implementation
- `_handle_provider_error(error)`: Handles provider errors
- `_update_user_credit(user_id, cost, endpoint, tokens_total)`: Updates a user's credit in the database

## Chat Resource

The `Chat` resource handles chat completions. It takes a list of messages and returns a response from the AI model.

### Usage

```python
from app.resources import Chat

chat = Chat()
response = chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ],
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000,
    user_id=123  # Optional, for tracking usage and credits
)

print(response.data)  # The assistant's response
print(response.usage.cost)  # The cost of the request
```

## Completions Resource

The `Completions` resource handles text completions. It takes a prompt and returns a completion from the AI model.

### Usage

```python
from app.resources import Completions

completions = Completions()
response = completions(
    prompt="Once upon a time",
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000,
    user_id=123  # Optional, for tracking usage and credits
)

print(response.data)  # The completion
print(response.usage.cost)  # The cost of the request
```

## Embeddings Resource

The `Embeddings` resource handles text embeddings. It takes a text or list of texts and returns embeddings from the AI model.

### Usage

```python
from app.resources import Embeddings

embeddings = Embeddings()
response = embeddings(
    text="Hello, world!",
    model="openai/text-embedding-ada-002",
    user_id=123  # Optional, for tracking usage and credits
)

print(response.data)  # The embeddings
print(response.dimensions)  # The dimensions of the embeddings
print(response.usage.cost)  # The cost of the request
```

## Images Resource

The `Images` resource handles image generation. It takes a prompt and returns generated images from the AI model.

### Usage

```python
from app.resources import Images

images = Images()
response = images(
    prompt="A beautiful sunset over the ocean",
    model="openai/dall-e-3",
    size="1024x1024",
    n=1,
    quality="standard",
    style="vivid",
    user_id=123  # Optional, for tracking usage and credits
)

print(response.data)  # The generated images
print(response.usage.cost)  # The cost of the request
```

## Cost Calculation

The Resources module calculates the cost of each request based on the token usage and the pricing information in the provider's JSON configuration files. The cost is calculated using the `calculate_cost` function from the `model_info` module.

### Model Information

Model information is loaded from JSON files in the `providers/json` directory. Each provider has its own JSON file containing information about its models, including pricing information.

The `model_info` module provides the following functions:

- `load_provider_models(provider)`: Loads model information for a provider
- `get_model_info(provider, model_name)`: Gets information about a specific model
- `calculate_cost(provider, model_name, tokens_prompt, tokens_completion)`: Calculates the cost of a request

## User Credit Management

The Resources module updates a user's credit in the database after each request. This is done using the `_update_user_credit` method of the `BaseResource` class, which calls the `update_user_credit` function in the `database` module.

The credit is updated based on the cost of the request, which is calculated using the pricing information in the provider's JSON configuration files.

## Error Handling

The Resources module handles errors from the providers and raises appropriate exceptions. This is done using the `_handle_provider_error` method of the `BaseResource` class.

Common errors include:

- `ProviderNotFoundError`: The provider is not found
- `ModelNotFoundError`: The model is not found
- `InvalidParametersError`: The parameters are invalid
- `RequestError`: The request to the provider fails
- `InsufficientCreditsError`: The user doesn't have enough credits
