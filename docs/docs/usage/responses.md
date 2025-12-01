# Response Format

indoxhub provides detailed response information for every API call, including usage statistics, costs, and performance metrics. This helps you monitor and optimize your AI application usage.

## Standard Response Structure

Every indoxhub response follows this consistent format:

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
        'timestamp': '2025-05-19T06:07:38.065330',
        'cache_read_tokens': 0,
        'cache_write_tokens': 0,
        'reasoning_tokens': 0,
        'web_search_count': 0,
        'request_count': 1,
        'cost_breakdown': {
            'input_tokens': 0.000025,
            'output_tokens': 0.000204,
            'cache_read': 0.0,
            'cache_write': 0.0,
            'reasoning': 0.0,
            'web_search': 0.0,
            'request': 0.0
        }
    },
    'raw_response': None,
    'data': 'Your AI response content here...',
    'finish_reason': None,
    'images': None
}
```

## Response Fields

### Metadata Fields

| Field         | Type    | Description                                |
| ------------- | ------- | ------------------------------------------ |
| `request_id`  | string  | Unique identifier for this request         |
| `created_at`  | string  | ISO timestamp when request was processed   |
| `duration_ms` | float   | Total request duration in milliseconds     |
| `provider`    | string  | AI provider used (openai, anthropic, etc.) |
| `model`       | string  | Specific model used                        |
| `success`     | boolean | Whether the request succeeded              |
| `message`     | string  | Success message or additional info         |

### Usage Statistics

The `usage` object contains detailed usage and cost information:

| Field                | Type    | Description                             |
| -------------------- | ------- | --------------------------------------- |
| `tokens_prompt`      | integer | Tokens used in the input/prompt         |
| `tokens_completion`  | integer | Tokens generated in the response        |
| `tokens_total`       | integer | Total tokens used (prompt + completion) |
| `cost`               | float   | Total cost in USD for this request      |
| `latency`            | float   | Provider response time in seconds       |
| `timestamp`          | string  | ISO timestamp of the request            |
| `cache_read_tokens`  | integer | Tokens read from cache                  |
| `cache_write_tokens` | integer | Tokens written to cache                 |
| `reasoning_tokens`   | integer | Tokens used for internal reasoning      |
| `web_search_count`   | integer | Number of web searches performed        |
| `request_count`      | integer | Number of requests made (usually 1)     |
| `cost_breakdown`     | object  | Detailed cost breakdown by component    |

#### Cost Breakdown

The `cost_breakdown` object provides detailed cost information:

| Field           | Type  | Description                       |
| --------------- | ----- | --------------------------------- |
| `input_tokens`  | float | Cost for input/prompt tokens      |
| `output_tokens` | float | Cost for output/completion tokens |
| `cache_read`    | float | Cost for cache read operations    |
| `cache_write`   | float | Cost for cache write operations   |
| `reasoning`     | float | Cost for reasoning tokens         |
| `web_search`    | float | Cost for web search operations    |
| `request`       | float | Base request cost                 |

### Content Fields

| Field           | Type         | Description                                 |
| --------------- | ------------ | ------------------------------------------- |
| `data`          | string/array | The actual AI response content              |
| `finish_reason` | string       | Why the response ended (stop, length, etc.) |
| `images`        | array/null   | Generated images with URLs (null if none)   |
| `raw_response`  | object       | Original provider response (optional)       |

## Response Examples by Operation

### Chat Completion Response

```python
response = client.chat(
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    model="openai/gpt-4o-mini"
)

# Response structure:
{
    'request_id': 'b881942c-e21d-4f9d-ad82-47344945c642',
    'created_at': '2025-06-15T09:53:26.130868',
    'duration_ms': 1737.612247467041,
    'provider': 'openai',
    'model': 'gpt-4o-mini',
    'success': True,
    'message': '',
    'usage': {
        'tokens_prompt': 24,
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
        'cost_breakdown': {
            'input_tokens': 3.6e-06,
            'output_tokens': 4.2e-06,
            'cache_read': 0.0,
            'cache_write': 0.0,
            'reasoning': 0.0,
            'web_search': 0.0,
            'request': 0.0
        }
    },
    'raw_response': None,
    'data': 'The capital of France is Paris.',
    'finish_reason': None
}
```

### Text Completion Response

```python
response = client.completions(
    prompt="Tell me a story",
    model="openai/gpt-4o-mini",
    max_tokens=500
)

# Response structure:
{
    'request_id': '0fecd9af-0ba8-47a4-852f-029b3a5bfa18',
    'created_at': '2025-06-15T09:54:51.393591',
    'duration_ms': 6939.460754394531,
    'provider': 'openai',
    'model': 'gpt-4o-mini',
    'success': True,
    'message': '',
    'usage': {
        'tokens_prompt': 11,
        'tokens_completion': 530,
        'tokens_total': 541,
        'cost': 0.00031965,
        'latency': 6.794795513153076,
        'timestamp': '2025-06-15T09:54:51.362423',
        'cache_read_tokens': 0,
        'cache_write_tokens': 0,
        'reasoning_tokens': 0,
        'web_search_count': 0,
        'request_count': 1,
        'cost_breakdown': {
            'input_tokens': 1.6499999999999999e-06,
            'output_tokens': 0.000318,
            'cache_read': 0.0,
            'cache_write': 0.0,
            'reasoning': 0.0,
            'web_search': 0.0,
            'request': 0.0
        }
    },
    'raw_response': None,
    'data': 'Once upon a time, in a small village nestled between rolling hills and a sparkling river, there lived a young girl named Elara. She was known throughout the village for her kindness and her love for nature...',
    'finish_reason': None,
    'images': None
}
```

### Text Completion Response with Images

For models that support image generation (like `gemini-2.5-flash-image`), the response may include generated images:

```python
response = client.completions(
    prompt="Describe a cat and draw a picture of it",
    model="google/gemini-2.5-flash-image"
)

# Response structure:
{
    'request_id': '48c93623-286e-4e03-807b-938e53cb5076',
    'created_at': '2025-10-26T16:48:59.574195',
    'duration_ms': 10853.046178817749,
    'provider': 'google',
    'model': 'gemini-2.5-flash-image',
    'success': True,
    'message': '',
    'usage': {
        'tokens_prompt': 8,
        'tokens_completion': 1377,
        'tokens_total': 1385,
        'cost': 0.0034449000000000003,
        'latency': 9.228402614593506,
        'timestamp': '2025-10-26T16:48:58.009249',
        'cache_read_tokens': 0,
        'cache_write_tokens': 0,
        'reasoning_tokens': 0,
        'web_search_count': 0,
        'request_count': 1,
        'cost_breakdown': {
            'input_tokens': 2.4e-06,
            'output_tokens': 0.0034425000000000002,
            'cache_read': 0.0,
            'cache_write': 0.0,
            'reasoning': 0.0,
            'web_search': 0.0,
            'request': 0.0
        }
    },
    'raw_response': None,
    'data': 'A cat is a small, domesticated carnivorous mammal... Here\'s a drawing of a cat for you:',
    'finish_reason': 'STOP',
    'images': [
        {
            'url': 'https://indoxhub.s3.amazonaws.com/dev_user_4/image/d0847065-2f2b-4529-8484-0e98e19b7318_20251026_164858.png?...',
            'index': 0
        }
    ]
}
```

### Embedding Response

```python
response = client.embeddings(
    text="Hello world",
    model="openai/text-embedding-3-small"
)

# Response structure:
{
    'request_id': 'req_ghi789',
    'created_at': '2025-05-19T10:40:15.456789',
    'duration_ms': 456.78,
    'provider': 'openai',
    'model': 'text-embedding-3-small',
    'success': True,
    'message': '',
    'usage': {
        'tokens_prompt': 2,
        'tokens_completion': 0,
        'tokens_total': 2,
        'cost': 0.000001,
        'latency': 0.3,
        'timestamp': '2025-05-19T10:40:15.400000'
    },
    'data': [
        [0.123, -0.456, 0.789, ...]  # 1536-dimensional vector
    ],
    'dimensions': 1536
}
```

### Image Generation Response

```python
response = client.images(
    prompt="A beautiful sunset over the ocean",
    model="openai/dall-e-3",
    size="1024x1024"
)

# Response structure:
{
    'request_id': '0bc89954-f5cc-4efc-a055-4e5624aa2a81',
    'created_at': '2025-05-29T11:39:24.621706',
    'duration_ms': 12340.412378311157,
    'provider': 'openai',
    'model': 'dall-e-3',
    'success': True,
    'message': '',
    'usage': {
        'tokens_prompt': 0,
        'tokens_completion': 0,
        'tokens_total': 0,
        'cost': 0.016,
        'latency': 12.240789651870728,
        'timestamp': '2025-05-29T11:39:24.612377',
        'cache_read_tokens': 0,
        'cache_write_tokens': 0,
        'reasoning_tokens': 0,
        'web_search_count': 0,
        'request_count': 1,
        'cost_breakdown': None
    },
    'raw_response': None,
    'data': [
        {
            'url': 'https://....image_12345.jpg',
            'revised_prompt': 'A beautiful sunset over the ocean with golden clouds...'
        }
    ]
}
```

## Working with Responses

### Accessing Response Data

```python
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4o-mini"
)

# Get the AI response text
content = response['data']
print(content)

# Get usage information
usage = response['usage']
print(f"Tokens used: {usage['tokens_total']}")
print(f"Cost: ${usage['cost']:.6f}")
print(f"Latency: {usage['latency']:.2f}s")

# Get detailed cost breakdown
if usage['cost_breakdown']:
    breakdown = usage['cost_breakdown']
    print(f"Input token cost: ${breakdown['input_tokens']:.6f}")
    print(f"Output token cost: ${breakdown['output_tokens']:.6f}")
    print(f"Cache read cost: ${breakdown['cache_read']:.6f}")

# Get metadata
print(f"Provider: {response['provider']}")
print(f"Model: {response['model']}")
print(f"Request ID: {response['request_id']}")
```

### Handling Image Responses

```python
response = client.images(
    prompt="A beautiful sunset",
    model="openai/dall-e-3",
    size="1024x1024"
)

# Get image URL
if response['data']:
    image_url = response['data'][0]['url']
    print(f"Image URL: {image_url}")

    # Download and display the image
    import requests
    from PIL import Image
    from io import BytesIO

    img_response = requests.get(image_url)
    img = Image.open(BytesIO(img_response.content))
    img.show()  # Or save: img.save("generated_image.png")

    # Optional: Get revised prompt if available
    if 'revised_prompt' in response['data'][0]:
        print(f"Revised prompt: {response['data'][0]['revised_prompt']}")
```

### Handling Images in Text Completions

For text completion models that can generate images (like Gemini models), check for the `images` field:

```python
response = client.completions(
    prompt="Describe a sunset and create an image",
    model="google/gemini-2.5-flash-image"
)

# Check if images were generated
if response['images'] and len(response['images']) > 0:
    print(f"Generated {len(response['images'])} image(s)")

    for image in response['images']:
        image_url = image['url']
        image_index = image['index']
        print(f"Image {image_index}: {image_url}")

        # Download and save the image
        import requests

        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            filename = f"generated_image_{image_index}.png"
            with open(filename, 'wb') as f:
                f.write(img_response.content)
            print(f"Saved image to {filename}")
else:
    print("No images were generated in this response")

# The text content is still available in response['data']
print(f"Text response: {response['data']}")
```

### Cost Tracking

```python
def track_costs(response):
    """Extract and log cost information from response."""
    usage = response['usage']

    print(f"Request Cost Breakdown:")
    print(f"  Model: {response['provider']}/{response['model']}")
    print(f"  Prompt tokens: {usage['tokens_prompt']}")
    print(f"  Completion tokens: {usage['tokens_completion']}")
    print(f"  Total tokens: {usage['tokens_total']}")
    print(f"  Cost: ${usage['cost']:.6f}")
    print(f"  Latency: {usage['latency']:.2f}s")

    return usage['cost']

# Use with any request
response = client.chat(messages=[...], model="openai/gpt-4o")
cost = track_costs(response)
```

### Performance Monitoring

```python
def analyze_performance(response):
    """Analyze request performance metrics."""
    duration = response['duration_ms']
    latency = response['usage']['latency'] * 1000  # Convert to ms

    # Network + processing overhead
    overhead = duration - latency

    print(f"Performance Analysis:")
    print(f"  Total duration: {duration:.2f}ms")
    print(f"  Provider latency: {latency:.2f}ms")
    print(f"  Network overhead: {overhead:.2f}ms")

    if overhead > 1000:  # > 1 second overhead
        print("  ⚠️  High network overhead detected")

    return {
        'total_duration': duration,
        'provider_latency': latency,
        'overhead': overhead
    }
```

## Error Responses

When an error occurs, the response format changes:

```python
{
    'success': False,
    'error': 'ModelNotFoundError',
    'message': 'Model "gpt-5" not found for provider "openai"',
    'status_code': 404,
    'request_id': 'req_error123',
    'details': {
        'provider': 'openai',
        'requested_model': 'gpt-5',
        'available_models': ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo']
    }
}
```

### Handling Error Responses

```python
try:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="invalid/model"
    )

    if response['success']:
        print(response['data'])
    else:
        print(f"Error: {response['error']}")
        print(f"Message: {response['message']}")

        # Get suggested alternatives
        if 'details' in response and 'available_models' in response['details']:
            print("Available models:", response['details']['available_models'])

except Exception as e:
    print(f"Request failed: {e}")
```

## Streaming Responses

For streaming requests, responses come in chunks:

```python
response_stream = client.chat(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="openai/gpt-4o-mini",
    stream=True
)

full_response = ""
total_cost = 0

for chunk in response_stream:
    if chunk['success']:
        # Accumulate the response
        full_response += chunk['data']

        # Track costs (final chunk has complete usage info)
        if 'usage' in chunk:
            total_cost = chunk['usage']['cost']

        print(chunk['data'], end='', flush=True)

print(f"\n\nTotal cost: ${total_cost:.6f}")
```

## Response Validation

```python
def validate_response(response):
    """Validate indoxhub response format."""
    required_fields = ['request_id', 'success', 'provider', 'model']

    for field in required_fields:
        if field not in response:
            raise ValueError(f"Missing required field: {field}")

    if response['success']:
        if 'data' not in response:
            raise ValueError("Success response missing 'data' field")
        if 'usage' not in response:
            raise ValueError("Success response missing 'usage' field")
    else:
        if 'error' not in response:
            raise ValueError("Error response missing 'error' field")

    return True

# Use with responses
response = client.chat(messages=[...], model="openai/gpt-4o-mini")
if validate_response(response):
    print("Response format is valid")
```

## Best Practices

### 1. Always Check Success Status

```python
response = client.chat(messages=[...], model="openai/gpt-4o-mini")

if response['success']:
    content = response['data']
    cost = response['usage']['cost']
    # Process successful response
else:
    error = response['error']
    message = response['message']
    # Handle error
```

### 2. Monitor Costs

```python
# Set up cost alerts
def check_cost_threshold(response, max_cost=0.01):
    """Alert if single request exceeds cost threshold."""
    cost = response['usage']['cost']
    if cost > max_cost:
        print(f"⚠️  High cost request: ${cost:.4f}")
        print(f"   Model: {response['provider']}/{response['model']}")
        print(f"   Tokens: {response['usage']['tokens_total']}")

    return cost

response = client.chat(messages=[...], model="openai/gpt-4o")
check_cost_threshold(response)
```

### 3. Track Performance

```python
# Performance monitoring
def log_performance(response):
    """Log performance metrics for monitoring."""
    metrics = {
        'request_id': response['request_id'],
        'model': f"{response['provider']}/{response['model']}",
        'duration_ms': response['duration_ms'],
        'latency_ms': response['usage']['latency'] * 1000,
        'tokens': response['usage']['tokens_total'],
        'cost': response['usage']['cost']
    }

    # Log to your monitoring system
    print(f"METRICS: {metrics}")

    return metrics
```

### 4. Store Request IDs

```python
# For debugging and support
def save_request_info(response, query_description):
    """Save request information for debugging."""
    info = {
        'timestamp': response['created_at'],
        'request_id': response['request_id'],
        'description': query_description,
        'model': f"{response['provider']}/{response['model']}",
        'success': response['success'],
        'cost': response.get('usage', {}).get('cost', 0)
    }

    # Save to logs or database
    print(f"REQUEST_LOG: {info}")

    return info

response = client.chat(messages=[...], model="openai/gpt-4o-mini")
save_request_info(response, "User greeting response")
```

_Last updated: Nov 16, 2025_