# Chat Completions

Chat completions are the primary way to interact with conversational AI models like GPT-4, Claude, and Gemini. This guide covers how to use the chat completions feature of the indoxhub Client.

## Basic Usage

The simplest way to use chat completions is with the `chat()` method:

```python
from indoxhub import Client

client = Client(api_key="your_api_key")

response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke about programming."}
    ],
    model="openai/gpt-4o-mini"
)

# Access the response text from the output array
print(response["output"][0]["content"][0]["text"])
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

indoxhub supports BYOK, allowing you to use your own API keys for AI providers. This bypasses platform rate limits and credit deductions:

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

- **No Credit Deduction**: Your indoxhub credits remain unchanged
- **No Rate Limiting**: Bypass platform rate limits
- **Direct Provider Access**: Connect directly to your provider accounts
- **Cost Control**: Pay providers directly at their rates
- **Full Features**: Access to all provider-specific chat features

## Streaming Responses

For long responses, you might want to stream the response to get it piece by piece. Streaming uses an event-based format compatible with OpenAI's new streaming API with Server-Sent Events (SSE).

### Basic Streaming Example

```python
import json

print("Streaming response:")
for chunk in client.chat(
    messages=[
        {"role": "user", "content": "Tell me a story about a robot in 5 sentences."}
    ],
    model="mistral/ministral-8b-latest",
    stream=True
):
    # Parse the chunk (it's a JSON string in SSE format)
    if chunk.startswith("data: "):
        data = chunk[6:]  # Remove "data: " prefix
        if data.strip() == "[DONE]":
            break

        try:
            event = json.loads(data)
            event_type = event.get("type")

            # Handle content deltas
            if event_type == "response.content_part.delta":
                delta = event.get("delta", "")
                print(delta, end="", flush=True)

            # Handle final response with usage
            elif event_type == "response.done":
                usage = event.get("response", {}).get("usage", {})
                print(f"\n\nTotal tokens: {usage.get('total_tokens', 0)}")

        except json.JSONDecodeError:
            pass

print("\nStreaming complete!")
```

### Complete Streaming Example with All Event Types

Here's a comprehensive example that handles all streaming event types:

```python
import json

def handle_streaming_response(client, messages, model):
    """Handle streaming response with all event types."""
    full_text = ""
    reasoning_text = ""
    usage_info = None

    for chunk in client.chat(messages=messages, model=model, stream=True):
        if chunk.startswith("data: "):
            data = chunk[6:]  # Remove "data: " prefix
            if data.strip() == "[DONE]":
                break

            try:
                event = json.loads(data)
                event_type = event.get("type")

                # Response creation
                if event_type == "response.created":
                    response_id = event.get("response", {}).get("id")
                    print(f"Response started: {response_id}")

                # Reasoning events (for reasoning-capable models like o1, o3)
                elif event_type == "response.reasoning.started":
                    print("\n[Reasoning phase started]")
                    reasoning_text = ""

                elif event_type == "response.reasoning.delta":
                    delta = event.get("delta", "")
                    reasoning_text += delta
                    # Optionally display reasoning as it streams
                    # print(delta, end="", flush=True)

                # Output item events
                elif event_type == "response.output_item.added":
                    output_index = event.get("output_index", 0)
                    item = event.get("item", {})
                    print(f"\n[Output item {output_index} added: {item.get('type')}]")

                # Content part events
                elif event_type == "response.content_part.added":
                    output_index = event.get("output_index", 0)
                    content_index = event.get("content_index", 0)
                    part = event.get("part", {})
                    print(f"[Content part {content_index} added: {part.get('type')}]")

                elif event_type == "response.content_part.delta":
                    delta = event.get("delta", "")
                    full_text += delta
                    print(delta, end="", flush=True)

                elif event_type == "response.output_item.done":
                    output_index = event.get("output_index", 0)
                    item = event.get("item", {})
                    if "reasoning" in item:
                        reasoning_text = item["reasoning"]
                    print(f"\n[Output item {output_index} completed]")

                # Image generation events
                elif event_type == "response.image_generation_call.in_progress":
                    output_index = event.get("output_index", 0)
                    call_id = event.get("image_generation_call", {}).get("id")
                    print(f"\n[Image generation {output_index} started: {call_id}]")

                elif event_type == "response.image_generation_call.generating":
                    output_index = event.get("output_index", 0)
                    print(f"[Image generation {output_index} in progress...]")

                elif event_type == "response.image_generation_call.partial_image":
                    output_index = event.get("output_index", 0)
                    # Partial base64 image data available
                    print(f"[Image {output_index} partial data received]")

                elif event_type == "response.image_generation_call.completed":
                    output_index = event.get("output_index", 0)
                    image_call = event.get("image_generation_call", {})
                    if "url" in image_call:
                        print(f"\n[Image {output_index} completed: {image_call['url']}]")
                    elif "data" in event:
                        print(f"\n[Image {output_index} completed: base64 data received]")

                # Final response with usage
                elif event_type == "response.done":
                    response_data = event.get("response", {})
                    usage_info = response_data.get("usage", {})
                    print(f"\n\n[Response completed]")
                    print(f"Total tokens: {usage_info.get('total_tokens', 0)}")
                    print(f"Input tokens: {usage_info.get('input_tokens', 0)}")
                    print(f"Output tokens: {usage_info.get('output_tokens', 0)}")
                    if usage_info.get("input_tokens_details", {}).get("cached_tokens", 0) > 0:
                        print(f"Cached tokens: {usage_info['input_tokens_details']['cached_tokens']}")
                    if usage_info.get("output_tokens_details", {}).get("reasoning_tokens", 0) > 0:
                        print(f"Reasoning tokens: {usage_info['output_tokens_details']['reasoning_tokens']}")

            except json.JSONDecodeError:
                pass

    return {
        "text": full_text,
        "reasoning": reasoning_text,
        "usage": usage_info
    }

# Use the handler
result = handle_streaming_response(
    client=client,
    messages=[{"role": "user", "content": "Tell me a story about a robot."}],
    model="openai/gpt-4o-mini"
)

print(f"\n\nFull response: {result['text']}")
if result['reasoning']:
    print(f"\nReasoning: {result['reasoning']}")
```

### Streaming Event Types

The streaming API emits the following event types in order:

1. **`response.created`** - Response creation event (sent first)

   ```json
   {
     "type": "response.created",
     "response": {
       "id": "request-id",
       "object": "response",
       "status": "in_progress",
       "model": "model-name"
     }
   }
   ```

2. **`response.reasoning.started`** - Reasoning phase started (for reasoning-capable models)

   ```json
   {
     "type": "response.reasoning.started",
     "response_id": "request-id"
   }
   ```

3. **`response.reasoning.delta`** - Reasoning content deltas (streamed chunks)

   ```json
   {
     "type": "response.reasoning.delta",
     "response_id": "request-id",
     "delta": "reasoning text chunk"
   }
   ```

4. **`response.output_item.added`** - Message output item added

   ```json
   {
     "type": "response.output_item.added",
     "response_id": "request-id",
     "output_index": 0,
     "item": {
       "type": "message",
       "role": "assistant",
       "status": "in_progress",
       "content": []
     }
   }
   ```

5. **`response.content_part.added`** - Content part added

   ```json
   {
     "type": "response.content_part.added",
     "response_id": "request-id",
     "output_index": 0,
     "content_index": 0,
     "part": {
       "type": "output_text",
       "text": ""
     }
   }
   ```

6. **`response.content_part.delta`** - Text content deltas (main streaming content)

   ```json
   {
     "type": "response.content_part.delta",
     "response_id": "request-id",
     "output_index": 0,
     "content_index": 0,
     "delta": "text chunk"
   }
   ```

7. **`response.output_item.done`** - Output item completed

   ```json
   {
     "type": "response.output_item.done",
     "response_id": "request-id",
     "output_index": 0,
     "item": {
       "type": "message",
       "role": "assistant",
       "status": "completed",
       "content": [
         {
           "type": "output_text",
           "text": "full text",
           "annotations": []
         }
       ],
       "reasoning": "optional reasoning content"
     }
   }
   ```

8. **`response.image_generation_call.*`** - Image generation events (if images are generated)

   **`response.image_generation_call.in_progress`** - Image generation started:

   ```json
   {
     "type": "response.image_generation_call.in_progress",
     "response_id": "request-id",
     "output_index": 1,
     "image_generation_call": {
       "id": "img_call_abc123...",
       "type": "image_generation_call",
       "status": "in_progress"
     }
   }
   ```

   **`response.image_generation_call.generating`** - Image generation in progress:

   ```json
   {
     "type": "response.image_generation_call.generating",
     "response_id": "request-id",
     "output_index": 1
   }
   ```

   **`response.image_generation_call.partial_image`** - Partial image data (base64):

   ```json
   {
     "type": "response.image_generation_call.partial_image",
     "response_id": "request-id",
     "output_index": 1,
     "partial_image_b64": "iVBORw0KGgoAAAANSUhEUgAA..."
   }
   ```

   **`response.image_generation_call.completed`** - Image generation completed (with URL):

   ```json
   {
     "type": "response.image_generation_call.completed",
     "response_id": "request-id",
     "output_index": 1,
     "image_generation_call": {
       "id": "img_call_abc123...",
       "type": "image_generation_call",
       "status": "completed",
       "url": "https://example.com/image.png"
     }
   }
   ```

   **`response.image_generation_call.completed`** - Image generation completed (with base64 data):

   ```json
   {
     "type": "response.image_generation_call.completed",
     "response_id": "request-id",
     "output_index": 1,
     "image_generation_call": {
       "id": "img_call_abc123...",
       "type": "image_generation_call",
       "status": "completed"
     },
     "data": "iVBORw0KGgoAAAANSUhEUgAA..."
   }
   ```

9. **`response.done`** - Final event with usage statistics

   ```json
   {
     "type": "response.done",
     "response": {
       "id": "request-id",
       "object": "response",
       "status": "completed",
       "usage": {
         "input_tokens": 100,
         "input_tokens_details": { "cached_tokens": 0 },
         "output_tokens": 50,
         "output_tokens_details": { "reasoning_tokens": 0 },
         "total_tokens": 150
       }
     }
   }
   ```

10. **`[DONE]`** - End of stream marker (plain text, not JSON)

### Handling Reasoning Events

For reasoning-capable models (like OpenAI's o1, o3), you can capture and display reasoning:

```python
import json

reasoning_chunks = []
text_chunks = []

for chunk in client.chat(
    messages=[{"role": "user", "content": "Solve this complex problem step by step."}],
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
                print("\n[Model is thinking...]")
                reasoning_chunks = []

            elif event_type == "response.reasoning.delta":
                delta = event.get("delta", "")
                reasoning_chunks.append(delta)
                # Show reasoning as it streams
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

### Handling Image Generation Events

For models that generate images (like some Gemini models), handle image events:

```python
import json
import base64

images = []

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
                print("\n[Image generation started]")

            elif event_type == "response.image_generation_call.completed":
                image_call = event.get("image_generation_call", {})
                if "url" in image_call:
                    images.append({"url": image_call["url"]})
                    print(f"\n[Image generated: {image_call['url']}]")
                elif "data" in event:
                    # Base64 image data
                    images.append({"data": event["data"]})
                    print("\n[Image generated: base64 data]")

            elif event_type == "response.content_part.delta":
                delta = event.get("delta", "")
                print(delta, end="", flush=True)

        except json.JSONDecodeError:
            pass

# Save images
for i, img in enumerate(images):
    if "url" in img:
        # Download from URL
        import requests
        response = requests.get(img["url"])
        with open(f"image_{i}.png", "wb") as f:
            f.write(response.content)
    elif "data" in img:
        # Save base64 data
        with open(f"image_{i}.png", "wb") as f:
            f.write(base64.b64decode(img["data"]))
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
# Access response text from the output array
assistant_response = response["output"][0]["content"][0]["text"]
messages.append({"role": "assistant", "content": assistant_response})
print(f"Assistant: {assistant_response}")

# Second user message
messages.append({"role": "user", "content": "What can you help me with?"})
response = client.chat(messages=messages, model="openai/gpt-4o-mini")
assistant_response = response["output"][0]["content"][0]["text"]
messages.append({"role": "assistant", "content": assistant_response})
print(f"Assistant: {assistant_response}")
```

## Response Format

The response from the chat method follows an OpenAI-compatible format:

```python
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
            ],
            # Optional: 'reasoning' field for reasoning-capable models
        }
    ],
    'usage': {
        'input_tokens': 24,
        'input_tokens_details': {'cached_tokens': 0},
        'output_tokens': 7,
        'output_tokens_details': {'reasoning_tokens': 0},
        'total_tokens': 31
    },
    'status': 'completed',
    # Optional fields if provided in request:
    'temperature': 0.7,
    'top_p': 1.0,
    'max_output_tokens': 100
}
```

### Accessing Response Content

To get the text content from the response:

```python
response = client.chat(
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    model="openai/gpt-4o-mini"
)

# Get the text content
text = response["output"][0]["content"][0]["text"]
print(text)  # "The capital of France is Paris."

# Get usage information
usage = response["usage"]
print(f"Input tokens: {usage['input_tokens']}")
print(f"Output tokens: {usage['output_tokens']}")
print(f"Total tokens: {usage['total_tokens']}")

# Check for reasoning content (if available)
if "reasoning" in response["output"][0]:
    reasoning = response["output"][0]["reasoning"]
    print(f"Reasoning: {reasoning}")
```

_Last updated: Nov 16, 2025_
