# Embeddings Example

This example demonstrates how to use the IndoxRouter client to generate embeddings from various AI providers.

## Basic Embeddings

```python
from indoxrouter import Client

# Initialize client with API key
client = Client(api_key="your_api_key")

# Generate embeddings for a single text
response = client.embeddings(
    text="This is a sample text to embed.",
    provider="openai",
    model="text-embedding-ada-002"
)

# Print the response
print(f"Dimensions: {response['dimensions']}")
print(f"Embedding (first 5 values): {response['embeddings'][0][:5]}")
```

## Batch Embeddings

```python
import numpy as np
from indoxrouter import Client

# Initialize client with API key
client = Client(api_key="your_api_key")

# Define some texts to embed
texts = [
    "The quick brown fox jumps over the lazy dog.",
    "The five boxing wizards jump quickly.",
    "How vexingly quick daft zebras jump!",
]

# Generate embeddings for multiple texts
response = client.embeddings(
    text=texts,
    provider="openai",
    model="text-embedding-ada-002"
)

# Print the response
print(f"Number of embeddings: {len(response['embeddings'])}")
print(f"Dimensions: {response['dimensions']}")

# Calculate cosine similarity between embeddings
embeddings = response["embeddings"]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

for i in range(len(embeddings)):
    for j in range(i + 1, len(embeddings)):
        similarity = cosine_similarity(embeddings[i], embeddings[j])
        print(f"Similarity between text {i+1} and text {j+1}: {similarity:.4f}")
```

## Using Different Providers

### OpenAI

```python
response = client.embeddings(
    text="This is a sample text to embed.",
    provider="openai",
    model="text-embedding-ada-002"
)
```

### Cohere

```python
response = client.embeddings(
    text="This is a sample text to embed.",
    provider="cohere",
    model="embed-english-v3.0"
)
```

### Google

```python
response = client.embeddings(
    text="This is a sample text to embed.",
    provider="google",
    model="embedding-001"
)
```

### Mistral

```python
response = client.embeddings(
    text="This is a sample text to embed.",
    provider="mistral",
    model="mistral-embed"
)
```

## Error Handling

```python
from indoxrouter import Client
from indoxrouter.exceptions import ModelNotFoundError, ProviderNotFoundError

try:
    client = Client(api_key="your_api_key")
    response = client.embeddings(
        text="This is a sample text to embed.",
        provider="nonexistent",
        model="nonexistent-model"
    )
except ProviderNotFoundError as e:
    print(f"Provider not found: {e}")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
```
