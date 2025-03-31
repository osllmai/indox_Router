# IndoxRouter Cookbook

This cookbook provides comprehensive examples of how to use the IndoxRouter client to interact with various AI providers through a unified API.

## Setup

First, let's install the IndoxRouter client and import the necessary modules:

```python
# Install the IndoxRouter client
!pip install indoxrouter

# Import the client and exceptions
from indoxrouter import Client
from indoxrouter import (
    IndoxRouterError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidParametersError,
    InsufficientCreditsError,
)
```

Now, let's initialize the client:

```python
# Initialize with API key
client = Client(api_key="your_api_key")

# Or use environment variable
# export INDOX_ROUTER_API_KEY=your_api_key
# client = Client()

# You can also set a custom timeout
# client = Client(api_key="your_api_key", timeout=30)  # 30 seconds timeout
```

## 1. Chat Completions

### Basic Chat Completion

Generate a simple chat completion:

```python
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="openai/gpt-4o-mini"
)

print("Response:", response["data"])
print("Cost:", response["usage"]["cost"])
print("Tokens used:", response["usage"]["tokens_total"])
```

### Chat Completion with Different Provider

Use a different provider for chat completion:

```python
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short poem about AI."}
    ],
    model="anthropic/claude-3-haiku",
    temperature=0.8,
    max_tokens=500
)

print("Response:", response["data"])
print("Cost:", response["usage"]["cost"])
```

### Multi-turn Conversation

Have a multi-turn conversation:

```python
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
]

response = client.chat(
    messages=conversation,
    model="openai/gpt-4o-mini"
)

# Add the assistant's response to the conversation
conversation.append({"role": "assistant", "content": response["data"]})

# Continue the conversation
conversation.append({"role": "user", "content": "Tell me a joke about programming."})

response = client.chat(
    messages=conversation,
    model="openai/gpt-4o-mini"
)

print("Response:", response["data"])
```

### Streaming Chat Completion

Stream the response for a better user experience:

```python
print("Streaming response:")
for chunk in client.chat(
    messages=[
        {"role": "user", "content": "Tell me a story about a robot in 5 sentences."}
    ],
    model="openai/gpt-4o-mini",
    stream=True
):
    if isinstance(chunk, dict) and "data" in chunk:
        print(chunk["data"], end="", flush=True)
    else:
        print(chunk, end="", flush=True)
print("\nStreaming complete!")
```

### Function Calling

Use function calling with OpenAI models:

```python
# Define functions
functions = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
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
                    "description": "The temperature unit to use"
                }
            },
            "required": ["location"]
        }
    }
]

response = client.chat(
    messages=[
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ],
    model="openai/gpt-4o-mini",
    additional_params={"functions": functions, "function_call": "auto"}
)

print("Function call response:", response)
```

## 2. Text Completions

### Basic Text Completion

Generate a simple text completion:

```python
response = client.completion(
    prompt="Once upon a time",
    model="openai/gpt-4o-mini"
)

print("Response:", response["data"])
print("Cost:", response["usage"]["cost"])
```

### Text Completion with Parameters

Use different parameters for text completion:

```python
response = client.completion(
    prompt="Write a recipe for chocolate cake",
    model="anthropic/claude-3-haiku",
    temperature=0.7,
    max_tokens=1000
)

print("Response:", response["data"])
```

### Streaming Text Completion

Stream the response for a better user experience:

```python
print("Streaming response:")
for chunk in client.completion(
    prompt="Explain quantum computing in simple terms",
    model="openai/gpt-4o-mini",
    stream=True
):
    if isinstance(chunk, dict) and "data" in chunk:
        print(chunk["data"], end="", flush=True)
    else:
        print(chunk, end="", flush=True)
print("\nStreaming complete!")
```

## 3. Embeddings

### Single Text Embedding

Generate embeddings for a single text:

```python
response = client.embeddings(
    text="Hello, world!",
    model="openai/text-embedding-ada-002"
)

print("Embedding dimensions:", len(response["data"][0]))
print("Cost:", response["usage"]["cost"])
print("First 5 values:", response["data"][0][:5])
```

### Multiple Text Embeddings

Generate embeddings for multiple texts:

```python
response = client.embeddings(
    text=["Hello, world!", "How are you?", "IndoxRouter is awesome!"],
    model="openai/text-embedding-ada-002"
)

print("Number of embeddings:", len(response["data"]))
print("Dimensions of each embedding:", len(response["data"][0]))
print("Cost:", response["usage"]["cost"])
```

### Using Different Embedding Models

Try different embedding models:

```python
# Cohere embeddings
response = client.embeddings(
    text="Hello, world!",
    model="cohere/embed-english-v3.0"
)

print("Cohere embedding dimensions:", len(response["data"][0]))
print("Cost:", response["usage"]["cost"])
```

## 4. Image Generation

### Basic Image Generation

Generate a simple image:

```python
response = client.images(
    prompt="A beautiful sunset over the ocean",
    model="openai/dall-e-3"
)

print("Image URL:", response["data"][0]["url"])
print("Cost:", response["usage"]["cost"])

# Display the image if in a notebook
from IPython.display import Image, display
display(Image(url=response["data"][0]["url"]))
```

### Multiple Images

Generate multiple images:

```python
response = client.images(
    prompt="A futuristic city with flying cars",
    model="openai/dall-e-3",
    n=2
)

print(f"Generated {len(response['data'])} images:")
for i, image in enumerate(response["data"]):
    print(f"Image {i+1} URL: {image['url']}")

# Display the images if in a notebook
from IPython.display import Image, display
for image in response["data"]:
    display(Image(url=image["url"]))
```

### Image Generation with Different Parameters

Use different parameters for image generation:

```python
response = client.images(
    prompt="A photorealistic portrait of a cyberpunk character",
    model="openai/dall-e-3",
    size="1024x1024",
    quality="hd",
    style="vivid"
)

print("Image URL:", response["data"][0]["url"])
print("Cost:", response["usage"]["cost"])

# Display the image if in a notebook
from IPython.display import Image, display
display(Image(url=response["data"][0]["url"]))
```

## 5. Model Information

### List All Models

Get information about all available models:

```python
models = client.models()

print("Available providers:")
for provider in models["providers"]:
    print(f"- {provider['name']} ({provider['id']})")
    print(f"  Capabilities: {', '.join(provider['capabilities'])}")
    print(f"  Models: {len(provider['models'])}")
```

### List Models for a Specific Provider

Get models for a specific provider:

```python
openai_models = client.models("openai")

print(f"OpenAI models ({len(openai_models['models'])}):")
for model in openai_models["models"]:
    print(f"- {model['name']} ({model['id']})")
    print(f"  Capabilities: {', '.join(model['capabilities'])}")
    if "pricing" in model:
        print(f"  Pricing: Input ${model['pricing']['input']}/1K tokens, Output ${model['pricing']['output']}/1K tokens")
```

### Get Specific Model Information

Get detailed information about a specific model:

```python
model_info = client.get_model_info("openai", "gpt-4o-mini")

print(f"Model: {model_info['name']} ({model_info['id']})")
print(f"Provider: {model_info['provider']}")
print(f"Description: {model_info['description']}")
print(f"Capabilities: {', '.join(model_info['capabilities'])}")
print(f"Input price: ${model_info['pricing']['input']}/1K tokens")
print(f"Output price: ${model_info['pricing']['output']}/1K tokens")
```

## 6. Usage Statistics

### Get Usage Statistics

Get usage statistics for the current user:

```python
usage = client.get_usage()

print("Usage statistics:")
print(f"Total requests: {usage['total_requests']}")
print(f"Total cost: ${usage['total_cost']}")
print(f"Remaining credits: ${usage['remaining_credits']}")

print("\nBreakdown by endpoint:")
for endpoint, stats in usage["endpoints"].items():
    print(f"- {endpoint}: {stats['requests']} requests, ${stats['cost']} cost")
```

## 7. Error Handling

### Handle Different Errors

Handle different types of errors gracefully:

```python
# Function to demonstrate error handling
def try_request(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ModelNotFoundError as e:
        print(f"Model not found: {e}")
    except ProviderNotFoundError as e:
        print(f"Provider not found: {e}")
    except InsufficientCreditsError as e:
        print(f"Insufficient credits: {e}")
    except InvalidParametersError as e:
        print(f"Invalid parameters: {e}")
    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
    except ProviderError as e:
        print(f"Provider error: {e}")
    except NetworkError as e:
        print(f"Network error: {e}")
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except IndoxRouterError as e:
        print(f"IndoxRouter error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

# Example: Model not found
result = try_request(client.chat,
    messages=[{"role": "user", "content": "Hello"}],
    model="nonexistent/model"
)

# Example: Invalid parameters
result = try_request(client.chat,
    messages="This is not a list of messages",  # Should be a list
    model="openai/gpt-4o-mini"
)

# Example: Provider not found
result = try_request(client.chat,
    messages=[{"role": "user", "content": "Hello"}],
    model="nonexistent/gpt-4o-mini"
)
```

## 8. Advanced Usage

### Using as a Context Manager

Use the client as a context manager to automatically close the session:

```python
with Client(api_key="your_api_key") as client:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        model="openai/gpt-4o-mini"
    )
    print("Response:", response["data"])
```

### Combining Different Capabilities

Combine different capabilities for more complex use cases:

```python
# Example: Generate text and then create an image based on it
completion_response = client.completion(
    prompt="Describe a fantastical creature that has never been seen before.",
    model="openai/gpt-4o-mini",
    max_tokens=200
)

creature_description = completion_response["data"]
print("Generated description:", creature_description)

# Now create an image based on the description
image_response = client.images(
    prompt=f"A detailed illustration of: {creature_description}",
    model="openai/dall-e-3"
)

print("Image URL:", image_response["data"][0]["url"])

# Display the image if in a notebook
from IPython.display import Image, display
display(Image(url=image_response["data"][0]["url"]))
```

### Semantic Search with Embeddings

Implement a simple semantic search using embeddings:

```python
import numpy as np

# Define some documents
documents = [
    "The quick brown fox jumps over the lazy dog.",
    "A fast auburn fox leaps above the sleepy canine.",
    "IndoxRouter provides a unified API for various AI providers.",
    "The API allows access to multiple AI models through a single interface.",
    "Paris is the capital of France and known for the Eiffel Tower.",
    "Rome is the capital of Italy and home to the Colosseum."
]

# Generate embeddings for all documents
embeddings_response = client.embeddings(
    text=documents,
    model="openai/text-embedding-ada-002"
)

document_embeddings = embeddings_response["data"]

# Function to calculate cosine similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Function to find most similar documents
def semantic_search(query, document_embeddings, documents, top_n=2):
    # Get embedding for the query
    query_embedding_response = client.embeddings(
        text=query,
        model="openai/text-embedding-ada-002"
    )
    query_embedding = query_embedding_response["data"][0]

    # Calculate similarities
    similarities = [
        cosine_similarity(query_embedding, doc_embedding)
        for doc_embedding in document_embeddings
    ]

    # Get top N results
    top_indices = np.argsort(similarities)[-top_n:][::-1]

    return [
        {"document": documents[i], "similarity": similarities[i]}
        for i in top_indices
    ]

# Example search
results = semantic_search("What is IndoxRouter?", document_embeddings, documents)

print("Search results:")
for i, result in enumerate(results):
    print(f"{i+1}. {result['document']} (Similarity: {result['similarity']:.4f})")
```

### RAG (Retrieval-Augmented Generation)

Implement a simple RAG system:

```python
# Using the same documents and embeddings from the previous example

def rag_query(query, document_embeddings, documents, top_n=2):
    # Get relevant documents
    relevant_docs = semantic_search(query, document_embeddings, documents, top_n)

    # Create a context from the relevant documents
    context = "\n".join([doc["document"] for doc in relevant_docs])

    # Create a prompt with the context
    prompt = f"""
    Context information:
    {context}

    Based on the context information, please answer the following question:
    {query}
    """

    # Generate a response
    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer the question based only on the provided context."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]

# Example RAG query
answer = rag_query("What does IndoxRouter do?", document_embeddings, documents)
print("RAG Answer:", answer)
```

## 9. Troubleshooting and Debugging

### Enable Debug Mode

Enable debug logging to see detailed information about requests and responses:

```python
# Enable debug logging
client.enable_debug()

# Try a request
try:
    response = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="openai/gpt-4o-mini"
    )
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
```

### Testing Server Connection

Use the `test_connection` method to verify that your server is accessible and properly configured:

```python
# Test the connection to the server
connection_info = client.test_connection()
print(f"Connection status: {connection_info['status']}")

if connection_info['status'] == 'connected':
    print(f"Server URL: {connection_info['url']}")
    print(f"Status code: {connection_info['status_code']}")
    if connection_info['server_info']:
        print(f"Server info: {connection_info['server_info']}")
else:
    print(f"Error: {connection_info['error']}")
    print(f"Error type: {connection_info['error_type']}")
```

### Common Issues and Solutions

#### "Resource not found" Error

If you see a "Resource not found" error, it usually means one of the following:

1. The server is not running. Make sure your IndoxRouter server is up and running:

   ```bash
   cd indoxRouter_server
   python -m main
   ```

2. The base URL is incorrect. Check the URL in your environment:

   ```python
   print(f"Using base URL: {client.base_url}")
   ```

3. The API endpoint path is incorrect. The client automatically adds the API version prefix, but you can check the full URL in the debug logs.

#### Server Errors (500 Internal Server Error)

If you encounter a 500 Internal Server Error:

1. Check the server logs for detailed error information:

   ```bash
   # Look at the server logs
   cd indoxRouter_server
   tail -f logs/server.log
   ```

2. Verify that the provider service is available and properly configured on the server.

3. Check if your request parameters are valid for the specific model you're using.

4. Try with a different model or provider to see if the issue is specific to one provider.

5. If you see a "too many values to unpack" error, it might be related to how the server parses the model string. The client now automatically formats the model string to be compatible with the server, but you can try different formats:

   ```python
   # Try using a different model format
   try:
       # First attempt with standard format
       response = client.chat(
           messages=[{"role": "user", "content": "Hello"}],
           model="openai/gpt-4o-mini"
       )
   except ProviderError as e:
       if "too many values to unpack" in str(e):
           # Try with a different provider/model
           response = client.chat(
               messages=[{"role": "user", "content": "Hello"}],
               model="anthropic/claude-3-haiku"
           )
   ```

6. If you see an error about "unexpected keyword argument 'return_generator'", it means the server is using an older version of the OpenAI API or a different implementation that doesn't support this parameter. The client automatically filters out this parameter, but you might need to update your server:

   ```python
   # Enable debug mode to see what parameters are being sent
   client.enable_debug()

   # Try a simpler request with minimal parameters
   response = client.chat(
       messages=[{"role": "user", "content": "Hello"}],
       model="openai/gpt-4o-mini",
       # Avoid using additional parameters that might cause issues
   )
   ```

#### Authentication Errors

If you see an "Authentication failed" error:

1. Make sure your API key is correct:

   ```python
   # First few characters of the API key (for security)
   print(f"API key starts with: {client.api_key[:5]}...")
   ```

2. Check if your API key is valid on the server.

#### Connection Errors

If you can't connect to the server:

1. Use the `test_connection` method to diagnose the issue:

   ```python
   connection_info = client.test_connection()
   print(f"Connection status: {connection_info}")
   ```

2. Check for firewall or network issues.

#### Insufficient Credits

If you see an "Insufficient credits" error:

1. Check your current credit balance:

   ```python
   try:
      usage = client.get_usage()
      print(f"Remaining credits: ${usage['remaining_credits']}")
   except Exception as e:
      print(f"Error getting usage: {e}")
   ```

2. Contact your administrator to add more credits to your account.

## 10. Cleanup

Don't forget to close the client when you're done:

```python
client.close()
print("Client closed successfully!")
```

## Conclusion

This cookbook has demonstrated how to use the IndoxRouter client to interact with various AI providers through a unified API. You can now use these examples as a starting point for your own applications.

For more information, refer to the [IndoxRouter documentation](https://docs.indoxrouter.com).
