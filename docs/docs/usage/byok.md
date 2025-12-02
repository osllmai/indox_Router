# BYOK (Bring Your Own Key) Support

indoxhub supports BYOK (Bring Your Own Key), allowing you to use your own API keys for AI providers instead of using the platform's shared API keys. This feature provides several benefits and gives you full control over your AI provider usage.

## What is BYOK?

BYOK (Bring Your Own Key) allows you to:

- **Use your own API keys** for AI providers (OpenAI, Anthropic, Google, etc.)
- **Bypass platform rate limits** and use provider's native limits
- **Avoid credit deduction** from your indoxhub account
- **Pay providers directly** at their rates without platform markup
- **Access full provider features** without platform restrictions

## How BYOK Works

When you provide a `byok_api_key` parameter:

1. **indoxhub authenticates** you with your platform API key
2. **Your provider API key** is used for the actual AI request
3. **No credits are deducted** from your indoxhub account
4. **No rate limiting** is applied by the platform
5. **Direct provider connection** is established

## Supported Endpoints

All AI endpoints in indoxhub support BYOK:

### Chat Completions

```python
response = client.chat(
    messages=[{"role": "user", "content": "Hello!"}],
    model="openai/gpt-4",
    byok_api_key="sk-your-openai-key-here"
)
```

### Text Completions

```python
response = client.completion(
    prompt="Complete this sentence:",
    model="openai/gpt-3.5-turbo-instruct",
    byok_api_key="sk-your-openai-key-here"
)
```

### Embeddings

```python
response = client.embeddings(
    text="Text to embed",
    model="openai/text-embedding-3-small",
    byok_api_key="sk-your-openai-key-here"
)
```

### Image Generation

```python
response = client.images(
    prompt="A beautiful sunset",
    model="openai/dall-e-3",
    size="1024x1024",
    byok_api_key="sk-your-openai-key-here"
)
```

### Text-to-Speech

```python
response = client.text_to_speech(
    input="Hello, world!",
    model="openai/tts-1",
    voice="alloy",
    byok_api_key="sk-your-openai-key-here"
)
```

## Provider-Specific Examples

### OpenAI

```python
# Chat with GPT-4
response = client.chat(
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    model="openai/gpt-4",
    byok_api_key="sk-your-openai-key-here"
)

# Generate images with DALL-E 3
response = client.images(
    prompt="A futuristic cityscape",
    model="openai/dall-e-3",
    size="1024x1024",
    byok_api_key="sk-your-openai-key-here"
)

# Create embeddings
response = client.embeddings(
    text="Machine learning concepts",
    model="openai/text-embedding-3-small",
    byok_api_key="sk-your-openai-key-here"
)
```

### Anthropic

```python
# Chat with Claude
response = client.chat(
    messages=[{"role": "user", "content": "Write a story"}],
    model="anthropic/claude-3-sonnet-20240229",
    byok_api_key="sk-ant-your-anthropic-key-here"
)
```

### Google

```python
# Chat with Gemini
response = client.chat(
    messages=[{"role": "user", "content": "Explain AI"}],
    model="google/gemini-1.5-pro",
    byok_api_key="your-google-api-key-here"
)

# Generate images with Imagen
response = client.images(
    prompt="A mountain landscape",
    model="google/imagen-3.0-generate-002",
    aspect_ratio="16:9",  # Google uses aspect ratios
    byok_api_key="your-google-api-key-here"
)
```

### Mistral

```python
# Chat with Mistral
response = client.chat(
    messages=[{"role": "user", "content": "Help with coding"}],
    model="mistral/mistral-large-latest",
    byok_api_key="your-mistral-api-key-here"
)
```

## Benefits of BYOK

### Cost Savings

- **No platform markup** on API calls
- **Direct provider billing** at their rates
- **No credit consumption** from your indoxhub account
- **Predictable costs** based on provider pricing

### Performance & Limits

- **Higher rate limits** using provider's native limits
- **No platform bottlenecks** or rate limiting
- **Direct provider connection** for faster response times
- **Full provider capabilities** without restrictions

### Control & Flexibility

- **Full control** over your provider accounts
- **Direct access** to provider dashboards and analytics
- **Provider-specific features** and parameters
- **No dependency** on platform availability

### Use Cases

- **High-volume applications** that need higher rate limits
- **Cost-sensitive projects** that benefit from direct provider pricing
- **Enterprise applications** that require full provider control
- **Development and testing** with your own API keys

## Security Considerations

### API Key Management

- **Keep your API keys secure** and never expose them in client-side code
- **Use environment variables** for storing API keys
- **Rotate keys regularly** for security best practices
- **Monitor usage** through provider dashboards

### Best Practices

```python
import os

# Store API keys in environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Use in requests
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4",
    byok_api_key=OPENAI_API_KEY
)
```

## Troubleshooting

### Common Issues

#### Invalid API Key

```python
# Ensure your API key is valid and has proper permissions
response = client.chat(
    messages=[{"role": "user", "content": "Test"}],
    model="openai/gpt-4",
    byok_api_key="sk-valid-openai-key-here"
)
```

#### Provider Mismatch

```python
# Ensure the model matches the provider of your API key
# OpenAI key with OpenAI model
response = client.chat(
    messages=[{"role": "user", "content": "Test"}],
    model="openai/gpt-4",  # ✅ Correct
    byok_api_key="sk-openai-key-here"
)

# Don't use OpenAI key with Anthropic model
# response = client.chat(
#     messages=[{"role": "user", "content": "Test"}],
#     model="anthropic/claude-3",  # ❌ Wrong provider
#     byok_api_key="sk-openai-key-here"
# )
```

#### Rate Limiting

- **BYOK bypasses platform rate limits** but not provider rate limits
- **Check your provider's rate limits** in their dashboard
- **Monitor usage** to avoid hitting provider limits

### Debug Information

When using BYOK, responses include:

- `"byok_api_key": true` in the response data
- `X-RateLimit-Bypass: BYOK API key used` in response headers
- Cost field set to 0 in usage statistics

## Migration Guide

### From Platform Keys to BYOK

1. **Get API keys** from your preferred providers
2. **Update your code** to include `byok_api_key` parameter
3. **Test with small requests** to ensure everything works
4. **Monitor costs** through provider dashboards
5. **Scale up** as needed

### Example Migration

**Before (Platform Keys):**

```python
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4"
)
```

**After (BYOK):**

```python
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4",
    byok_api_key="sk-your-openai-key-here"
)
```

## Next Steps

- **[Basic Usage](basic-usage.md)**: Learn the fundamentals of indoxhub
- **[Chat Completions](chat.md)**: Detailed chat completion examples
- **[Image Generation](images.md)**: Create images with BYOK support
- **[Embeddings](embeddings.md)**: Generate embeddings with your own keys
- **[Text-to-Speech](tts.md)**: Convert text to speech with BYOK

---

_BYOK support is available for all indoxhub AI endpoints. Start using your own API keys today for better control, cost savings, and performance._

_Last updated: Nov 16, 2025_