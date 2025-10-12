# Chat Completions

Chat completions are the primary way to interact with conversational AI models like GPT-4, Claude, and Gemini. This guide covers how to use the chat completions feature of the IndoxRouter Client.

## Basic Usage

The simplest way to use chat completions is with the `chat()` method:

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")

response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke about programming."}
    ],
    model="openai/gpt-4o-mini"
)

print(response["data"])
```

## Message Format

The `messages` parameter is a list of dictionaries, each with `role` and `content` keys:

- `role`: Can be one of "system", "user", "assistant", or "function"
- `content`: The content of the message (string for text-only, or list for multimodal)

Example message formats:

```python
# System message (instructions to the AI)
{"role": "system", "content": "You are a helpful assistant."}

# User message (the user's input)
{"role": "user", "content": "What's the weather like today?"}

# Assistant message (previous responses from the assistant)
{"role": "assistant", "content": "I don't have access to current weather information."}

# Function message (for function calling, when available)
{"role": "function", "name": "get_weather", "content": '{"temperature": 72, "condition": "sunny"}'}
```

### Multimodal Messages (Text + Images)

For vision-capable models, you can send images along with text by using a list format for the content:

```python
import base64

# Read and encode image
with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

# Multimodal message with text and image
{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": "What's in this image?"
        },
        {
            "type": "image",
            "image": {
                "data": image_base64,
                "media_type": "image/jpeg"
            }
        }
    ]
}
```

!!! info "Vision Models"
Not all models support image inputs. Vision-capable models include `gpt-4o`, `claude-sonnet-4.5`, `gemini-2.0-flash`, and many others. See the [Vision & Multimodal](vision.md) guide for complete documentation.

## Model Selection

You can specify different models using the `provider/model_name` format:

```python
# OpenAI
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4o-mini"
)

# Anthropic
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="anthropic/claude-3-sonnet-20240229"
)

# Google
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="google/gemini-1.5-pro"
)

# Mistral
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="mistral/mistral-large-latest"
)
```

## Common Parameters

The chat method accepts several parameters to control the generation:

```python
response = client.chat(
    messages=[{"role": "user", "content": "Write a poem about AI."}],
    model="openai/gpt-4o-mini",
    temperature=0.7,  # Controls randomness (0-1)
    max_tokens=100,   # Maximum number of tokens to generate
    stream=False,     # Whether to stream the response
)
```

## BYOK (Bring Your Own Key) Support

IndoxRouter supports BYOK, allowing you to use your own API keys for AI providers. This bypasses platform rate limits and credit deductions:

```python
# Use your own OpenAI API key
response = client.chat(
    messages=[{"role": "user", "content": "Hello!"}],
    model="openai/gpt-4",
    byok_api_key="sk-your-openai-key-here"
)

# Use your own Anthropic API key
response = client.chat(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="anthropic/claude-3-sonnet-20240229",
    byok_api_key="sk-ant-your-anthropic-key-here"
)

# Use your own Google API key
response = client.chat(
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    model="google/gemini-1.5-pro",
    byok_api_key="your-google-api-key-here"
)
```

### BYOK Benefits for Chat

- **No Credit Deduction**: Your IndoxRouter credits remain unchanged
- **No Rate Limiting**: Bypass platform rate limits
- **Direct Provider Access**: Connect directly to your provider accounts
- **Cost Control**: Pay providers directly at their rates
- **Full Features**: Access to all provider-specific chat features

## Streaming Responses

For long responses, you might want to stream the response to get it piece by piece:

```python
print("Streaming response:")
for chunk in client.chat(
    messages=[
        {"role": "user", "content": "Tell me a story about a robot in 5 sentences."}
    ],
    model="mistral/ministral-8b-latest",
    stream=True
):
    if isinstance(chunk, dict) and "data" in chunk:
        print(chunk["data"], end="", flush=True)
    else:
        print(chunk, end="", flush=True)
print("\nStreaming complete!")
```

## Managing Conversations

For multi-turn conversations, you'll need to keep track of the message history:

```python
# Initialize the conversation with a system message
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

# First user message
messages.append({"role": "user", "content": "Hello, who are you?"})
response = client.chat(messages=messages, model="openai/gpt-4o-mini")
assistant_response = response["choices"][0]["message"]["content"]
messages.append({"role": "assistant", "content": assistant_response})
print(f"Assistant: {assistant_response}")

# Second user message
messages.append({"role": "user", "content": "What can you help me with?"})
response = client.chat(messages=messages, model="openai/gpt-4o-mini")
assistant_response = response["choices"][0]["message"]["content"]
messages.append({"role": "assistant", "content": assistant_response})
print(f"Assistant: {assistant_response}")
```

## Response Format

The response from the chat method follows this structure:

```python
{'request_id': 'b881942c-e21d-4f9d-ad82-47344945c642',
 'created_at': '2025-06-15T09:53:26.130868',
 'duration_ms': 1737.612247467041,
 'provider': 'openai',
 'model': 'gpt-4o-mini',
 'success': True,
 'message': '',
 'usage': {'tokens_prompt': 24,
  'tokens_completion': 7,
  'tokens_total': 31,
  'cost': 7.8e-06,
  'latency': 1.629077672958374,
  'timestamp': '2025-06-15T09:53:26.114626',
  'cache_read_tokens': 0,
  'cache_write_tokens': 0,
  'reasoning_tokens': 0,
  'web_search_count': 0,
  'request_count': 1,
  'cost_breakdown': {'input_tokens': 3.6e-06,
   'output_tokens': 4.2e-06,
   'cache_read': 0.0,
   'cache_write': 0.0,
   'reasoning': 0.0,
   'web_search': 0.0,
   'request': 0.0}},
 'raw_response': None,
 'data': 'The capital of France is Paris.',
 'finish_reason': None}
```
