<div class="hero-section">
<h1>IndoxRouter</h1>
<p>A unified Python client for accessing multiple AI providers through a single, consistent API. Switch between OpenAI, Anthropic, Google, Mistral, DeepSeek, XAI, and Qwen models seamlessly without changing your code.</p>
<a href="getting-started/" class="cta-button">Get Started</a>
</div>

## Installation

```bash
pip install indoxrouter
```

## Quick Start

### Initialize the Client

```python
from indoxrouter import Client

# Initialize with API key
client = Client(api_key="your_api_key")

# Or use environment variable INDOX_ROUTER_API_KEY
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

print(response['data'])
print(f"Cost: ${response['usage']['cost']}")
print(f"Tokens used: {response['usage']['tokens_total']}")
```

### Response Format

Every response includes detailed usage information:

```python
{
    'request_id': 'c08cc108-6b0d-48bd-a660-546143f1b9fa',
    'created_at': '2025-05-19T06:07:38.077269',
    'duration_ms': 9664.651870727539,
    'provider': 'deepseek',
    'model': 'deepseek-chat',
    'success': True,
    'message': '',
    'usage': {
        'tokens_prompt': 15,
        'tokens_completion': 107,
        'tokens_total': 122,
        'cost': 0.000229,
        'latency': 9.487398862838745,
        'timestamp': '2025-05-19T06:07:38.065330'
    },
    'data': 'Your AI response text here...',
    'finish_reason': None
}
```

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

You can also use the OpenAI SDK with IndoxRouter's base URL:

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_indoxrouter_api_key",
    base_url="https://api.indoxrouter.com"
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

## Rate Limits

IndoxRouter has three tiers with different rate limits:

| Tier       | Requests/Minute | Tokens/Hour | Best For                 |
| ---------- | --------------- | ----------- | ------------------------ |
| Free       | 10              | 10,000      | Testing & prototyping    |
| Standard   | 60              | 100,000     | Production applications  |
| Enterprise | 500             | 1,000,000   | High-volume applications |

Rate limit information is included in error responses when limits are exceeded.

## Next Steps

- **[Getting Started](getting-started.md)**: Detailed setup guide
- **[Usage Examples](usage/basic-usage.md)**: Comprehensive usage examples
- **[Model Guide](usage/models.md)**: Complete model reference
- **[API Reference](api/client.md)**: Full API documentation
