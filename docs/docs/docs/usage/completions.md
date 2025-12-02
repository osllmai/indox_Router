# Text Completions

indoxhub supports text completion endpoints for generating text based on prompts.

## Basic Text Completion

```python
from indoxhub import Client

client = Client(api_key="your_api_key")

# Generate text completion
response = client.completions(
    prompt="The future of artificial intelligence is",
    model="openai/gpt-3.5-turbo-instruct",
    max_tokens=100,
    temperature=0.7
)

print("Response:", response["data"])
```

## Parameters

- `prompt`: The text prompt to complete
- `model`: The model to use for completion
- `max_tokens`: Maximum number of tokens to generate
- `temperature`: Controls randomness (0.0 to 2.0)
- `top_p`: Controls diversity via nucleus sampling
- `frequency_penalty`: Penalizes frequent tokens
- `presence_penalty`: Penalizes new tokens

## BYOK (Bring Your Own Key) Support

indoxhub supports BYOK for text completions, allowing you to use your own API keys for AI providers:

```python
# Use your own OpenAI API key for completions
response = client.completion(
    prompt="The future of artificial intelligence is",
    model="openai/gpt-3.5-turbo-instruct",
    max_tokens=100,
    temperature=0.7,
    byok_api_key="sk-your-openai-key-here"
)

# Use your own Anthropic API key for completions
response = client.completion(
    prompt="Explain quantum computing in simple terms:",
    model="anthropic/claude-3-sonnet-20240229",
    max_tokens=150,
    byok_api_key="sk-ant-your-anthropic-key-here"
)

# Use your own Google API key for completions
response = client.completion(
    prompt="Write a short story about a robot:",
    model="google/gemini-1.5-pro",
    max_tokens=200,
    byok_api_key="your-google-api-key-here"
)
```

### BYOK Benefits for Text Completions

- **No Credit Deduction**: Your indoxhub credits remain unchanged
- **No Rate Limiting**: Bypass platform rate limits
- **Direct Provider Access**: Connect directly to your provider accounts
- **Cost Control**: Pay providers directly at their rates
- **Full Features**: Access to all provider-specific completion features

## Example Use Cases

### Creative Writing

```python
response = client.completions(
    prompt="Once upon a time in a magical forest,",
    model="openai/gpt-3.5-turbo-instruct",
    max_tokens=200,
    temperature=0.9
)
```

### Code Generation

```python
response = client.completions(
    prompt="# Python function to calculate fibonacci numbers\ndef fibonacci(n):",
    model="openai/gpt-3.5-turbo-instruct",
    max_tokens=150,
    temperature=0.2
)
```

_Last updated: Nov 08, 2025_