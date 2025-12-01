# Embeddings

Embeddings are vector representations of text that capture semantic meaning, making them useful for similarity search, clustering, classification, and retrieval applications. This guide covers how to use the embeddings feature of indoxhub.

## Basic Usage

The simplest way to generate embeddings is with the `embeddings()` method:

```python
from indoxhub import Client

client = Client(api_key="your_api_key")

# Generate embeddings for a single text
response = client.embeddings(
    text="Machine learning is a field of study that gives computers the ability to learn without being explicitly programmed.",
    model="openai/text-embedding-3-small"
)

# Print the embedding dimensions
print(f"Embedding dimensions: {len(response['data'][0]['embedding'])}")
print(f"First few dimensions: {response['data'][0]['embedding'][:5]}")
```

## Processing Multiple Texts

You can generate embeddings for multiple texts in a single request by passing a list of strings:

```python
from indoxhub import Client

client = Client(api_key="your_api_key")

# Generate embeddings for multiple texts
response = client.embeddings(
    text=[
        "Artificial intelligence is revolutionizing industries worldwide.",
        "Natural language processing helps computers understand human language.",
        "Machine learning algorithms improve with more training data."
    ],
    model="openai/text-embedding-3-small"
)

# Print information about the embeddings
for i, item in enumerate(response["data"]):
    embedding = item["embedding"]
    print(f"Text {i+1}: Dimensions: {len(embedding)}")
```

## Model Selection

You can select different embedding models from various providers:

```python
# OpenAI
openai_response = client.embeddings(
    text="Example text for embedding",
    model="openai/text-embedding-3-small"
)

# OpenAI larger model
openai_large_response = client.embeddings(
    text="Example text for embedding",
    model="openai/text-embedding-3-large"
)

# Google
google_response = client.embeddings(
    text="Example text for embedding",
    model="google/text-embedding-gecko"
)

# Mistral
mistral_response = client.embeddings(
    text="Example text for embedding",
    model="mistral/mistral-embed"
)
```

## BYOK (Bring Your Own Key) Support

indoxhub supports BYOK for embeddings, allowing you to use your own API keys for AI providers:

```python
# Use your own OpenAI API key for embeddings
response = client.embeddings(
    text="Machine learning is transforming industries",
    model="openai/text-embedding-3-small",
    byok_api_key="sk-your-openai-key-here"
)

# Use your own Google API key for embeddings
response = client.embeddings(
    text="Natural language processing examples",
    model="google/text-embedding-gecko",
    byok_api_key="your-google-api-key-here"
)

# Use your own Mistral API key for embeddings
response = client.embeddings(
    text="AI and machine learning concepts",
    model="mistral/mistral-embed",
    byok_api_key="your-mistral-api-key-here"
)
```

### BYOK Benefits for Embeddings

- **No Credit Deduction**: Your indoxhub credits remain unchanged
- **No Rate Limiting**: Bypass platform rate limits
- **Direct Provider Access**: Connect directly to your provider accounts
- **Cost Control**: Pay providers directly at their rates
- **Full Features**: Access to all provider-specific embedding features
- **Higher Quality**: Use provider's native embedding capabilities

## Response Format

The response from the embeddings method follows this structure:

```python
{
    "id": "embd-123456789",
    "object": "embedding",
    "created": 1684936116,
    "model": "openai/text-embedding-3-small",
    "data": [
        {
            "embedding": [0.002345, -0.012345, 0.123456, ...],  # Vector of n dimensions
            "index": 0
        },
        # More items if multiple texts were provided
    ],
    "usage": {
        "prompt_tokens": 10,
        "total_tokens": 10
    }
}
```

## Working with Embeddings

### Calculating Similarity

Once you have embeddings, you can calculate similarity between them using cosine similarity:

```python
import numpy as np
from scipy.spatial.distance import cosine

def cosine_similarity(a, b):
    return 1 - cosine(a, b)

# Get embeddings for two texts
response = client.embeddings(
    text=[
        "The weather is quite nice today.",
        "Today's weather is pleasant."
    ],
    model="openai/text-embedding-3-small"
)

# Extract the embedding vectors
embedding1 = response["data"][0]["embedding"]
embedding2 = response["data"][1]["embedding"]

# Calculate similarity
similarity = cosine_similarity(embedding1, embedding2)
print(f"Similarity: {similarity:.4f}")  # Higher value means more similar
```

### Building a Simple RAG System

Here's a basic example of using embeddings for a simple retrieval-augmented generation (RAG) system:

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Sample knowledge base
documents = [
    "Machine learning is a field of study that gives computers the ability to learn without being explicitly programmed.",
    "Natural language processing is a subfield of linguistics, computer science, and artificial intelligence.",
    "Neural networks are computing systems inspired by the biological neural networks in animal brains.",
    "Deep learning is part of a broader family of machine learning methods based on artificial neural networks.",
    "Reinforcement learning is the training of machine learning models to make a sequence of decisions."
]

client = Client(api_key="your_api_key")

# Step 1: Generate embeddings for our knowledge base
docs_response = client.embeddings(
    text=documents,
    model="openai/text-embedding-3-small"
)

# Extract embeddings
doc_embeddings = np.array([item["embedding"] for item in docs_response["data"]])

# Step 2: Process a query
query = "How do computers learn without explicit programming?"

# Generate embedding for the query
query_response = client.embeddings(
    text=query,
    model="openai/text-embedding-3-small"
)
query_embedding = np.array(query_response["data"][0]["embedding"])

# Step 3: Find the most similar document
similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
most_similar_index = np.argmax(similarities)
most_similar_doc = documents[most_similar_index]

print(f"Query: {query}")
print(f"Most relevant document: {most_similar_doc}")
print(f"Similarity score: {similarities[most_similar_index]:.4f}")

# Step 4: Generate an answer using the most relevant document as context
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer the question."},
        {"role": "user", "content": f"Context: {most_similar_doc}\n\nQuestion: {query}"}
    ],
    model="openai/gpt-4o-mini"
)

print("\nGenerated Answer:")
print(response["choices"][0]["message"]["content"])
```

## Advanced Usage

### Chunking Large Documents

For practical applications, you'll often need to chunk large documents before creating embeddings:

```python
def chunk_text(text, chunk_size=1000, overlap=100):
    """Split text into overlapping chunks."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if len(chunk) < 100:  # Skip very small chunks at the end
            continue
        chunks.append(chunk)
    return chunks

# Example usage
large_document = """
[Your long document text here...]
"""

chunks = chunk_text(large_document)
print(f"Document split into {len(chunks)} chunks")

# Generate embeddings for each chunk
chunk_response = client.embeddings(
    text=chunks,
    model="openai/text-embedding-3-small"
)

chunk_embeddings = [item["embedding"] for item in chunk_response["data"]]
```

### Storing Embeddings

For production applications, you would typically store embeddings in a vector database:

```python
# Pseudocode for storing embeddings in a vector database
# Replace with actual implementation for your chosen database

# Generate embeddings
response = client.embeddings(
    text=documents,
    model="openai/text-embedding-3-small"
)

# Store in vector database
for i, doc in enumerate(documents):
    vector = response["data"][i]["embedding"]
    doc_id = f"doc_{i}"
    vector_db.insert(
        id=doc_id,
        vector=vector,
        metadata={"text": doc}
    )
```

## Best Practices

1. **Choose the right model**: Different embedding models have different dimensions and performance characteristics
2. **Normalize text**: Clean and normalize text before generating embeddings
3. **Chunk large documents**: Split large texts into smaller chunks
4. **Cache embeddings**: Store embeddings to avoid regenerating them for the same content
5. **Use appropriate similarity metrics**: Cosine similarity is common, but other metrics might be better for specific use cases
6. **Consider dimensionality reduction**: For very large collections, consider techniques like PCA to reduce embedding dimensions

_Last updated: Nov 16, 2025_