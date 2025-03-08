# Basic Usage Examples

This page provides basic examples of using indoxRouter for various tasks.

## Setup

First, import the necessary modules and initialize the client:

```python
from indoxRouter import Client
from indoxRouter.models import ChatMessage

# Initialize the client with your API key
client = Client(api_key="your-api-key")
```

## Chat Completion

### Basic Chat

```python
# Define your messages
messages = [
    {"role": "user", "content": "What are three fun activities to do in New York?"}
]

# Make the API call
response = client.chat(
    messages=messages,
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
)

# Print the response
print(response.data)
```

### Multi-turn Conversation

```python
# Define your messages for a multi-turn conversation
messages = [
    {"role": "user", "content": "Hello, I'm planning a trip to Japan."},
    {"role": "assistant", "content": "That's exciting! Japan is a wonderful destination with rich culture, delicious food, and beautiful landscapes. When are you planning to visit, and what kinds of activities are you interested in?"},
    {"role": "user", "content": "I'm planning to go in April for two weeks. I'm interested in both traditional and modern aspects of Japan."}
]

# Make the API call
response = client.chat(
    messages=messages,
    model="anthropic/claude-3-haiku",
    temperature=0.7,
    max_tokens=500,
)

# Print the response
print(response.data)

# Continue the conversation
messages.append({"role": "assistant", "content": response.data})
messages.append({"role": "user", "content": "What are the must-visit places in Tokyo?"})

# Make another API call
response = client.chat(
    messages=messages,
    model="anthropic/claude-3-haiku",
    temperature=0.7,
    max_tokens=500,
)

# Print the response
print(response.data)
```

### Using System Messages

```python
# Define your messages with a system message
messages = [
    {"role": "system", "content": "You are a helpful travel assistant who provides concise recommendations."},
    {"role": "user", "content": "What are three fun activities to do in New York?"}
]

# Make the API call
response = client.chat(
    messages=messages,
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
)

# Print the response
print(response.data)
```

## Text Completion

### Basic Completion

```python
# Define your prompt
prompt = "Write a short story about a robot learning to paint."

# Make the API call
response = client.completion(
    prompt=prompt,
    model="anthropic/claude-3-haiku",
    temperature=0.7,
    max_tokens=500,
)

# Print the response
print(response.data)
```

### Controlling Output with Parameters

```python
# Define your prompt
prompt = "Write a poem about the ocean."

# Make the API call with specific parameters
response = client.completion(
    prompt=prompt,
    model="openai/gpt-4o-mini",
    temperature=0.9,  # Higher temperature for more creative output
    max_tokens=200,
    top_p=0.8,
    frequency_penalty=0.5,
    presence_penalty=0.5,
)

# Print the response
print(response.data)
```

## Embeddings

### Single Text Embedding

```python
# Define your text
text = "This is a sample text to embed."

# Make the API call
response = client.embeddings(
    text=text,
    model="openai/text-embedding-3-small",
)

# Print the embedding dimensions
print(f"Embedding dimensions: {len(response.data[0])}")
```

### Multiple Text Embeddings

```python
# Define your texts
texts = [
    "This is the first sample text to embed.",
    "This is the second sample text to embed.",
    "This is the third sample text to embed."
]

# Make the API call
response = client.embeddings(
    text=texts,
    model="openai/text-embedding-3-small",
)

# Print the number of embeddings and their dimensions
print(f"Number of embeddings: {len(response.data)}")
print(f"Embedding dimensions: {len(response.data[0])}")
```

## Image Generation

### Basic Image Generation

```python
# Define your prompt
prompt = "A futuristic city with flying cars and neon lights"

# Make the API call
response = client.image(
    prompt=prompt,
    model="openai/dall-e-3",
    size="1024x1024",
)

# Print the image URL
print(response.data[0])
```

### Multiple Images

```python
# Define your prompt
prompt = "A serene landscape with mountains and a lake"

# Make the API call
response = client.image(
    prompt=prompt,
    model="openai/dall-e-3",
    size="1024x1024",
    n=3,  # Generate 3 images
)

# Print the image URLs
for i, image_url in enumerate(response.data):
    print(f"Image {i+1}: {image_url}")
```

## Provider and Model Information

### List Providers

```python
# List all providers
providers = client.providers()
print(f"Available providers: {[p['id'] for p in providers]}")
```

### List Models

```python
# List all models
models = client.models()
print("Available models:")
for provider, provider_models in models.items():
    print(f"\n{provider}:")
    for model in provider_models:
        print(f"  - {model['id']}")
```

### Get Model Information

```python
# Get information about a specific model
model_info = client.model_info(provider="openai", model="gpt-4o-mini")
print(f"Model: {model_info.name}")
print(f"Provider: {model_info.provider}")
print(f"Type: {model_info.type}")
print(f"Description: {model_info.description}")
print(f"Input price per 1K tokens: ${model_info.input_price_per_1k_tokens}")
print(f"Output price per 1K tokens: ${model_info.output_price_per_1k_tokens}")
```

## Usage and User Information

### Get Usage Statistics

```python
# Get usage statistics
usage = client.get_usage()
print(f"Total tokens used: {usage['total_tokens']}")
print(f"Total cost: ${usage['total_cost']}")
```

### Get User Information

```python
# Get user information
user_info = client.get_user_info()
print(f"User ID: {user_info['id']}")
print(f"Email: {user_info['email']}")
print(f"Plan: {user_info['plan']}")
```

## Resource Management

### Using a Context Manager

```python
# Using a context manager
with Client(api_key="your-api-key") as client:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello, world!"}],
        model="openai/gpt-4o-mini",
    )
    print(response.data)
```

### Manually Closing the Client

```python
# Manually closing the client
client = Client(api_key="your-api-key")
response = client.chat(
    messages=[{"role": "user", "content": "Hello, world!"}],
    model="openai/gpt-4o-mini",
)
print(response.data)
client.close()
```
