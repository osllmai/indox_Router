# Response Format

indoxhub provides detailed response information for every API call, including usage statistics, costs, and performance metrics. This helps you monitor and optimize your AI application usage.

## Standard Response Structure

!!! note "Response Format Differences"
**Chat and Completions endpoints** use an OpenAI-compatible format with an `output` array. All other endpoints (embeddings, images, audio, etc.) use the standard format below with a `data` field.

Most indoxhub endpoints follow this consistent format:

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

**Chat and Completions endpoints** use an OpenAI-compatible format. See the [Chat Completion Response](#chat-completion-response) and [Text Completion Response](#text-completion-response) sections below for details.

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

# Response structure (OpenAI-compatible format):
{
    'id': 'b881942c-e21d-4f9d-ad82-47344945c642',
    'object': 'response',
    'created_at': 1718456006,
    'model': 'gpt-4o-mini',
    'provider': 'openai',
    'duration_ms': 1737.61,
    'output': [
        {
            'type': 'message',
            'status': 'completed',
            'role': 'assistant',
            'content': [
                {
                    'type': 'output_text',
                    'text': 'The capital of France is Paris.',
                    'annotations': []
                }
            ]
        }
    ],
    'usage': {
        'input_tokens': 24,
        'input_tokens_details': {'cached_tokens': 0},
        'output_tokens': 7,
        'output_tokens_details': {'reasoning_tokens': 0},
        'total_tokens': 31
    },
    'status': 'completed'
}
```

### Text Completion Response

```python
response = client.completions(
    prompt="Tell me a story",
    model="openai/gpt-3.5-turbo-instruct",
    max_tokens=500
)

# Response structure (OpenAI-compatible format):
{
    'id': '0fecd9af-0ba8-47a4-852f-029b3a5bfa18',
    'object': 'response',
    'created_at': 1718456091,
    'model': 'gpt-3.5-turbo-instruct',
    'provider': 'openai',
    'duration_ms': 6939.46,
    'output': [
        {
            'type': 'message',
            'status': 'completed',
            'role': 'assistant',
            'content': [
                {
                    'type': 'output_text',
                    'text': 'Once upon a time, in a small village nestled between rolling hills and a sparkling river, there lived a young girl named Elara. She was known throughout the village for her kindness and her love for nature...',
                    'annotations': []
                }
            ]
        }
    ],
    'usage': {
        'input_tokens': 11,
        'input_tokens_details': {'cached_tokens': 0},
        'output_tokens': 530,
        'output_tokens_details': {'reasoning_tokens': 0},
        'total_tokens': 541
    },
    'status': 'completed'
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

For chat and completion responses (OpenAI-compatible format):

```python
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4o-mini"
)

# Get the AI response text from the output array
content = response['output'][0]['content'][0]['text']
print(content)

# Get usage information
usage = response['usage']
print(f"Input tokens: {usage['input_tokens']}")
print(f"Output tokens: {usage['output_tokens']}")
print(f"Total tokens: {usage['total_tokens']}")

# Get cached tokens if available
if 'input_tokens_details' in usage:
    cached = usage['input_tokens_details'].get('cached_tokens', 0)
    print(f"Cached tokens: {cached}")

# Get reasoning tokens if available
if 'output_tokens_details' in usage:
    reasoning = usage['output_tokens_details'].get('reasoning_tokens', 0)
    if reasoning > 0:
        print(f"Reasoning tokens: {reasoning}")

# Check for reasoning content in the message (for reasoning-capable models)
if 'reasoning' in response['output'][0]:
    reasoning_text = response['output'][0]['reasoning']
    print(f"Reasoning: {reasoning_text}")

# Get metadata
print(f"Provider: {response['provider']}")
print(f"Model: {response['model']}")
print(f"Request ID: {response['id']}")
print(f"Status: {response['status']}")
```

For other endpoints (embeddings, images, etc.), the response format remains unchanged with `response['data']`:

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

# The text content is available in response['output'][0]['content'][0]['text']
print(f"Text response: {response['output'][0]['content'][0]['text']}")
```

### Cost Tracking

```python
def track_usage(response):
    """Extract and log usage information from response."""
    usage = response['usage']

    print(f"Request Usage Breakdown:")
    print(f"  Model: {response['provider']}/{response['model']}")
    print(f"  Input tokens: {usage['input_tokens']}")
    print(f"  Output tokens: {usage['output_tokens']}")
    print(f"  Total tokens: {usage['total_tokens']}")

    # Check for cached tokens
    if 'input_tokens_details' in usage:
        cached = usage['input_tokens_details'].get('cached_tokens', 0)
        if cached > 0:
            print(f"  Cached tokens: {cached}")

    # Check for reasoning tokens
    if 'output_tokens_details' in usage:
        reasoning = usage['output_tokens_details'].get('reasoning_tokens', 0)
        if reasoning > 0:
            print(f"  Reasoning tokens: {reasoning}")

    # Note: Cost information is not included in individual response usage objects.
    # Use client.get_usage() to get cost statistics.

    return usage['total_tokens']

# Use with any request
response = client.chat(messages=[...], model="openai/gpt-4o")
total_tokens = track_usage(response)
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

    # For chat/completion responses (OpenAI-compatible format)
    if response.get('status') == 'completed':
        print(response['output'][0]['content'][0]['text'])
    elif response.get('error'):
        print(f"Error: {response['error']}")
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")

        # Get suggested alternatives
        if 'details' in response and 'available_models' in response['details']:
            print("Available models:", response['details']['available_models'])

except Exception as e:
    print(f"Request failed: {e}")
```

## Streaming Responses

For streaming requests, responses use an event-based format compatible with OpenAI's new streaming API. The stream uses Server-Sent Events (SSE) format where each event is prefixed with `data: ` and ends with `\n\n`.

### Basic Streaming Example

```python
import json

response_stream = client.chat(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="openai/gpt-4o-mini",
    stream=True
)

full_response = ""
total_tokens = 0

for chunk in response_stream:
    # Parse the chunk (it's a JSON string in SSE format)
    if chunk.startswith("data: "):
        data = chunk[6:]  # Remove "data: " prefix
        if data.strip() == "[DONE]":
            break

        try:
            event = json.loads(data)
            event_type = event.get("type")

            # Handle response creation
            if event_type == "response.created":
                print("Response started...")

            # Handle content deltas (text chunks)
            elif event_type == "response.content_part.delta":
                delta = event.get("delta", "")
                full_response += delta
                print(delta, end='', flush=True)

            # Handle final response with usage
            elif event_type == "response.done":
                usage = event.get("response", {}).get("usage", {})
                total_tokens = usage.get("total_tokens", 0)
                print(f"\n\nTotal tokens: {total_tokens}")

        except json.JSONDecodeError:
            pass

print(f"\n\nFull response: {full_response}")
```

### Streaming Event Types and Structures

The streaming API emits the following event types in sequence. Each event is a JSON object sent as a Server-Sent Event (SSE) with the format `data: <json>\n\n`.

#### 1. response.created

Sent first when the response is created.

```json
{
  "type": "response.created",
  "response": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "object": "response",
    "status": "in_progress",
    "model": "gpt-4o-mini"
  }
}
```

#### 2. response.reasoning.started

Sent when reasoning phase starts (for reasoning-capable models like OpenAI o1, o3).

```json
{
  "type": "response.reasoning.started",
  "response_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 3. response.reasoning.delta

Sent for each chunk of reasoning content (streamed before the main response).

```json
{
  "type": "response.reasoning.delta",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "delta": "Let me think about this step by step..."
}
```

#### 4. response.output_item.added

Sent when a new output item (message) is added to the response.

```json
{
  "type": "response.output_item.added",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 0,
  "item": {
    "type": "message",
    "role": "assistant",
    "status": "in_progress",
    "content": []
  }
}
```

#### 5. response.content_part.added

Sent when a new content part is added to the output item.

```json
{
  "type": "response.content_part.added",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 0,
  "content_index": 0,
  "part": {
    "type": "output_text",
    "text": ""
  }
}
```

#### 6. response.content_part.delta

Sent for each chunk of text content (main streaming content). This is the primary event for receiving the response text.

```json
{
  "type": "response.content_part.delta",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 0,
  "content_index": 0,
  "delta": "Once upon a time..."
}
```

#### 7. response.output_item.done

Sent when an output item is completed.

```json
{
  "type": "response.output_item.done",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 0,
  "item": {
    "type": "message",
    "role": "assistant",
    "status": "completed",
    "content": [
      {
        "type": "output_text",
        "text": "Once upon a time, in a land far away...",
        "annotations": []
      }
    ],
    "reasoning": "Optional reasoning content for reasoning-capable models"
  }
}
```

#### 8. response.image_generation_call.* Events

For models that generate images, these events are emitted:

**response.image_generation_call.in_progress** - Image generation started:
```json
{
  "type": "response.image_generation_call.in_progress",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 1,
  "image_generation_call": {
    "id": "img_call_abc123...",
    "type": "image_generation_call",
    "status": "in_progress"
  }
}
```

**response.image_generation_call.generating** - Image generation in progress:
```json
{
  "type": "response.image_generation_call.generating",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 1
}
```

**response.image_generation_call.partial_image** - Partial image data (base64):
```json
{
  "type": "response.image_generation_call.partial_image",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 1,
  "partial_image_b64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**response.image_generation_call.completed** - Image generation completed (with URL):
```json
{
  "type": "response.image_generation_call.completed",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 1,
  "image_generation_call": {
    "id": "img_call_abc123...",
    "type": "image_generation_call",
    "status": "completed",
    "url": "https://example.com/image.png"
  }
}
```

**response.image_generation_call.completed** - Image generation completed (with base64 data):
```json
{
  "type": "response.image_generation_call.completed",
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_index": 1,
  "image_generation_call": {
    "id": "img_call_abc123...",
    "type": "image_generation_call",
    "status": "completed"
  },
  "data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### 9. response.done

Sent last with final usage statistics.

```json
{
  "type": "response.done",
  "response": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "object": "response",
    "status": "completed",
    "usage": {
      "input_tokens": 24,
      "input_tokens_details": {
        "cached_tokens": 0
      },
      "output_tokens": 107,
      "output_tokens_details": {
        "reasoning_tokens": 0
      },
      "total_tokens": 131
    }
  }
}
```

#### 10. [DONE]

Plain text marker (not JSON) indicating the end of the stream:
```
data: [DONE]\n\n
```

### Complete Streaming Flow Example

Here's a complete example handling all event types:

```python
import json

def stream_chat_complete(client, messages, model):
    """Complete streaming handler with all event types."""
    full_text = ""
    reasoning_text = ""
    images = []
    usage_info = None
    
    for chunk in client.chat(messages=messages, model=model, stream=True):
        if chunk.startswith("data: "):
            data = chunk[6:]
            if data.strip() == "[DONE]":
                break
            
            try:
                event = json.loads(data)
                event_type = event.get("type")
                
                # Track response creation
                if event_type == "response.created":
                    response_id = event.get("response", {}).get("id")
                    print(f"Response ID: {response_id}")
                
                # Handle reasoning (for reasoning models)
                elif event_type == "response.reasoning.started":
                    print("\n[Reasoning phase]")
                    reasoning_text = ""
                
                elif event_type == "response.reasoning.delta":
                    delta = event.get("delta", "")
                    reasoning_text += delta
                
                # Handle output items
                elif event_type == "response.output_item.added":
                    item_type = event.get("item", {}).get("type")
                    print(f"\n[{item_type} item added]")
                
                # Handle content parts
                elif event_type == "response.content_part.added":
                    part_type = event.get("part", {}).get("type")
                    print(f"[{part_type} part added]")
                
                elif event_type == "response.content_part.delta":
                    delta = event.get("delta", "")
                    full_text += delta
                    print(delta, end="", flush=True)
                
                elif event_type == "response.output_item.done":
                    item = event.get("item", {})
                    if "reasoning" in item:
                        reasoning_text = item["reasoning"]
                    print("\n[Item completed]")
                
                # Handle image generation
                elif event_type == "response.image_generation_call.in_progress":
                    call_id = event.get("image_generation_call", {}).get("id")
                    print(f"\n[Image generation started: {call_id}]")
                
                elif event_type == "response.image_generation_call.completed":
                    image_call = event.get("image_generation_call", {})
                    if "url" in image_call:
                        images.append({"url": image_call["url"]})
                        print(f"\n[Image completed: {image_call['url']}]")
                    elif "data" in event:
                        images.append({"data": event["data"]})
                        print("\n[Image completed: base64 data]")
                
                # Handle final usage
                elif event_type == "response.done":
                    usage_info = event.get("response", {}).get("usage", {})
                    print(f"\n\n[Stream completed]")
                    print(f"Total tokens: {usage_info.get('total_tokens', 0)}")
            
            except json.JSONDecodeError:
                pass
    
    return {
        "text": full_text,
        "reasoning": reasoning_text,
        "images": images,
        "usage": usage_info
    }

# Usage
result = stream_chat_complete(
    client=client,
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="openai/gpt-4o-mini"
)
```

### Streaming with Reasoning Models

For reasoning-capable models (like OpenAI o1, o3), reasoning content streams before the main response:

```python
import json

reasoning_chunks = []
text_chunks = []

for chunk in client.chat(
    messages=[{"role": "user", "content": "Solve this step by step"}],
    model="openai/o1-preview",
    stream=True
):
    if chunk.startswith("data: "):
        data = chunk[6:]
        if data.strip() == "[DONE]":
            break
        
        try:
            event = json.loads(data)
            event_type = event.get("type")
            
            if event_type == "response.reasoning.started":
                print("\n[Model reasoning...]")
                reasoning_chunks = []
            
            elif event_type == "response.reasoning.delta":
                delta = event.get("delta", "")
                reasoning_chunks.append(delta)
                # Optionally show reasoning
                print(delta, end="", flush=True)
            
            elif event_type == "response.content_part.delta":
                delta = event.get("delta", "")
                text_chunks.append(delta)
                print(delta, end="", flush=True)
        
        except json.JSONDecodeError:
            pass

full_reasoning = "".join(reasoning_chunks)
full_text = "".join(text_chunks)
```

### Streaming with Image Generation

For models that generate images (like some Gemini models):

```python
import json
import base64
import requests

images = []
text_chunks = []

for chunk in client.chat(
    messages=[{"role": "user", "content": "Describe and draw a cat"}],
    model="google/gemini-2.5-flash-image",
    stream=True
):
    if chunk.startswith("data: "):
        data = chunk[6:]
        if data.strip() == "[DONE]":
            break
        
        try:
            event = json.loads(data)
            event_type = event.get("type")
            
            if event_type == "response.image_generation_call.in_progress":
                print("\n[Generating image...]")
            
            elif event_type == "response.image_generation_call.completed":
                image_call = event.get("image_generation_call", {})
                if "url" in image_call:
                    images.append({"url": image_call["url"]})
                    print(f"\n[Image ready: {image_call['url']}]")
                elif "data" in event:
                    images.append({"data": event["data"]})
                    print("\n[Image ready: base64 data]")
            
            elif event_type == "response.content_part.delta":
                delta = event.get("delta", "")
                text_chunks.append(delta)
                print(delta, end="", flush=True)
        
        except json.JSONDecodeError:
            pass

# Save images
for i, img in enumerate(images):
    if "url" in img:
        response = requests.get(img["url"])
        with open(f"image_{i}.png", "wb") as f:
            f.write(response.content)
    elif "data" in img:
        with open(f"image_{i}.png", "wb") as f:
            f.write(base64.b64decode(img["data"]))
```

### Event Flow Sequence

The typical event flow for a streaming response is:

1. `response.created` - Response initialization
2. `response.reasoning.started` (optional) - If reasoning model
3. `response.reasoning.delta` (multiple, optional) - Reasoning chunks
4. `response.output_item.added` - Message item added
5. `response.content_part.added` - Content part added
6. `response.content_part.delta` (multiple) - Text chunks
7. `response.output_item.done` - Message completed
8. `response.image_generation_call.*` (optional) - If images generated
9. `response.done` - Final usage statistics
10. `[DONE]` - Stream end marker

## Response Validation

```python
def validate_response(response):
    """Validate indoxhub response format."""
    required_fields = ['request_id', 'success', 'provider', 'model']

    for field in required_fields:
        if field not in response:
            raise ValueError(f"Missing required field: {field}")

    # For chat/completion responses (OpenAI-compatible format)
    if response.get('object') == 'response':
        if 'output' not in response:
            raise ValueError("Response missing 'output' field")
        if 'usage' not in response:
            raise ValueError("Response missing 'usage' field")
    # For other endpoints, check for 'data' field
    elif 'data' not in response and 'error' not in response:
        raise ValueError("Response missing 'data' or 'error' field")

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

# For chat/completion responses (OpenAI-compatible format)
if response['status'] == 'completed':
    content = response['output'][0]['content'][0]['text']
    usage = response['usage']
    # Note: Cost information is not in the response usage object.
    # Use client.get_usage() to get cost statistics.
    # Process successful response
elif response.get('error'):
    error = response['error']
    # Handle error
```

### 2. Monitor Usage and Costs

```python
# Monitor token usage from responses
def check_token_usage(response, max_tokens=10000):
    """Alert if single request exceeds token threshold."""
    usage = response['usage']
    total_tokens = usage['total_tokens']
    if total_tokens > max_tokens:
        print(f"⚠️  High token usage: {total_tokens} tokens")
        print(f"   Model: {response['provider']}/{response['model']}")
        print(f"   Input tokens: {usage['input_tokens']}")
        print(f"   Output tokens: {usage['output_tokens']}")

    return total_tokens

response = client.chat(messages=[...], model="openai/gpt-4o")
check_token_usage(response)

# For cost monitoring, use get_usage()
def check_cost_threshold(client, max_cost=50.0):
    """Alert if total usage cost exceeds threshold."""
    usage = client.get_usage()
    total_cost = usage['total_cost']
    if total_cost > max_cost:
        print(f"⚠️  High total cost: ${total_cost:.2f}")
        print(f"   Remaining credits: ${usage['remaining_credits']:.2f}")

    return total_cost

check_cost_threshold(client)
```

### 3. Track Performance

```python
# Performance monitoring
def log_performance(response):
    """Log performance metrics for monitoring."""
    metrics = {
        'request_id': response['id'],
        'model': f"{response['provider']}/{response['model']}",
        'duration_ms': response['duration_ms'],
        'tokens': response['usage']['total_tokens'],
        'input_tokens': response['usage']['input_tokens'],
        'output_tokens': response['usage']['output_tokens']
    }

    # Note: Cost information is not in the response usage object.
    # Use client.get_usage() to get cost statistics.

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
        'timestamp': response.get('created_at'),
        'request_id': response.get('id'),
        'description': query_description,
        'model': f"{response['provider']}/{response['model']}",
        'status': response.get('status'),
        'tokens': response.get('usage', {}).get('total_tokens', 0)
    }

    # Note: Cost information is not in the response.
    # Use client.get_usage() to get cost statistics.

    # Save to logs or database
    print(f"REQUEST_LOG: {info}")

    return info

response = client.chat(messages=[...], model="openai/gpt-4o-mini")
save_request_info(response, "User greeting response")
```

_Last updated: Nov 16, 2025_
