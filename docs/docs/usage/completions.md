# Text Completions

IndoxRouter supports text completion endpoints for generating text based on prompts.

## Basic Text Completion

```python
from indoxrouter import Client

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
