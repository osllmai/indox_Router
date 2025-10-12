# Basic Examples

This page provides some basic examples of using the IndoxRouter Client for common tasks.

## Chat Completion Example

```python
from indoxrouter import Client

# Initialize the client
with Client(api_key="your_api_key") as client:
    # Generate a chat completion
    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is machine learning and why is it important?"}
        ],
        model="openai/gpt-4o-mini",
        temperature=0.7
    )

    # Print the response
    print(response["data"])
```

## Text Completion Example

```python
from indoxrouter import Client

# Initialize the client
with Client(api_key="your_api_key") as client:
    # Generate a text completion
    response = client.completion(
        prompt="Write a short poem about artificial intelligence:",
        model="openai/gpt-4o-mini",
        max_tokens=100
    )

    # Print the response
    print(response["data"])
```

## Embedding Example

```python
from indoxrouter import Client

# Initialize the client
with Client(api_key="your_api_key") as client:
    # Generate embeddings for multiple texts
    response = client.embeddings(
        text=[
            "Machine learning is a branch of artificial intelligence.",
            "Natural language processing helps computers understand human language."
        ],
        model="openai/text-embedding-3-small"
    )

    # Print the first few dimensions of each embedding
    for i, embedding_data in enumerate(response["data"]):
        embedding = embedding_data["embedding"]
        print(f"Embedding {i+1} (first 5 dimensions): {embedding[:5]}")
        print(f"Embedding {i+1} dimensions: {len(embedding)}")
```

## Vision & Image Analysis Example

```python
from indoxrouter import Client
import base64

# Initialize the client
with Client(api_key="your_api_key") as client:
    # Read and encode an image
    with open("photo.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')

    # Analyze the image with a vision-capable model
    response = client.chat(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What's in this image? Please describe it in detail."
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
        ],
        model="openai/gpt-4o"
    )

    # Print the image description
    print(response["data"])
```

## Image Generation Example

```python
from indoxrouter import Client

# Initialize the client
with Client(api_key="your_api_key") as client:
    # Generate an image
    response = client.images(
        prompt="A futuristic city with flying cars and towering skyscrapers at sunset",
        model="openai/dall-e-3",
        size="1024x1024"
    )

    # Print the image URL
    print(f"Generated image URL: {response['data'][0]['url']}")
```

## Model Information Example

```python
from indoxrouter import Client
import json

# Initialize the client
with Client(api_key="your_api_key") as client:
    # Get information about all available models
    providers = client.models()

    # Print information about each provider
    for provider in providers:
        print(f"Provider: {provider['id']} ({provider['name']})")
        print(f"Description: {provider.get('description', 'No description')}")
        print(f"Models available: {len(provider['models'])}")
        print("Model IDs:")
        for model in provider['models']:
            print(f"  - {model['id']}")
        print()

    # Get details about a specific model
    model_info = client.get_model_info("openai", "gpt-4o-mini")
    print(f"Model: {model_info['id']}")
    print(f"Description: {model_info.get('description', 'No description')}")
    print(f"Capabilities: {', '.join(model_info.get('capabilities', []))}")
    print(f"Max tokens: {model_info.get('max_tokens', 'Unknown')}")
```
