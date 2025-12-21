# API Reference

!!! info "API Version"
**Version:** 0.2.0

A unified API for various AI providers

## Base URL

```
https://api.indoxhub.com/api/v1
```

## Authentication

All endpoints require authentication using an API key. Include your API key in the request header:

```http
Authorization: Bearer YOUR_API_KEY
```

You can obtain an API key by registering an account through the platform.

## Installation

Install the client libraries:

=== "Python"

    ```bash
    pip install indoxhub
    ```

=== "JavaScript/TypeScript"

    ```bash
    npm install @indoxhub/client
    ```

---

## Available Endpoints

The API provides the following user-facing endpoints:

- [Analytics](#analytics)
- [Audio](#audio)
- [Chat](#chat)
- [Completions](#completions)
- [Embeddings](#embeddings)
- [Images](#images)
- [Models](#models)
- [User](#user)
- [Videos](#videos)

---

## Analytics

### Get Usage Data

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/analytics/usage</code>
</div>

Get detailed usage analytics with flexible grouping and filtering.

Returns:
Usage analytics data based on the specified filters and grouping.

**Parameters:**

| Name              | Location | Type    | Required | Description                                                                        |
| ----------------- | -------- | ------- | -------- | ---------------------------------------------------------------------------------- |
| `start_date`      | query    | any     |          | Start date for filtering (YYYY-MM-DD)                                              |
| `end_date`        | query    | any     |          | End date for filtering (YYYY-MM-DD)                                                |
| `group_by`        | query    | string  |          | Field to group results by (date, model, provider, endpoint, session_id, client_ip) |
| `provider`        | query    | any     |          | Filter by provider                                                                 |
| `model`           | query    | any     |          | Filter by model                                                                    |
| `session_id`      | query    | any     |          | Filter by session ID                                                               |
| `endpoint`        | query    | any     |          | Filter by endpoint (chat, completion, embedding, image)                            |
| `include_content` | query    | boolean |          | Include request/response content in results (only for non-grouped queries)         |

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Session Data

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/analytics/sessions</code>
</div>

Get session-based analytics showing conversation flows.

Returns:
Session analytics data showing sequences of interactions.

**Parameters:**

| Name         | Location | Type | Required | Description                           |
| ------------ | -------- | ---- | -------- | ------------------------------------- |
| `start_date` | query    | any  |          | Start date for filtering (YYYY-MM-DD) |
| `end_date`   | query    | any  |          | End date for filtering (YYYY-MM-DD)   |
| `session_id` | query    | any  |          | Filter by specific session ID         |

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Model Performance

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/analytics/models</code>
</div>

Get model performance analytics comparing different models.

Returns:
Model performance data grouped by model.

**Parameters:**

| Name         | Location | Type | Required | Description                           |
| ------------ | -------- | ---- | -------- | ------------------------------------- |
| `start_date` | query    | any  |          | Start date for filtering (YYYY-MM-DD) |
| `end_date`   | query    | any  |          | End date for filtering (YYYY-MM-DD)   |
| `provider`   | query    | any  |          | Filter by provider                    |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/analytics/models \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## Audio

### Create Text To Speech

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/audio/tts/generations</code>
</div>

Generate audio from text using text-to-speech models.

Args:
request: The FastAPI request object
audio_request: The text-to-speech generation request.
current_user: The current user.

Returns:
The text-to-speech generation response.

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `application/json`

**Schema:** [AudioRequest](#schema-audiorequest)

```json
{
  "input": "string"  // required,
  "provider": "...",
  "model": "...",
  "voice": "...",
  "instructions": "...",
  "response_format": "...",
  "speed": "...",
  "additional_params": "...",
  "byok_api_key": "..."
}
```

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.text_to_speech(
        input="Hello, world!",
        model="openai/tts-1",
        voice="alloy"
    )
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/audio/tts/generations \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "input": "Hello, world!",
        "model": "openai/tts-1",
        "voice": "alloy"
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.textToSpeech(
      "Hello, world!",
      {model: "openai/tts-1", voice: "alloy"}
    );
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [AudioResponse](#schema-audioresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Create Transcription

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/audio/stt/transcriptions</code>
</div>

Transcribe audio to text using speech-to-text models.

Args:
request: The FastAPI request object
file: The audio file to transcribe
provider: The provider to use (optional, defaults to openai)
model: The model to use (optional, defaults to whisper-1)
language: The language code (e.g., 'en', 'es', 'fr')
prompt: Optional text to guide the model's style
response_format: The format of the response (json, text, srt, verbose_json, vtt)
temperature: Temperature for transcription (0.0 to 1.0)
timestamp_granularities: JSON string for timestamp granularities (whisper-1 only)
byok_api_key: API key from the user's API keys
current_user: The current user

Returns:
The speech-to-text transcription response.

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `multipart/form-data`

**Schema:** [Body_create_transcription_audio_stt_transcriptions_post](#schema-body_create_transcription_audio_stt_transcriptions_post)

```json
{
  "file": "string"  // required,
  "provider": "string",
  "model": "string",
  "language": "string",
  "prompt": "string",
  "response_format": "json",
  "temperature": 0,
  "timestamp_granularities": "string",
  "byok_api_key": "string"
}
```

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.speech_to_text(
        file="path/to/audio.mp3",
        model="openai/whisper-1"
    )
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/audio/stt/transcriptions \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.speechToText(
      "path/to/audio.mp3",
      {model: "openai/whisper-1"}
    );
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [AudioResponse](#schema-audioresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Create Translation

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/audio/stt/translations</code>
</div>

Translate audio to English text using speech-to-text models.

Args:
request: The FastAPI request object
file: The audio file to translate
provider: The provider to use (only openai supports translation)
model: The model to use (only whisper-1 supports translation)
prompt: Optional text to guide the model's style
response_format: The format of the response (json, text, srt, verbose_json, vtt)
temperature: Temperature for translation (0.0 to 1.0)
byok_api_key: API key from the user's API keys
current_user: The current user

Returns:
The audio translation response.

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `multipart/form-data`

**Schema:** [Body_create_translation_audio_stt_translations_post](#schema-body_create_translation_audio_stt_translations_post)

```json
{
  "file": "string"  // required,
  "provider": "openai",
  "model": "whisper-1",
  "prompt": "string",
  "response_format": "json",
  "temperature": 0,
  "byok_api_key": "string"
}
```

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.translate_audio(
        file="path/to/audio.mp3",
        model="openai/whisper-1"
    )
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/audio/stt/translations \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.translateAudio(
      "path/to/audio.mp3",
      {model: "openai/whisper-1"}
    );
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [AudioResponse](#schema-audioresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## Chat

### Create Chat Completion

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/chat/completions</code>
</div>

Create a chat completion.

Args:
request: The FastAPI request object
chat_request: The chat completion request.
current_user: The current user.

Returns:
The chat completion response.

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `application/json`

**Schema:** [ChatRequest](#schema-chatrequest)

```json
{
  "messages": []  // List of messages cannot be empty - required,
  "provider": "...",
  "model": "...",
  "temperature": "...",
  "max_tokens": "...",
  "top_p": "...",
  "frequency_penalty": "...",
  "presence_penalty": "...",
  "stream": "...",
  "additional_params": "...",
  "byok_api_key": "..."
}
```

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.chat(
        messages=[
            {"role": "user", "content": "Hello!"}
        ],
        model="openai/gpt-4o-mini"
    )
    # Access response text from output array
    print(response["output"][0]["content"][0]["text"])
    # Access usage information
    print(f"Tokens: {response['usage']['total_tokens']}")
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/chat/completions \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [{"role": "user", "content": "Hello!"}],
        "model": "openai/gpt-4o-mini"
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.chat(
      [{role: "user", content: "Hello!"}],
      {model: "openai/gpt-4o-mini"}
    );
    console.log(response);
    ```

**Streaming Responses**

When `stream: true` is set in the request, the endpoint returns a Server-Sent Events (SSE) stream instead of a JSON response. The stream contains event-based data compatible with OpenAI's streaming API format.

**Stream Format:**

Each event is sent as a Server-Sent Event with the format:
```
data: <json_event>\n\n
```

The stream ends with:
```
data: [DONE]\n\n
```

**Streaming Event Types:**

The following event types are emitted during streaming:

1. **`response.created`** - Response initialization
2. **`response.reasoning.started`** - Reasoning phase started (for reasoning-capable models)
3. **`response.reasoning.delta`** - Reasoning content chunks
4. **`response.output_item.added`** - Message output item added
5. **`response.content_part.added`** - Content part added
6. **`response.content_part.delta`** - Text content chunks (main streaming content)
7. **`response.output_item.done`** - Output item completed
8. **`response.image_generation_call.*`** - Image generation events (if images are generated)
9. **`response.done`** - Final event with usage statistics
10. **`[DONE]`** - End of stream marker (plain text, not JSON)

For detailed event structures and examples, see the [Streaming Responses](../usage/responses.md#streaming-responses) section in the usage guide.

**Streaming Code Example:**

=== "Python"

    ```python
    import json
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    # Enable streaming
    for chunk in client.chat(
        messages=[{"role": "user", "content": "Tell me a story"}],
        model="openai/gpt-4o-mini",
        stream=True
    ):
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
                
                # Handle final usage
                elif event_type == "response.done":
                    usage = event.get("response", {}).get("usage", {})
                    print(f"\n\nTotal tokens: {usage.get('total_tokens', 0)}")
            except json.JSONDecodeError:
                pass
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/chat/completions \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -H "Accept: text/event-stream" \
      -d '{
        "messages": [{"role": "user", "content": "Tell me a story"}],
        "model": "openai/gpt-4o-mini",
        "stream": true
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const stream = await client.chat(
      [{role: "user", content: "Tell me a story"}],
      {model: "openai/gpt-4o-mini", stream: true}
    );

    for await (const chunk of stream) {
      if (chunk.startsWith("data: ")) {
        const data = chunk.slice(6);
        if (data.trim() === "[DONE]") break;
        
        try {
          const event = JSON.parse(data);
          if (event.type === "response.content_part.delta") {
            process.stdout.write(event.delta);
          } else if (event.type === "response.done") {
            console.log(`\n\nTotal tokens: ${event.response.usage.total_tokens}`);
          }
        } catch (e) {
          // Ignore parse errors
        }
      }
    }
    ```

**Responses:**

??? success "200 - Successful Response (Non-Streaming)"

    **Content-Type:** `application/json`

    **Schema:** [ChatResponse](#schema-chatresponse)

    When `stream: false` or not specified, returns a JSON response with OpenAI-compatible format:
    ```json
    {
      "id": "request-id",
      "object": "response",
      "created_at": 1718456006,
      "model": "gpt-4o-mini",
      "provider": "openai",
      "duration_ms": 1737.61,
      "output": [{
        "type": "message",
        "status": "completed",
        "role": "assistant",
        "content": [{
          "type": "output_text",
          "text": "Response text here...",
          "annotations": []
        }]
      }],
      "usage": {
        "input_tokens": 24,
        "input_tokens_details": {"cached_tokens": 0},
        "output_tokens": 7,
        "output_tokens_details": {"reasoning_tokens": 0},
        "total_tokens": 31
      },
      "status": "completed"
    }
    ```

??? success "200 - Successful Response (Streaming)"

    **Content-Type:** `text/event-stream`

    When `stream: true`, returns a Server-Sent Events stream. See [Streaming Responses](../usage/responses.md#streaming-responses) section in the usage guide for detailed event format documentation.

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Stop Stream

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/chat/stop-stream/{stream_id}</code>
</div>

Stop an active streaming response and log its usage.

Args:
stream_id: ID of the stream to stop
current_user: The current authenticated user

Returns:
Success status

**Parameters:**

| Name        | Location | Type   | Required | Description |
| ----------- | -------- | ------ | -------- | ----------- |
| `stream_id` | path     | string | ✓        |             |

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## Completions

### Create Completion

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/completions</code>
</div>

Create a text completion.

Args:
request: The FastAPI request object
completion_request: The completion request.
current_user: The current user.

Returns:
The completion response.

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `application/json`

**Schema:** [CompletionRequest](#schema-completionrequest)

```json
{
  "prompt": "string"  // required,
  "provider": "...",
  "model": "...",
  "temperature": "...",
  "max_tokens": "...",
  "top_p": "...",
  "frequency_penalty": "...",
  "presence_penalty": "...",
  "stream": "...",
  "additional_params": "...",
  "byok_api_key": "..."
}
```

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.completion(
        prompt="Write a story about",
        model="openai/gpt-3.5-turbo-instruct"
    )
    # Access response text from output array
    print(response["output"][0]["content"][0]["text"])
    # Access usage information
    print(f"Tokens: {response['usage']['total_tokens']}")
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/completions \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "prompt": "Write a story about",
        "model": "openai/gpt-3.5-turbo-instruct"
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.completion(
      "Write a story about",
      {model: "openai/gpt-3.5-turbo-instruct"}
    );
    // Access response text from output array
    console.log(response.output[0].content[0].text);
    // Access usage information
    console.log(`Tokens: ${response.usage.total_tokens}`);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [CompletionResponse](#schema-completionresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Stop Stream

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/completions/stop-stream/{stream_id}</code>
</div>

Stop an active streaming response and log its usage.

Args:
stream_id: ID of the stream to stop
current_user: The current authenticated user

Returns:
Success status

**Parameters:**

| Name        | Location | Type   | Required | Description |
| ----------- | -------- | ------ | -------- | ----------- |
| `stream_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    # Stop a streaming completion
    result = client.stop_completion_stream(stream_id="your-stream-id")
    print(result)
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/completions/stop-stream/{stream_id} \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    // Stop a streaming completion
    const result = await client.stopCompletionStream("your-stream-id");
    console.log(result);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## Embeddings

### Create Embedding

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/embeddings</code>
</div>

Create embeddings for text.

Args:
request: The FastAPI request object
embedding_request: The embedding request.
current_user: The current user.

Returns:
The embedding response.

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `application/json`

**Schema:** [EmbeddingRequest](#schema-embeddingrequest)

```json
{
  "text": "..."  // required,
  "provider": "...",
  "model": "...",
  "additional_params": "...",
  "byok_api_key": "..."
}
```

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.embeddings(
        text="Sample text to embed",
        model="openai/text-embedding-ada-002"
    )
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/embeddings \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "text": ["Sample text to embed"],
        "model": "openai/text-embedding-ada-002"
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.embeddings(
      "Sample text to embed",
      {model: "openai/text-embedding-ada-002"}
    );
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [EmbeddingResponse](#schema-embeddingresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## Images

### Create Image

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/images/generations</code>
</div>

Generate images from a prompt.

Args:
request: The FastAPI request object
image_request: The image generation request.
current_user: The current user.

Returns:
The image generation response.

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `application/json`

**Schema:** [ImageRequest](#schema-imagerequest)

```json
{
  "prompt": "string"  // required,
  "provider": "...",
  "model": "...",
  "size": "...",
  "n": "...",
  "quality": "...",
  "style": "...",
  "response_format": "...",
  "user": "...",
  "background": "...",
  "moderation": "...",
  "output_compression": "...",
  "output_format": "...",
  "negative_prompt": "...",
  "guidance_scale": "...",
  "seed": "...",
  "safety_filter_level": "...",
  "person_generation": "...",
  "include_safety_attributes": "...",
  "include_rai_reason": "...",
  "language": "...",
  "output_mime_type": "...",
  "add_watermark": "...",
  "enhance_prompt": "...",
  "aspect_ratio": "...",
  "additional_params": "...",
  "byok_api_key": "..."
}
```

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.images(
        prompt="A beautiful sunset",
        model="openai/dall-e-3"
    )
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/images/generations \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "prompt": "A beautiful sunset",
        "model": "openai/dall-e-3"
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.images(
      "A beautiful sunset",
      {model: "openai/dall-e-3"}
    );
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [ImageResponse](#schema-imageresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## Models

### Get Providers

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/</code>
</div>

List all providers with their complete structure from MongoDB (with JSON fallback).

Returns:
A list of provider data from MongoDB or JSON files as fallback.

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/ \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

---

### Get Trending Models Data

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/trending</code>
</div>

Get trending models based on usage over the specified time period.

This endpoint does not require authentication and returns aggregate usage statistics.

Args:
days: Number of days to look back
limit: Maximum number of models to return

Returns:
List of trending models with aggregate usage statistics

**Parameters:**

| Name    | Location | Type    | Required | Description                                   |
| ------- | -------- | ------- | -------- | --------------------------------------------- |
| `days`  | query    | integer |          | Number of days to look back for trending data |
| `limit` | query    | integer |          | Number of trending models to return           |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/trending \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Provider Info

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/{provider_id}</code>
</div>

Get the complete structure for a specific provider from MongoDB (with JSON fallback).

Args:
provider_id: The provider ID

Returns:
The provider data from MongoDB or JSON files as fallback

**Parameters:**

| Name          | Location | Type   | Required | Description |
| ------------- | -------- | ------ | -------- | ----------- |
| `provider_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/{provider_id} \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Text Completion Models

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/{provider_id}/text_completions</code>
</div>

Get text completion models for a provider.

Args:
provider_id: The provider ID

Returns:
List of text completion models exactly as stored in JSON

**Parameters:**

| Name          | Location | Type   | Required | Description |
| ------------- | -------- | ------ | -------- | ----------- |
| `provider_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/{provider_id}/text_completions \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Embedding Models

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/{provider_id}/embeddings</code>
</div>

Get embedding models for a provider.

Args:
provider_id: The provider ID

Returns:
List of embedding models exactly as stored in JSON

**Parameters:**

| Name          | Location | Type   | Required | Description |
| ------------- | -------- | ------ | -------- | ----------- |
| `provider_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.embeddings(
        text="Sample text to embed",
        model="openai/text-embedding-ada-002"
    )
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/{provider_id}/embeddings \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.embeddings(
      "Sample text to embed",
      {model: "openai/text-embedding-ada-002"}
    );
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Image Generation Models

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/{provider_id}/image_generation</code>
</div>

Get image generation models for a provider.

Args:
provider_id: The provider ID

Returns:
List of image generation models exactly as stored in JSON

**Parameters:**

| Name          | Location | Type   | Required | Description |
| ------------- | -------- | ------ | -------- | ----------- |
| `provider_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/{provider_id}/image_generation \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Text To Speech Models

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/{provider_id}/text_to_speech</code>
</div>

Get text-to-speech models for a provider.

Args:
provider_id: The provider ID

Returns:
List of text-to-speech models exactly as stored in JSON

**Parameters:**

| Name          | Location | Type   | Required | Description |
| ------------- | -------- | ------ | -------- | ----------- |
| `provider_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/{provider_id}/text_to_speech \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Speech To Text Models

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/{provider_id}/speech_to_text</code>
</div>

Get speech-to-text models for a provider.

Args:
provider_id: The provider ID

Returns:
List of speech-to-text models exactly as stored in JSON

**Parameters:**

| Name          | Location | Type   | Required | Description |
| ------------- | -------- | ------ | -------- | ----------- |
| `provider_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/{provider_id}/speech_to_text \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Video Generation Models

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/{provider_id}/video_generation</code>
</div>

Get video generation models for a provider.

Args:
provider_id: The provider ID

Returns:
List of video generation models exactly as stored in JSON

**Parameters:**

| Name          | Location | Type   | Required | Description |
| ------------- | -------- | ------ | -------- | ----------- |
| `provider_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/{provider_id}/video_generation \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Model Info

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/models/{provider_id}/{model_id}</code>
</div>

Get information about a specific model from MongoDB (with JSON fallback).

Args:
provider_id: The provider ID
model_id: The model ID or modelName

Returns:
The model data from MongoDB or JSON files as fallback

**Parameters:**

| Name          | Location | Type   | Required | Description |
| ------------- | -------- | ------ | -------- | ----------- |
| `provider_id` | path     | string | ✓        |             |
| `model_id`    | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.models()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/models/{provider_id}/{model_id} \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.models();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## User

### Health Check

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/user/health</code>
</div>

Health check endpoint for the user router.

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

---

### Get Current User Details

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/user/me</code>
</div>

Get details of the currently authenticated user.

Args:
current_user: The current authenticated user.

Returns:
Current user details.

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [UserResponse](#schema-userresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### List Transactions

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/user/transactions</code>
</div>

List all transactions for the authenticated user.

Args:
current_user: The current authenticated user.
limit: Maximum number of transactions to return.
offset: Offset for pagination.

Returns:
List of transactions.

**Parameters:**

| Name     | Location | Type    | Required | Description |
| -------- | -------- | ------- | -------- | ----------- |
| `limit`  | query    | integer |          |             |
| `offset` | query    | integer |          |             |

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [TransactionList](#schema-transactionlist)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Create New Api Key

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/user/api-keys</code>
</div>

Create a new API key for the authenticated user.

This is the ONLY endpoint that returns the full API key.
After creation, the key will be masked in all other responses.

Args:
request: The request object for debugging
api_key_data: The API key creation data.
current_user: The current authenticated user.

Returns:
The newly created API key with full key visible (only time it's shown).

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `application/json`

**Schema:** [app**models**schemas\_\_ApiKeyCreate](#schema-app__models__schemas__apikeycreate)

```json
{
  "name": "API Key",
  "expiration_time": "..." // Expiration time in days from now. If not provided (None), the API key will never expire.
}
```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [ApiKeyCreatedResponse](#schema-apikeycreatedresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### List Api Keys

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/user/api-keys</code>
</div>

List all API keys for the authenticated user.

Args:
current_user: The current authenticated user.

Returns:
List of API keys.

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [ApiKeyList](#schema-apikeylist)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Delete Api Key Endpoint

<div class="endpoint-badge">
  <span class="method method-delete">DELETE</span>
  <code class="endpoint-path">/user/api-keys/{api_key_id}</code>
</div>

Permanently delete an API key.

Args:
api_key_id: The API key ID to delete.
current_user: The current authenticated user.

Returns:
Success indicator.

**Parameters:**

| Name         | Location | Type    | Required | Description |
| ------------ | -------- | ------- | -------- | ----------- |
| `api_key_id` | path     | integer | ✓        |             |

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Usage Stats

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/user/usage</code>
</div>

Get usage statistics for the authenticated user.

Args:
current_user: The current authenticated user.
start_date: Optional start date for filtering.
end_date: Optional end date for filtering.

Returns:
Usage statistics.

**Parameters:**

| Name         | Location | Type | Required | Description |
| ------------ | -------- | ---- | -------- | ----------- |
| `start_date` | query    | any  |          |             |
| `end_date`   | query    | any  |          |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.get_usage()
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/user/usage \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.getUsage();
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [UsageResponse](#schema-usageresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Revoke User Api Key

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/user/api-keys/{api_key_id}/revoke</code>
</div>

Revoke an API key without deleting it.

Args:
api_key_id: The API key ID to revoke.
current_user: The current authenticated user.

Returns:
Success indicator.

**Parameters:**

| Name         | Location | Type    | Required | Description |
| ------------ | -------- | ------- | -------- | ----------- |
| `api_key_id` | path     | integer | ✓        |             |

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Enable User Api Key

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/user/api-keys/{api_key_id}/enable</code>
</div>

Enable a previously revoked API key.

Args:
api_key_id: The ID of the API key to enable
current_user: The current authenticated user

Returns:
Success status

**Parameters:**

| Name         | Location | Type    | Required | Description |
| ------------ | -------- | ------- | -------- | ----------- |
| `api_key_id` | path     | integer | ✓        |             |

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Delete User Account

<div class="endpoint-badge">
  <span class="method method-delete">DELETE</span>
  <code class="endpoint-path">/user/account</code>
</div>

Delete the authenticated user's account permanently.

This action is irreversible and will delete all user data.

Args:
current_user: The current authenticated user
response: Response object to clear cookies

Returns:
Success status

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## Videos

### Create Video

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/videos/generations</code>
</div>

Generate videos from a prompt.

Args:
request: The FastAPI request object
video_request: The video generation request.
current_user: The current user.

Returns:
The video generation response.

**Request Body:**

!!! info "Required"
This request requires a body.

**Content-Type:** `application/json`

**Schema:** [VideoRequest](#schema-videorequest)

```json
{
  "prompt": "string"  // required,
  "provider": "...",
  "model": "...",
  "aspect_ratio": "...",
  "resolution": "...",
  "duration": "...",
  "n": "...",
  "size": "...",
  "input_image": "...",
  "reference_image": "...",
  "reference_images": "...",
  "generate_audio": "...",
  "negative_prompt": "...",
  "person_generation": "...",
  "last_frame": "...",
  "video": "...",
  "response_format": "...",
  "additional_params": "...",
  "byok_api_key": "..."
}
```

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.videos(
        prompt="A cat playing piano",
        model="google/veo-3.0-generate-001",
        duration=8
    )
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/videos/generations \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "prompt": "A cat playing piano",
        "model": "google/veo-3.0-generate-001",
        "duration": 8
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.videos(
      "A cat playing piano",
      {model: "google/veo-3.0-generate-001", duration: 8}
    );
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

    **Schema:** [VideoResponse](#schema-videoresponse)

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get Video Job Status

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/videos/jobs/{job_id}</code>
</div>

Get the status of a video generation job.

Args:
job_id: The job ID to check
current_user: The current user

Returns:
Job status information

**Parameters:**

| Name     | Location | Type   | Required | Description |
| -------- | -------- | ------ | -------- | ----------- |
| `job_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.get_video_job_status(job_id="job_123")
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X GET https://api.indoxhub.com/api/v1/videos/jobs/{job_id} \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json"
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.getVideoJobStatus("job_123");
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Get User Video Jobs

<div class="endpoint-badge">
  <span class="method method-get">GET</span>
  <code class="endpoint-path">/videos/jobs</code>
</div>

Get all video generation jobs for the current user.

Args:
limit: Maximum number of jobs to return
skip: Number of jobs to skip (for pagination)
current_user: The current user

Returns:
List of job information

**Parameters:**

| Name    | Location | Type    | Required | Description |
| ------- | -------- | ------- | -------- | ----------- |
| `limit` | query    | integer |          |             |
| `skip`  | query    | integer |          |             |

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

### Cancel Video Job

<div class="endpoint-badge">
  <span class="method method-post">POST</span>
  <code class="endpoint-path">/videos/jobs/{job_id}/cancel</code>
</div>

Cancel a pending video generation job.

Args:
job_id: The job ID to cancel
current_user: The current user

Returns:
Cancellation status

**Parameters:**

| Name     | Location | Type   | Required | Description |
| -------- | -------- | ------ | -------- | ----------- |
| `job_id` | path     | string | ✓        |             |

**Code Examples:**

=== "Python"

    ```python
    from indoxhub import Client

    client = Client(api_key="your_api_key")

    response = client.get_video_job_status(job_id="job_123")
    print(response)
    ```

=== "cURL"

    ```bash
    curl -X POST https://api.indoxhub.com/api/v1/videos/jobs/{job_id}/cancel \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "prompt": "A cat playing piano",
        "model": "google/veo-3.0-generate-001",
        "duration": 8
      }'
    ```

=== "JavaScript"

    ```javascript
    import { Client } from "@indoxhub/client";

    const client = new Client("your_api_key");

    const response = await client.getVideoJobStatus("job_123");
    console.log(response);
    ```

**Responses:**

??? success "200 - Successful Response"

    **Content-Type:** `application/json`

??? warning "422 - Validation Error"

    **Content-Type:** `application/json`

    **Schema:** [HTTPValidationError](#schema-httpvalidationerror)

---

## Data Schemas

This section describes the data models used in the API.

### ApiKeyCreatedResponse {: #schema-apikeycreatedresponse }

API key response model for creation (with full key shown once).

**Properties:**

| Property       | Type    | Required | Description |
| -------------- | ------- | -------- | ----------- |
| `id`           | integer | ✓        |             |
| `api_key`      | string  | ✓        |             |
| `name`         | string  | ✓        |             |
| `is_active`    | boolean | ✓        |             |
| `created_at`   | string  | ✓        |             |
| `expires_at`   | any     | ✓        |             |
| `last_used_at` | any     |          |             |

### ApiKeyList {: #schema-apikeylist }

API key list response model.

**Properties:**

| Property | Type                                            | Required | Description |
| -------- | ----------------------------------------------- | -------- | ----------- |
| `keys`   | array[[ApiKeyResponse](#schema-apikeyresponse)] | ✓        |             |

### ApiKeyResponse {: #schema-apikeyresponse }

API key response model for listing (with masked key).

**Properties:**

| Property       | Type    | Required | Description |
| -------------- | ------- | -------- | ----------- |
| `id`           | integer | ✓        |             |
| `api_key`      | string  | ✓        |             |
| `name`         | string  | ✓        |             |
| `is_active`    | boolean | ✓        |             |
| `created_at`   | string  | ✓        |             |
| `expires_at`   | any     | ✓        |             |
| `last_used_at` | any     |          |             |

### AudioRequest {: #schema-audiorequest }

Text-to-speech generation request model.

**Properties:**

| Property            | Type   | Required | Description |
| ------------------- | ------ | -------- | ----------- |
| `input`             | string | ✓        |             |
| `provider`          | any    |          |             |
| `model`             | any    |          |             |
| `voice`             | any    |          |             |
| `instructions`      | any    |          |             |
| `response_format`   | any    |          |             |
| `speed`             | any    |          |             |
| `additional_params` | any    |          |             |
| `byok_api_key`      | any    |          |             |

### AudioResponse {: #schema-audioresponse }

Audio generation response model.

**Properties:**

| Property       | Type    | Required | Description |
| -------------- | ------- | -------- | ----------- |
| `request_id`   | string  | ✓        |             |
| `created_at`   | string  | ✓        |             |
| `duration_ms`  | any     |          |             |
| `provider`     | string  | ✓        |             |
| `model`        | string  | ✓        |             |
| `success`      | boolean |          |             |
| `message`      | string  |          |             |
| `usage`        | any     |          |             |
| `raw_response` | any     |          |             |
| `data`         | object  |          |             |

### Body_create_transcription_audio_stt_transcriptions_post {: #schema-body_create_transcription_audio_stt_transcriptions_post }

**Properties:**

| Property                  | Type   | Required | Description |
| ------------------------- | ------ | -------- | ----------- |
| `file`                    | string | ✓        |             |
| `provider`                | string |          |             |
| `model`                   | string |          |             |
| `language`                | string |          |             |
| `prompt`                  | string |          |             |
| `response_format`         | string |          |             |
| `temperature`             | number |          |             |
| `timestamp_granularities` | string |          |             |
| `byok_api_key`            | string |          |             |

### Body_create_translation_audio_stt_translations_post {: #schema-body_create_translation_audio_stt_translations_post }

**Properties:**

| Property          | Type   | Required | Description |
| ----------------- | ------ | -------- | ----------- |
| `file`            | string | ✓        |             |
| `provider`        | string |          |             |
| `model`           | string |          |             |
| `prompt`          | string |          |             |
| `response_format` | string |          |             |
| `temperature`     | number |          |             |
| `byok_api_key`    | string |          |             |

### ChatMessage {: #schema-chatmessage }

Chat message model.

**Properties:**

| Property  | Type   | Required | Description |
| --------- | ------ | -------- | ----------- |
| `role`    | string | ✓        |             |
| `content` | any    | ✓        |             |

### ChatRequest {: #schema-chatrequest }

Chat completion request model.

**Properties:**

| Property            | Type                                      | Required | Description                      |
| ------------------- | ----------------------------------------- | -------- | -------------------------------- |
| `messages`          | array[[ChatMessage](#schema-chatmessage)] | ✓        | List of messages cannot be empty |
| `provider`          | any                                       |          |                                  |
| `model`             | any                                       |          |                                  |
| `temperature`       | any                                       |          |                                  |
| `max_tokens`        | any                                       |          |                                  |
| `top_p`             | any                                       |          |                                  |
| `frequency_penalty` | any                                       |          |                                  |
| `presence_penalty`  | any                                       |          |                                  |
| `stream`            | any                                       |          |                                  |
| `additional_params` | any                                       |          |                                  |
| `byok_api_key`      | any                                       |          |                                  |

### ChatResponse {: #schema-chatresponse }

Chat completion response model.

**Properties:**

| Property        | Type    | Required | Description |
| --------------- | ------- | -------- | ----------- |
| `request_id`    | string  | ✓        |             |
| `created_at`    | string  | ✓        |             |
| `duration_ms`   | any     |          |             |
| `provider`      | string  | ✓        |             |
| `model`         | string  | ✓        |             |
| `success`       | boolean |          |             |
| `message`       | string  |          |             |
| `usage`         | any     |          |             |
| `raw_response`  | any     |          |             |
| `data`          | any     |          |             |
| `finish_reason` | any     |          |             |
| `images`        | any     |          |             |

### CompletionRequest {: #schema-completionrequest }

Text completion request model.

**Properties:**

| Property            | Type   | Required | Description |
| ------------------- | ------ | -------- | ----------- |
| `prompt`            | string | ✓        |             |
| `provider`          | any    |          |             |
| `model`             | any    |          |             |
| `temperature`       | any    |          |             |
| `max_tokens`        | any    |          |             |
| `top_p`             | any    |          |             |
| `frequency_penalty` | any    |          |             |
| `presence_penalty`  | any    |          |             |
| `stream`            | any    |          |             |
| `additional_params` | any    |          |             |
| `byok_api_key`      | any    |          |             |

### CompletionResponse {: #schema-completionresponse }

Text completion response model.

**Properties:**

| Property        | Type    | Required | Description |
| --------------- | ------- | -------- | ----------- |
| `request_id`    | string  | ✓        |             |
| `created_at`    | string  | ✓        |             |
| `duration_ms`   | any     |          |             |
| `provider`      | string  | ✓        |             |
| `model`         | string  | ✓        |             |
| `success`       | boolean |          |             |
| `message`       | string  |          |             |
| `usage`         | any     |          |             |
| `raw_response`  | any     |          |             |
| `data`          | string  |          |             |
| `finish_reason` | any     |          |             |

### DailyUsage {: #schema-dailyusage }

**Properties:**

| Property   | Type                             | Required | Description |
| ---------- | -------------------------------- | -------- | ----------- |
| `date`     | string                           | ✓        |             |
| `requests` | integer                          | ✓        |             |
| `cost`     | number                           | ✓        |             |
| `tokens`   | [TokenUsage](#schema-tokenusage) | ✓        |             |

### EmbeddingRequest {: #schema-embeddingrequest }

Embedding request model.

**Properties:**

| Property            | Type | Required | Description |
| ------------------- | ---- | -------- | ----------- |
| `text`              | any  | ✓        |             |
| `provider`          | any  |          |             |
| `model`             | any  |          |             |
| `additional_params` | any  |          |             |
| `byok_api_key`      | any  |          |             |

### EmbeddingResponse {: #schema-embeddingresponse }

Embedding response model.

**Properties:**

| Property       | Type                 | Required | Description |
| -------------- | -------------------- | -------- | ----------- |
| `request_id`   | string               | ✓        |             |
| `created_at`   | string               | ✓        |             |
| `duration_ms`  | any                  |          |             |
| `provider`     | string               | ✓        |             |
| `model`        | string               | ✓        |             |
| `success`      | boolean              |          |             |
| `message`      | string               |          |             |
| `usage`        | any                  |          |             |
| `raw_response` | any                  |          |             |
| `data`         | array[array[number]] |          |             |
| `dimensions`   | integer              |          |             |

### HTTPValidationError {: #schema-httpvalidationerror }

**Properties:**

| Property | Type                                              | Required | Description |
| -------- | ------------------------------------------------- | -------- | ----------- |
| `detail` | array[[ValidationError](#schema-validationerror)] |          |             |

### ImageRequest {: #schema-imagerequest }

Image generation request model.

**Properties:**

| Property                    | Type   | Required | Description |
| --------------------------- | ------ | -------- | ----------- |
| `prompt`                    | string | ✓        |             |
| `provider`                  | any    |          |             |
| `model`                     | any    |          |             |
| `size`                      | any    |          |             |
| `n`                         | any    |          |             |
| `quality`                   | any    |          |             |
| `style`                     | any    |          |             |
| `response_format`           | any    |          |             |
| `user`                      | any    |          |             |
| `background`                | any    |          |             |
| `moderation`                | any    |          |             |
| `output_compression`        | any    |          |             |
| `output_format`             | any    |          |             |
| `negative_prompt`           | any    |          |             |
| `guidance_scale`            | any    |          |             |
| `seed`                      | any    |          |             |
| `safety_filter_level`       | any    |          |             |
| `person_generation`         | any    |          |             |
| `include_safety_attributes` | any    |          |             |
| `include_rai_reason`        | any    |          |             |
| `language`                  | any    |          |             |
| `output_mime_type`          | any    |          |             |
| `add_watermark`             | any    |          |             |
| `enhance_prompt`            | any    |          |             |
| `aspect_ratio`              | any    |          |             |
| `additional_params`         | any    |          |             |
| `byok_api_key`              | any    |          |             |

### ImageResponse {: #schema-imageresponse }

Image generation response model.

**Properties:**

| Property       | Type          | Required | Description |
| -------------- | ------------- | -------- | ----------- |
| `request_id`   | string        | ✓        |             |
| `created_at`   | string        | ✓        |             |
| `duration_ms`  | any           |          |             |
| `provider`     | string        | ✓        |             |
| `model`        | string        | ✓        |             |
| `success`      | boolean       |          |             |
| `message`      | string        |          |             |
| `usage`        | any           |          |             |
| `raw_response` | any           |          |             |
| `data`         | array[object] |          |             |

### TokenUsage {: #schema-tokenusage }

**Properties:**

| Property | Type    | Required | Description |
| -------- | ------- | -------- | ----------- |
| `input`  | integer | ✓        |             |
| `output` | integer | ✓        |             |
| `total`  | integer | ✓        |             |

### TransactionItem {: #schema-transactionitem }

Transaction item model for listing transactions.

**Properties:**

| Property           | Type    | Required | Description |
| ------------------ | ------- | -------- | ----------- |
| `id`               | integer | ✓        |             |
| `transaction_id`   | string  | ✓        |             |
| `amount`           | number  | ✓        |             |
| `currency`         | string  | ✓        |             |
| `transaction_type` | string  | ✓        |             |
| `status`           | string  | ✓        |             |
| `payment_method`   | string  | ✓        |             |
| `description`      | any     | ✓        |             |
| `created_at`       | string  | ✓        |             |

### TransactionList {: #schema-transactionlist }

Transaction list response model.

**Properties:**

| Property       | Type                                              | Required | Description |
| -------------- | ------------------------------------------------- | -------- | ----------- |
| `transactions` | array[[TransactionItem](#schema-transactionitem)] | ✓        |             |
| `total_count`  | integer                                           | ✓        |             |

### Usage {: #schema-usage }

Usage information model.

**Properties:**

| Property             | Type    | Required | Description |
| -------------------- | ------- | -------- | ----------- |
| `tokens_prompt`      | integer |          |             |
| `tokens_completion`  | integer |          |             |
| `tokens_total`       | integer |          |             |
| `cost`               | number  |          |             |
| `latency`            | number  |          |             |
| `timestamp`          | string  |          |             |
| `cache_read_tokens`  | integer |          |             |
| `cache_write_tokens` | integer |          |             |
| `reasoning_tokens`   | integer |          |             |
| `web_search_count`   | integer |          |             |
| `request_count`      | integer |          |             |
| `cost_breakdown`     | any     |          |             |

### UsageResponse {: #schema-usageresponse }

**Properties:**

| Property            | Type                                    | Required | Description |
| ------------------- | --------------------------------------- | -------- | ----------- |
| `total_requests`    | integer                                 | ✓        |             |
| `total_cost`        | number                                  | ✓        |             |
| `remaining_credits` | number                                  | ✓        |             |
| `total_tokens`      | [TokenUsage](#schema-tokenusage)        |          |             |
| `endpoints`         | object                                  | ✓        |             |
| `providers`         | object                                  | ✓        |             |
| `models`            | object                                  | ✓        |             |
| `daily_usage`       | array[[DailyUsage](#schema-dailyusage)] | ✓        |             |

### UsageStats {: #schema-usagestats }

**Properties:**

| Property   | Type                             | Required | Description |
| ---------- | -------------------------------- | -------- | ----------- |
| `requests` | integer                          | ✓        |             |
| `cost`     | number                           | ✓        |             |
| `tokens`   | [TokenUsage](#schema-tokenusage) | ✓        |             |

### UserResponse {: #schema-userresponse }

User response model.

**Properties:**

| Property                 | Type    | Required | Description |
| ------------------------ | ------- | -------- | ----------- |
| `id`                     | integer | ✓        |             |
| `username`               | string  | ✓        |             |
| `email`                  | string  | ✓        |             |
| `first_name`             | any     |          |             |
| `last_name`              | any     |          |             |
| `is_active`              | boolean | ✓        |             |
| `credits`                | number  | ✓        |             |
| `app_credit`             | integer | ✓        |             |
| `account_tier`           | string  | ✓        |             |
| `created_at`             | string  | ✓        |             |
| `metadata`               | any     |          |             |
| `has_model_restrictions` | any     |          |             |
| `has_password`           | any     |          |             |
| `avatar_url`             | any     |          |             |

### ValidationError {: #schema-validationerror }

**Properties:**

| Property | Type       | Required | Description |
| -------- | ---------- | -------- | ----------- |
| `loc`    | array[any] | ✓        |             |
| `msg`    | string     | ✓        |             |
| `type`   | string     | ✓        |             |

### VideoRequest {: #schema-videorequest }

Video generation request model.

**Properties:**

| Property            | Type   | Required | Description |
| ------------------- | ------ | -------- | ----------- |
| `prompt`            | string | ✓        |             |
| `provider`          | any    |          |             |
| `model`             | any    |          |             |
| `aspect_ratio`      | any    |          |             |
| `resolution`        | any    |          |             |
| `duration`          | any    |          |             |
| `n`                 | any    |          |             |
| `size`              | any    |          |             |
| `input_image`       | any    |          |             |
| `reference_image`   | any    |          |             |
| `reference_images`  | any    |          |             |
| `generate_audio`    | any    |          |             |
| `negative_prompt`   | any    |          |             |
| `person_generation` | any    |          |             |
| `last_frame`        | any    |          |             |
| `video`             | any    |          |             |
| `response_format`   | any    |          |             |
| `additional_params` | any    |          |             |
| `byok_api_key`      | any    |          |             |

### VideoResponse {: #schema-videoresponse }

Video generation response model.

**Properties:**

| Property       | Type    | Required | Description |
| -------------- | ------- | -------- | ----------- |
| `request_id`   | string  | ✓        |             |
| `created_at`   | string  | ✓        |             |
| `duration_ms`  | any     |          |             |
| `provider`     | string  | ✓        |             |
| `model`        | string  | ✓        |             |
| `success`      | boolean |          |             |
| `message`      | string  |          |             |
| `usage`        | any     |          |             |
| `raw_response` | any     |          |             |
| `data`         | any     |          |             |

### app**models**schemas**ApiKeyCreate {: #schema-app**models**schemas**apikeycreate }

API key creation request model.

**Properties:**

| Property          | Type   | Required | Description                                                                              |
| ----------------- | ------ | -------- | ---------------------------------------------------------------------------------------- |
| `name`            | string |          |                                                                                          |
| `expiration_time` | any    |          | Expiration time in days from now. If not provided (None), the API key will never expire. |

_Last updated: Nov 16, 2025_
