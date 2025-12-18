# indoxhub

[![Website](https://img.shields.io/badge/Website-indoxhub.com-blue)](https://indoxhub.com)

A unified Python client for accessing multiple AI providers through a single, consistent API. Switch between OpenAI, Anthropic, Google, Mistral, DeepSeek, XAI, and Qwen models seamlessly without changing your code.

## Installation

```bash
pip install indoxhub
```

## Quick Start

### Initialize the Client

```python
from indoxhub import Client

# Initialize with API key
client = Client(api_key="your_api_key")

# Or use environment variable INDOX_HUB_API_KEY
client = Client()
```

### Chat Completion Example

```python
response = client.chat(
    messages=[
        {"role": "user", "content": "Tell me a story about a robot in 5 sentences."}
    ],
    model="deepseek/deepseek-chat"
)

# Access response text from output array
print(response['output'][0]['content'][0]['text'])
print(f"Tokens used: {response['usage']['total_tokens']}")

# Note: Cost information is not included in individual response usage objects.
# Use get_usage() to get cost statistics.
```

## BYOK (Bring Your Own Key) Support

indoxhub supports BYOK, allowing you to use your own API keys for AI providers instead of using the platform's shared keys. This provides several benefits:

- **No credit deduction** from your indoxhub account
- **No rate limiting** from the platform
- **Direct provider access** with your own API keys
- **Cost control** - you pay providers directly at their rates

### Using BYOK

```python
# Use your own OpenAI API key
response = client.chat(
    messages=[{"role": "user", "content": "Hello!"}],
    model="openai/gpt-4",
    byok_api_key="sk-your-openai-key-here"
)

# Use your own Google API key for image generation
response = client.images(
    prompt="A beautiful sunset",
    model="google/imagen-3.0-generate-002",
    byok_api_key="your-google-api-key"
)

# Use your own API key for embeddings
response = client.embeddings(
    text="Sample text for embedding",
    model="openai/text-embedding-ada-002",
    byok_api_key="sk-your-openai-key-here"
)
```

### BYOK Benefits

- **Cost Savings**: No platform markup on API calls
- **Higher Limits**: Use provider's native rate limits
- **Direct Billing**: Pay providers directly at their rates
- **Full Control**: Access to all provider-specific features
- **No Platform Dependencies**: Works even if indoxhub is down

### Supported Endpoints

All AI endpoints support BYOK:

- ✅ Chat completions (`client.chat()`)
- ✅ Text completions (`client.completion()`)
- ✅ Embeddings (`client.embeddings()`)
- ✅ Image generation (`client.images()`)
- ✅ Video generation (`client.videos()`)
- ✅ Text-to-speech (`client.text_to_speech()`)

### Response Format

!!! note "Response Format Differences"
**Chat and Completions endpoints** use an OpenAI-compatible format with an `output` array. All other endpoints (embeddings, images, audio, etc.) use a standard format with a `data` field.

Chat and completion responses follow an OpenAI-compatible format:

```python
{
    'id': 'c08cc108-6b0d-48bd-a660-546143f1b9fa',
    'object': 'response',
    'created_at': 1718456006,
    'model': 'deepseek-chat',
    'provider': 'deepseek',
    'duration_ms': 9664.65,
    'output': [
        {
            'type': 'message',
            'status': 'completed',
            'role': 'assistant',
            'content': [
                {
                    'type': 'output_text',
                    'text': 'Your AI response text here...',
                    'annotations': []
                }
            ]
        }
    ],
    'usage': {
        'input_tokens': 15,
        'input_tokens_details': {'cached_tokens': 0},
        'output_tokens': 107,
        'output_tokens_details': {'reasoning_tokens': 0},
        'total_tokens': 122
    },
    'status': 'completed'
}
```

To access the response text: `response['output'][0]['content'][0]['text']`

### Usage Tracking

Monitor your usage and costs:

```python
# Get detailed usage statistics
usage = client.get_usage()
print(f"Total requests: {usage['total_requests']}")
print(f"Total cost: ${usage['total_cost']}")
print(f"Remaining credits: ${usage['remaining_credits']}")
```

### Model Information

Get detailed information about available models:

```python
# Get specific model info
model_info = client.get_model_info(provider="openai", model="gpt-4o-mini")
print(f"Context window: {model_info['specs']['context_window']}")
print(f"Capabilities: {model_info['capabilities']}")

# List all available models
models = client.models()
for provider in models:
    print(f"Provider: {provider['name']}")
    for model in provider.get('text_completions', []):
        print(f"  - {model['modelName']}")
```

## Using with OpenAI SDK

You can also use the OpenAI SDK with indoxhub's base URL:

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_indoxhub_api_key",
    base_url="https://api.indoxhub.com"
)

response = client.chat.completions.create(
    model="anthropic/claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Examples by Use Case

### Cost-Optimized Chat

```python
# Use fast, cost-effective models for high-volume applications
response = client.chat(
    messages=[{"role": "user", "content": "Summarize this text..."}],
    model="openai/gpt-3.5-turbo",  # Most cost-effective
    max_tokens=100
)
```

### High-Quality Analysis

```python
# Use premium models for complex reasoning
response = client.chat(
    messages=[{"role": "user", "content": "Analyze this complex problem..."}],
    model="anthropic/claude-3-opus-20240229",  # Highest quality
    temperature=0.1  # More focused responses
)
```

### Code Generation

```python
# Use specialized coding models
response = client.chat(
    messages=[{"role": "user", "content": "Write a Python function to..."}],
    model="deepseek/deepseek-coder",  # Optimized for coding
    temperature=0.0  # Deterministic code
)
```

### Vision & Image Analysis

```python
import base64

# Analyze images with vision-capable models
with open("photo.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image",
                    "image": {
                        "data": image_base64,
                        "media_type": "image/jpeg"
                    }
                }
            ]
        }
    ],
    model="openai/gpt-4o"
)

# Access response text from output array
print(response['output'][0]['content'][0]['text'])
```

### Image Generation

```python
# Generate images with different providers
response = client.images(
    prompt="A futuristic cityscape at sunset",
    model="openai/dall-e-3",
    size="1024x1024",
    style="vivid"
)

image_url = response['data'][0]['url']
```

### Video Generation

```python
# Generate videos (asynchronous process)
response = client.videos(
    prompt="A majestic eagle soaring over mountain peaks, cinematic camera movement",
    model="openai/sora-2",
    size="1280x720",
    duration=4
)

job_id = response['data']['job_id']

# Check job status
status_response = client.jobs(job_id=job_id)
if status_response['status'] == 'completed':
    video_url = status_response['result']['data'][0]['url']
```

## Rate Limits

indoxhub has three tiers with different rate limits:

| Tier       | Requests/Minute | Tokens/Hour | Best For                 |
| ---------- | --------------- | ----------- | ------------------------ |
| Free       | 10              | 10,000      | Testing & prototyping    |
| Standard   | 60              | 100,000     | Production applications  |
| Enterprise | 500             | 1,000,000   | High-volume applications |

Rate limit information is included in error responses when limits are exceeded.

## Next Steps

- **[Getting Started](getting-started.md)**: Detailed setup guide
- **[Usage Examples](usage/basic-usage.md)**: Comprehensive usage examples
- **[API Reference](api/client.md)**: Full API documentation

_Last updated: Nov 16, 2025_
