# Streaming Responses

indoxRouter supports streaming responses from LLM providers, which is useful for real-time applications where you want to display the response as it's being generated.

## Basic Streaming

To enable streaming, set the `stream` parameter to `True` and the `return_generator` parameter to `True` when making a request:

```python
from indoxRouter import Client

client = Client(api_key="your-api-key")

# Define the prompt
prompt = "Write a short story about a robot learning to paint."

# Make the streaming request
generator = client.completion(
    prompt=prompt,
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=300,
    stream=True,
    return_generator=True,
)

# Iterate through the generator and print each chunk
response_text = ""
usage_info = None

for chunk in generator:
    # Check if this is the final usage info chunk
    if isinstance(chunk, dict) and chunk.get("is_usage_info"):
        usage_info = chunk
    else:
        # This is a content chunk
        print(chunk, end="", flush=True)
        response_text += chunk

print("\n\nFinal response:", response_text)
print("Usage info:", usage_info)
```

## Streaming in Web Applications

### FastAPI Example

Here's an example of using streaming responses with FastAPI:

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from indoxRouter import Client

app = FastAPI()
client = Client(api_key="your-api-key")

@app.post("/stream")
async def stream_response(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    model = data.get("model", "openai/gpt-4o-mini")

    async def generate():
        generator = client.completion(
            prompt=prompt,
            model=model,
            stream=True,
            return_generator=True,
        )

        for chunk in generator:
            if isinstance(chunk, dict) and chunk.get("is_usage_info"):
                # Skip the usage info chunk
                continue
            yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
```

### Flask Example

Here's an example of using streaming responses with Flask:

```python
from flask import Flask, request, Response
from indoxRouter import Client

app = Flask(__name__)
client = Client(api_key="your-api-key")

@app.route("/stream", methods=["POST"])
def stream_response():
    data = request.json
    prompt = data.get("prompt", "")
    model = data.get("model", "openai/gpt-4o-mini")

    def generate():
        generator = client.completion(
            prompt=prompt,
            model=model,
            stream=True,
            return_generator=True,
        )

        for chunk in generator:
            if isinstance(chunk, dict) and chunk.get("is_usage_info"):
                # Skip the usage info chunk
                continue
            yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
    )
```

## Streaming Chat Completions

You can also stream chat completions:

```python
messages = [
    {"role": "user", "content": "Write a short story about a robot learning to paint."}
]

generator = client.chat(
    messages=messages,
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
    stream=True,
    return_generator=True,
)

for chunk in generator:
    if isinstance(chunk, dict) and chunk.get("is_usage_info"):
        usage_info = chunk
    else:
        print(chunk, end="", flush=True)
```

## Handling Streaming in JavaScript

Here's an example of handling streaming responses in JavaScript:

```javascript
async function streamCompletion() {
  const response = await fetch("/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt: "Write a short story about a robot learning to paint.",
      model: "openai/gpt-4o-mini",
    }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let result = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") break;
        result += data;
        // Update UI with the new chunk
        document.getElementById("result").textContent = result;
      }
    }
  }
}
```

## Best Practices

1. **Error Handling**: Always handle errors that might occur during streaming.
2. **Timeouts**: Set appropriate timeouts for streaming requests.
3. **Buffering**: Consider buffering chunks to reduce UI updates for a smoother experience.
4. **Fallback**: Provide a fallback mechanism in case streaming is not available.
5. **Usage Tracking**: Keep track of the usage information returned at the end of the stream.

## Limitations

- Not all providers support streaming.
- Streaming may not be available for all models.
- The format of streaming responses may vary between providers.

For more examples, see the [Streaming Examples](../examples/streaming.md) section.
