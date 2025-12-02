# Advanced Examples

This section covers advanced usage patterns and real-world applications of indoxhub.

## Streaming Responses

Handle real-time streaming responses for better user experience:

```python
from indoxhub import Client

client = Client(api_key="your_api_key")

# Stream chat responses
response = client.chat(
    messages=[
        {"role": "user", "content": "Write a short story about AI"}
    ],
    model="openai/gpt-4o-mini",
    stream=True
)

for chunk in response:
    if chunk.get("data"):
        print(chunk["data"], end="", flush=True)
```

## Batch Processing

Process multiple requests efficiently using synchronous calls:

```python
from concurrent.futures import ThreadPoolExecutor
from indoxhub import Client

def process_batch():
    client = Client(api_key="your_api_key")

    prompts = [
        "Explain quantum computing",
        "What is machine learning?",
        "How does blockchain work?"
    ]

    # Process requests in parallel using threads
    def make_request(prompt):
        return client.chat(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-4o-mini"
        )

    with ThreadPoolExecutor(max_workers=3) as executor:
        responses = list(executor.map(make_request, prompts))

    for i, response in enumerate(responses):
        print(f"Question {i+1}: {prompts[i]}")
        print(f"Answer: {response['data']}")
        print("---")

# Run the batch processing
process_batch()
```

Or using asyncio with synchronous client:

```python
import asyncio
from indoxhub import Client

async def process_batch():
    client = Client(api_key="your_api_key")

    prompts = [
        "Explain quantum computing",
        "What is machine learning?",
        "How does blockchain work?"
    ]

    # Run synchronous requests in thread pool
    loop = asyncio.get_event_loop()

    def make_request(prompt):
        return client.chat(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-4o-mini"
        )

    tasks = [
        loop.run_in_executor(None, make_request, prompt)
        for prompt in prompts
    ]

    responses = await asyncio.gather(*tasks)

    for i, response in enumerate(responses):
        print(f"Question {i+1}: {prompts[i]}")
        print(f"Answer: {response['data']}")
        print("---")

# Run the batch processing
asyncio.run(process_batch())
```

## Error Handling and Retries

Implement robust error handling:

```python
import time
from indoxhub import Client, indoxhubError

def chat_with_retry(client, messages, model, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat(
                messages=messages,
                model=model
            )
            return response
        except indoxhubError as e:
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
    print(response['data'])
except indoxhubError as e:
    print(f"Failed after all retries: {e}")
```

## Custom Model Routing

Route requests to different models based on content:

```python
from indoxhub import Client

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
            "response": response['data']
        }

# Usage
router = SmartRouter(api_key="your_api_key")

result = router.chat("Write a Python function to sort a list")
print(f"Model used: {result['model_used']}")
print(f"Response: {result['response']}")
```

## Tool Calling (Function Calling)

Use tool calling for structured outputs with compatible models:

```python
from indoxhub import Client
import json

client = Client(api_key="your_api_key")

# Define available tools (OpenAI tools format)
tools = [
    {
        "type": "function",
        "function": {
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
    }
]

response = client.chat(
    messages=[
        {"role": "user", "content": "What's the weather like in New York?"}
    ],
    model="openai/gpt-4o-mini",
    tools=tools,
    tool_choice="auto"
)

# Handle tool call (Note: This feature may not be fully implemented in current backend)
if response.get('tool_calls'):
    tool_calls = response['tool_calls']
    for tool_call in tool_calls:
        tool_name = tool_call['function']['name']
        tool_args = json.loads(tool_call['function']['arguments'])

        print(f"Tool called: {tool_name}")
        print(f"Arguments: {tool_args}")

        # In a real application, you would call the actual tool here
        weather_result = f"The weather in {tool_args['location']} is sunny, 72°F"

        # Send the tool result back to the model
        follow_up = client.chat(
            messages=[
                {"role": "user", "content": "What's the weather like in New York?"},
                {"role": "assistant", "content": response['data'], "tool_calls": tool_calls},
                {"role": "tool", "tool_call_id": tool_call['id'], "content": weather_result}
            ],
            model="openai/gpt-4o-mini"
        )

        print(follow_up['data'])
else:
    # Regular response without tool calls
    print(f"Response: {response['data']}")
```

**Note:** Tool calling support may vary by provider and model. Not all models in indoxhub currently support tool calling.

_Last updated: Nov 16, 2025_