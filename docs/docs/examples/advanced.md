# Advanced Examples

This section covers advanced usage patterns and real-world applications of IndoxRouter.

## Streaming Responses

Handle real-time streaming responses for better user experience:

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")

# Stream chat responses
for chunk in client.chat_stream(
    messages=[
        {"role": "user", "content": "Write a short story about AI"}
    ],
    model="openai/gpt-4o-mini"
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Batch Processing

Process multiple requests efficiently:

```python
import asyncio
from indoxrouter import AsyncClient

async def process_batch():
    client = AsyncClient(api_key="your_api_key")

    prompts = [
        "Explain quantum computing",
        "What is machine learning?",
        "How does blockchain work?"
    ]

    tasks = []
    for prompt in prompts:
        task = client.chat(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-4o-mini"
        )
        tasks.append(task)

    responses = await asyncio.gather(*tasks)

    for i, response in enumerate(responses):
        print(f"Question {i+1}: {prompts[i]}")
        print(f"Answer: {response['choices'][0]['message']['content']}")
        print("---")

# Run the batch processing
asyncio.run(process_batch())
```

## Error Handling and Retries

Implement robust error handling:

```python
import time
from indoxrouter import Client, IndoxRouterError

def chat_with_retry(client, messages, model, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat(
                messages=messages,
                model=model
            )
            return response
        except IndoxRouterError as e:
            if attempt == max_retries - 1:
                raise e

            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    return None

# Usage
client = Client(api_key="your_api_key")

try:
    response = chat_with_retry(
        client,
        [{"role": "user", "content": "Hello!"}],
        "openai/gpt-4o-mini"
    )
    print(response['choices'][0]['message']['content'])
except IndoxRouterError as e:
    print(f"Failed after all retries: {e}")
```

## Custom Model Routing

Route requests to different models based on content:

```python
from indoxrouter import Client

class SmartRouter:
    def __init__(self, api_key):
        self.client = Client(api_key=api_key)

    def route_request(self, message):
        # Analyze the request to choose the best model
        content = message.lower()

        if any(word in content for word in ['code', 'programming', 'function']):
            return "openai/gpt-4o"  # Better for coding
        elif any(word in content for word in ['creative', 'story', 'poem']):
            return "anthropic/claude-3-opus"  # Better for creativity
        elif len(content) < 50:
            return "openai/gpt-3.5-turbo"  # Fast for simple queries
        else:
            return "openai/gpt-4o-mini"  # Default choice

    def chat(self, message):
        model = self.route_request(message)

        response = self.client.chat(
            messages=[{"role": "user", "content": message}],
            model=model
        )

        return {
            "model_used": model,
            "response": response['choices'][0]['message']['content']
        }

# Usage
router = SmartRouter(api_key="your_api_key")

result = router.chat("Write a Python function to sort a list")
print(f"Model used: {result['model_used']}")
print(f"Response: {result['response']}")
```

## Function Calling

Use function calling for structured outputs:

```python
from indoxrouter import Client
import json

client = Client(api_key="your_api_key")

# Define available functions
functions = [
    {
        "name": "get_weather",
        "description": "Get weather information for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
]

response = client.chat(
    messages=[
        {"role": "user", "content": "What's the weather like in New York?"}
    ],
    model="openai/gpt-4o-mini",
    functions=functions,
    function_call="auto"
)

# Handle function call
if response['choices'][0]['message'].get('function_call'):
    function_call = response['choices'][0]['message']['function_call']
    function_name = function_call['name']
    function_args = json.loads(function_call['arguments'])

    print(f"Function called: {function_name}")
    print(f"Arguments: {function_args}")

    # In a real application, you would call the actual function here
    weather_result = f"The weather in {function_args['location']} is sunny, 72°F"

    # Send the function result back to the model
    follow_up = client.chat(
        messages=[
            {"role": "user", "content": "What's the weather like in New York?"},
            response['choices'][0]['message'],
            {"role": "function", "name": function_name, "content": weather_result}
        ],
        model="openai/gpt-4o-mini"
    )

    print(follow_up['choices'][0]['message']['content'])
```
