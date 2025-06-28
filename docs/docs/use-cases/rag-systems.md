# Building RAG Systems with IndoxRouter

Retrieval-Augmented Generation (RAG) is a powerful approach that combines the benefits of retrieving relevant information from a knowledge base with the capabilities of large language models. This guide demonstrates how to build effective RAG systems using IndoxRouter.

## What is RAG?

RAG enhances language model responses by:

1. Breaking down documents into smaller chunks
2. Creating vector embeddings for each chunk
3. Storing these embeddings in a vector database
4. When a query is received, finding the most relevant chunks
5. Using these chunks as context for the language model to generate an answer

This approach helps ground model responses in specific knowledge and reduces hallucinations.

## Basic RAG Implementation

Here's a simple implementation of a RAG system using IndoxRouter:

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from indoxrouter import Client

# Initialize client
client = Client(api_key="your_api_key")

# Sample documents - in a real application, you would load these from files
documents = [
    "The Python programming language was created by Guido van Rossum and first released in 1991.",
    "Python is known for its readability and simplicity, making it an excellent language for beginners.",
    "Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming.",
    "The name Python comes from Monty Python, not the snake.",
    "Popular Python frameworks include Django and Flask for web development, and NumPy and Pandas for data analysis."
]

# Step 1: Generate embeddings for the documents
doc_response = client.embeddings(
    text=documents,
    model="openai/text-embedding-3-small"
)

# Convert to numpy array for easier processing
doc_embeddings = np.array([item["embedding"] for item in doc_response["data"]])

# Step 2: Process a user query
query = "Why is Python good for beginners?"

# Generate embedding for the query
query_response = client.embeddings(
    text=query,
    model="openai/text-embedding-3-small"
)
query_embedding = np.array(query_response["data"][0]["embedding"])

# Step 3: Find the most relevant documents
similarities = cosine_similarity([query_embedding], doc_embeddings)[0]

# Get the top 2 most relevant documents
top_indices = np.argsort(similarities)[-2:][::-1]
relevant_docs = [documents[i] for i in top_indices]
context = "\n".join(relevant_docs)

# Step 4: Generate an answer using the relevant documents as context
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Answer the question based on the provided context only."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ],
    model="openai/gpt-4o-mini"
)

# Print the answer
print(f"Question: {query}")
print(f"Answer: {response['data']")
```

## Advanced RAG Implementation

For real-world applications, you'll need a more sophisticated approach:

```python
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from indoxrouter import Client

class RAGSystem:
    def __init__(self, api_key, embed_model="openai/text-embedding-3-small", llm_model="openai/gpt-4o-mini"):
        """Initialize the RAG system with API key and models."""
        self.client = Client(api_key=api_key)
        self.embed_model = embed_model
        self.llm_model = llm_model
        self.document_store = []
        self.embeddings = []

    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Split text into overlapping chunks."""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if len(chunk) < 100:  # Skip very small chunks
                continue
            chunks.append(chunk)
        return chunks

    def add_document(self, doc_id, text, metadata=None):
        """Process and add a document to the RAG system."""
        # Split document into chunks
        chunks = self.chunk_text(text)

        # Create embeddings for each chunk
        response = self.client.embeddings(
            text=chunks,
            model=self.embed_model
        )

        # Store chunks and their embeddings
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            embedding = response["data"][i]["embedding"]
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "chunk_index": i,
                "total_chunks": len(chunks)
            })

            self.document_store.append({
                "id": chunk_id,
                "text": chunk,
                "metadata": chunk_metadata
            })
            self.embeddings.append(embedding)

        print(f"Added document {doc_id} with {len(chunks)} chunks")

    def query(self, question, top_k=3):
        """Process a query and return the answer with supporting evidence."""
        # Generate embedding for the query
        query_response = self.client.embeddings(
            text=question,
            model=self.embed_model
        )
        query_embedding = np.array(query_response["data"][0]["embedding"])

        # Calculate similarities with all document chunks
        doc_embeddings = np.array(self.embeddings)
        similarities = cosine_similarity([query_embedding], doc_embeddings)[0]

        # Get top K most relevant chunks
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        relevant_chunks = [self.document_store[i] for i in top_indices]

        # Build context from relevant chunks
        context_parts = []
        for i, chunk in enumerate(relevant_chunks):
            context_parts.append(f"[Document {i+1}] {chunk['text']}")

        context = "\n\n".join(context_parts)

        # Generate answer using context
        system_message = (
            "You are a helpful assistant. Answer the user's question based ONLY on the provided context. "
            "If the answer cannot be determined from the context, say 'I don't have enough information to answer that question.'"
        )

        response = self.client.chat(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Context:\n\n{context}\n\nQuestion: {question}"}
            ],
            model=self.llm_model
        )

        answer = response["data"]

        # Return answer along with supporting evidence
        return {
            "question": question,
            "answer": answer,
            "sources": relevant_chunks,
            "similarities": [similarities[i] for i in top_indices]
        }

# Usage example
rag = RAGSystem(api_key="your_api_key")

# Add some documents
rag.add_document("python_basics", """
Python is a high-level, interpreted programming language with dynamic semantics.
Its high-level built in data structures, combined with dynamic typing and dynamic binding,
make it very attractive for Rapid Application Development, as well as for use as a
scripting or glue language to connect existing components together.
""")

rag.add_document("python_features", """
Python's simple, easy to learn syntax emphasizes readability and therefore reduces
the cost of program maintenance. Python supports modules and packages, which encourages
program modularity and code reuse. The Python interpreter and the extensive standard
library are available in source or binary form without charge for all major platforms.
""")

# Query the system
result = rag.query("What makes Python good for development?")
print(f"Question: {result['question']}")
print(f"Answer: {result['answer']}")
print("\nSources:")
for i, source in enumerate(result['sources']):
    print(f"{i+1}. {source['metadata']['doc_id']} (similarity: {result['similarities'][i]:.3f})")
```

## Best Practices

### 1. Document Preprocessing

- **Clean text**: Remove unnecessary formatting, headers, footers
- **Normalize text**: Handle different encodings, special characters
- **Structure preservation**: Maintain important formatting like lists, tables

### 2. Chunking Strategies

- **Fixed-size chunking**: Simple but may break context
- **Sentence-based chunking**: Preserves semantic boundaries
- **Paragraph-based chunking**: Good for structured documents
- **Overlapping chunks**: Helps maintain context across boundaries

### 3. Embedding Optimization

- **Choose appropriate models**: Balance quality vs speed
- **Batch processing**: Process multiple texts together for efficiency
- **Caching**: Store embeddings to avoid recomputation

### 4. Retrieval Tuning

- **Adjust top_k**: Find the right balance of context vs noise
- **Similarity thresholds**: Filter out irrelevant results
- **Hybrid search**: Combine semantic and keyword search

### 5. Response Generation

- **Clear instructions**: Tell the model how to use the context
- **Context formatting**: Structure the retrieved information clearly
- **Fallback handling**: Handle cases where no relevant context is found

## Integration with Vector Databases

For production systems, consider using dedicated vector databases:

```python
# Example with Pinecone
import pinecone
from indoxrouter import Client

class ProductionRAG:
    def __init__(self, api_key, pinecone_api_key, pinecone_env):
        self.client = Client(api_key=api_key)

        # Initialize Pinecone
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        self.index = pinecone.Index("rag-index")

    def add_document(self, doc_id, text):
        # Generate embeddings
        response = self.client.embeddings(
            text=text,
            model="openai/text-embedding-3-small"
        )

        # Store in Pinecone
        self.index.upsert([(
            doc_id,
            response["data"][0]["embedding"],
            {"text": text}
        )])

    def query(self, question, top_k=3):
        # Generate query embedding
        query_response = self.client.embeddings(
            text=question,
            model="openai/text-embedding-3-small"
        )

        # Search Pinecone
        results = self.index.query(
            vector=query_response["data"][0]["embedding"],
            top_k=top_k,
            include_metadata=True
        )

        # Build context
        context = "\n\n".join([match.metadata["text"] for match in results.matches])

        # Generate answer
        response = self.client.chat(
            messages=[
                {"role": "system", "content": "Answer based on the provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ],
            model="openai/gpt-4o-mini"
        )

        return response["data"]
```

This approach provides scalable, production-ready RAG systems with IndoxRouter.
