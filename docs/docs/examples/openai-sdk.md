# Using OpenAI SDK with IndoxRouter

You can use the familiar OpenAI SDK with IndoxRouter to access all supported providers through the OpenAI-compatible API. This is perfect if you're already using OpenAI SDK in your codebase.

## Setup

Install the OpenAI SDK and configure it to use IndoxRouter:

```bash
pip install openai
```

```python
from openai import OpenAI

# Configure OpenAI client to use IndoxRouter
client = OpenAI(
    api_key="your_indoxrouter_api_key",  # Your IndoxRouter API key
    base_url="https://api.indoxrouter.com"  # IndoxRouter base URL
)
```

## Chat Completions

Use any provider's models through the OpenAI SDK interface:

### OpenAI Models

```python
# GPT-4o
response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
```

### Anthropic Models

```python
# Claude 3 Opus
response = client.chat.completions.create(
    model="anthropic/claude-3-opus-20240229",
    messages=[
        {"role": "user", "content": "Write a creative story about a time traveler"}
    ],
    temperature=0.8,
    max_tokens=800
)

print(response.choices[0].message.content)
```

### Google Models

```python
# Gemini Pro
response = client.chat.completions.create(
    model="google/gemini-1.5-pro",
    messages=[
        {"role": "user", "content": "Analyze the impact of AI on healthcare"}
    ],
    temperature=0.3,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

### DeepSeek Models

```python
# DeepSeek for coding
response = client.chat.completions.create(
    model="deepseek/deepseek-coder",
    messages=[
        {"role": "user", "content": "Write a Python function to calculate Fibonacci numbers"}
    ],
    temperature=0,
    max_tokens=300
)

print(response.choices[0].message.content)
```

## Streaming Responses

Stream responses from any provider:

```python
# Streaming with Claude
stream = client.chat.completions.create(
    model="anthropic/claude-3-sonnet-20240229",
    messages=[
        {"role": "user", "content": "Tell me a long story about space exploration"}
    ],
    stream=True,
    max_tokens=1500
)

print("Story: ", end="")
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

## Text Completions

Use text completion models:

```python
# GPT-3.5 Turbo Instruct
response = client.completions.create(
    model="openai/gpt-3.5-turbo-instruct",
    prompt="The future of artificial intelligence is",
    max_tokens=200,
    temperature=0.7
)

print(response.choices[0].text)
```

## Embeddings

Generate embeddings using different providers:

```python
# OpenAI embeddings
response = client.embeddings.create(
    model="openai/text-embedding-3-small",
    input="Hello, world!"
)

embedding = response.data[0].embedding
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")

# Multiple texts
response = client.embeddings.create(
    model="openai/text-embedding-3-large",
    input=[
        "Document 1: Introduction to machine learning",
        "Document 2: Deep learning fundamentals",
        "Document 3: Natural language processing"
    ]
)

for i, embedding_obj in enumerate(response.data):
    print(f"Document {i+1} embedding dimensions: {len(embedding_obj.embedding)}")
```

## Image Generation

Generate images using DALL-E or other providers:

```python
# DALL-E 3
response = client.images.generate(
    model="openai/dall-e-3",
    prompt="A futuristic cityscape with flying cars at sunset",
    size="1024x1024",
    quality="hd",
    style="vivid",
    n=1
)

image_url = response.data[0].url
print(f"Generated image: {image_url}")

# Get revised prompt
if hasattr(response.data[0], 'revised_prompt'):
    print(f"Revised prompt: {response.data[0].revised_prompt}")
```

## Error Handling

Handle errors using OpenAI SDK patterns:

```python
from openai import OpenAI, RateLimitError, AuthenticationError

client = OpenAI(
    api_key="your_indoxrouter_api_key",
    base_url="https://api.indoxrouter.com"
)

try:
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(response.choices[0].message.content)

except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")

except AuthenticationError as e:
    print(f"Authentication failed: {e}")

except Exception as e:
    print(f"Request failed: {e}")
```

## Advanced Usage

### Function Calling

Use function calling with supported models:

```python
import json

# Define a function
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ],
    tools=tools,
    tool_choice="auto"
)

# Check if the model wants to call a function
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    print(f"Model wants to call: {function_name}")
    print(f"With arguments: {function_args}")

    # Simulate function execution
    weather_result = {"temperature": "72°F", "condition": "sunny"}

    # Send function result back
    messages = [
        {"role": "user", "content": "What's the weather like in San Francisco?"},
        response.choices[0].message,
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(weather_result)
        }
    ]

    final_response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=messages
    )

    print(final_response.choices[0].message.content)
```

### JSON Mode

Request structured JSON responses:

```python
response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        {"role": "user", "content": "Generate a JSON object with information about Paris, France"}
    ],
    response_format={"type": "json_object"}
)

# Parse the JSON response
import json
city_info = json.loads(response.choices[0].message.content)
print(json.dumps(city_info, indent=2))
```

### Reproducible Outputs

Use seed for reproducible outputs (when supported):

```python
# Same prompt with same seed should give same result
response1 = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Generate a random number"}],
    seed=12345,
    temperature=0
)

response2 = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Generate a random number"}],
    seed=12345,
    temperature=0
)

print(f"Response 1: {response1.choices[0].message.content}")
print(f"Response 2: {response2.choices[0].message.content}")
print(f"Same result: {response1.choices[0].message.content == response2.choices[0].message.content}")
```

## Model Comparison

Easily compare responses from different providers:

```python
def compare_models(prompt, models):
    """Compare responses from different models."""

    results = {}

    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )

            results[model] = {
                'response': response.choices[0].message.content,
                'finish_reason': response.choices[0].finish_reason,
                'usage': response.usage._asdict() if response.usage else None
            }

        except Exception as e:
            results[model] = {'error': str(e)}

    return results

# Compare different models
prompt = "Explain the concept of artificial general intelligence in simple terms."
models = [
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku-20240307",
    "google/gemini-1.5-flash",
    "deepseek/deepseek-chat"
]

comparison = compare_models(prompt, models)

for model, result in comparison.items():
    print(f"\n{'='*50}")
    print(f"Model: {model}")
    print(f"{'='*50}")

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Response: {result['response'][:200]}...")
        if result['usage']:
            print(f"Tokens: {result['usage']['total_tokens']}")
```

## Provider-Specific Features

### Anthropic Claude Features

```python
# Claude with system message in messages (Anthropic style)
response = client.chat.completions.create(
    model="anthropic/claude-3-opus-20240229",
    messages=[
        {"role": "system", "content": "You are Claude, an AI assistant created by Anthropic."},
        {"role": "user", "content": "What are your capabilities?"}
    ],
    max_tokens=500
)
```

### Google Gemini Features

```python
# Gemini with longer context
response = client.chat.completions.create(
    model="google/gemini-1.5-pro",
    messages=[
        {"role": "user", "content": "Analyze this very long document..." + "x" * 10000}
    ],
    max_tokens=1000
)
```

## Batch Processing

Process multiple requests efficiently:

```python
import asyncio
from openai import AsyncOpenAI

# Use async client for better performance
async_client = AsyncOpenAI(
    api_key="your_indoxrouter_api_key",
    base_url="https://api.indoxrouter.com"
)

async def process_batch(prompts, model="openai/gpt-4o-mini"):
    """Process multiple prompts concurrently."""

    async def single_request(prompt):
        try:
            response = await async_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            return {
                'prompt': prompt,
                'response': response.choices[0].message.content,
                'success': True
            }
        except Exception as e:
            return {
                'prompt': prompt,
                'error': str(e),
                'success': False
            }

    # Process all prompts concurrently
    tasks = [single_request(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)

    return results

# Example usage
prompts = [
    "What is machine learning?",
    "Explain quantum computing",
    "How does blockchain work?",
    "What is artificial intelligence?"
]

# Run batch processing
results = asyncio.run(process_batch(prompts))

# Display results
for result in results:
    if result['success']:
        print(f"Q: {result['prompt']}")
        print(f"A: {result['response'][:100]}...")
        print()
    else:
        print(f"Failed: {result['prompt']} - {result['error']}")
```

## Migration from OpenAI

If you're migrating from direct OpenAI usage to IndoxRouter:

### Before (Direct OpenAI)

```python
from openai import OpenAI

client = OpenAI(api_key="sk-openai-key...")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### After (IndoxRouter)

```python
from openai import OpenAI

# Only change: API key and base URL
client = OpenAI(
    api_key="your_indoxrouter_api_key",  # IndoxRouter API key
    base_url="https://api.indoxrouter.com"  # IndoxRouter base URL
)

response = client.chat.completions.create(
    model="openai/gpt-4o",  # Specify provider/model
    messages=[{"role": "user", "content": "Hello"}]
)

# Access to other providers with same code!
response = client.chat.completions.create(
    model="anthropic/claude-3-opus-20240229",  # Switch to Anthropic
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Best Practices

### 1. Handle Provider-Specific Differences

```python
def robust_chat_completion(model, messages, **kwargs):
    """Make chat completion with provider-specific handling."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response

    except Exception as e:
        error_msg = str(e).lower()

        # Handle common provider-specific errors
        if "context length" in error_msg:
            # Reduce max_tokens or message length
            kwargs['max_tokens'] = min(kwargs.get('max_tokens', 4000), 2000)
            return client.chat.completions.create(model=model, messages=messages, **kwargs)

        elif "rate limit" in error_msg:
            # Implement retry with backoff
            import time
            time.sleep(60)
            return client.chat.completions.create(model=model, messages=messages, **kwargs)

        else:
            raise
```

### 2. Cost Tracking

```python
def track_usage(response):
    """Track token usage and costs."""

    if hasattr(response, 'usage') and response.usage:
        usage = response.usage

        # Estimate cost (you'd get actual cost from IndoxRouter response headers)
        print(f"Tokens used: {usage.total_tokens}")
        print(f"  Prompt: {usage.prompt_tokens}")
        print(f"  Completion: {usage.completion_tokens}")

        # Note: Actual costs would be in IndoxRouter's response format
        # when using the native client, not available in OpenAI SDK format

# Usage
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)

track_usage(response)
```

### 3. Model Fallback

```python
def chat_with_fallback(messages, preferred_models, **kwargs):
    """Try multiple models as fallbacks."""

    for model in preferred_models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            print(f"✅ Success with {model}")
            return response

        except Exception as e:
            print(f"❌ Failed with {model}: {e}")
            continue

    raise Exception("All fallback models failed")

# Example usage
fallback_models = [
    "openai/gpt-4o",                      # Try premium first
    "openai/gpt-4o-mini",                 # Fallback to cheaper
    "anthropic/claude-3-sonnet-20240229", # Different provider
    "deepseek/deepseek-chat"              # Most economical
]

response = chat_with_fallback(
    messages=[{"role": "user", "content": "Complex analysis task"}],
    preferred_models=fallback_models,
    temperature=0.3,
    max_tokens=1000
)
```

This approach lets you use the familiar OpenAI SDK while getting access to all IndoxRouter providers and their cost tracking features!

_Last updated: Nov 08, 2025_