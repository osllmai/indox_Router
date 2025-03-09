# Chat Completion Example

This example demonstrates how to use the IndoxRouter client to generate chat completions from various AI providers.

## Basic Chat Completion

```python
from indoxrouter import Client

# Initialize client with API key
client = Client(api_key="your_api_key")

# Generate a chat completion
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7
)

# Print the response
print(response["choices"][0]["message"]["content"])
```

## Streaming Chat Completion

```python
from indoxrouter import Client

# Initialize client with API key
client = Client(api_key="your_api_key")

# Generate a streaming chat completion
print("Response: ", end="", flush=True)
for chunk in client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short story about a robot learning to paint."}
    ],
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7,
    stream=True
):
    if "choices" in chunk and len(chunk["choices"]) > 0:
        content = chunk["choices"][0].get("delta", {}).get("content", "")
        print(content, end="", flush=True)
print("\n")
```

## Using Different Providers

### Anthropic (Claude)

```python
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
    provider="anthropic",
    model="claude-3-haiku-20240307",
    temperature=0.7
)
```

### Mistral

```python
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
    provider="mistral",
    model="mistral-small",
    temperature=0.7
)
```

### Google (Gemini)

```python
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
    provider="google",
    model="gemini-pro",
    temperature=0.7
)
```

## Error Handling

```python
from indoxrouter import Client
from indoxrouter.exceptions import ModelNotFoundError, ProviderNotFoundError

try:
    client = Client(api_key="your_api_key")
    response = client.chat(
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        provider="nonexistent",
        model="nonexistent-model"
    )
except ProviderNotFoundError as e:
    print(f"Provider not found: {e}")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
```
