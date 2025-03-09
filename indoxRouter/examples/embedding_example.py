"""
Example of using the indoxRouter client for embeddings.
"""

import os
import sys
import numpy as np
from dotenv import load_dotenv

# Add the parent directory to the path so we can import indoxrouter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indoxrouter import Client

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.environ.get("INDOXROUTER_API_KEY")
if not api_key:
    print("Please set the INDOXROUTER_API_KEY environment variable")
    sys.exit(1)

# Initialize the client
client = Client(api_key=api_key)

try:
    # Define some texts to embed
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "The five boxing wizards jump quickly.",
        "How vexingly quick daft zebras jump!",
    ]

    # Get embeddings for the texts
    print("Getting embeddings...")
    response = client.embeddings(
        text=texts,
        provider="openai",
        model="text-embedding-ada-002",
    )

    # Print the response
    print("\nEmbedding response:")
    print(f"Model: {response.get('model')}")
    print(f"Provider: {response.get('provider')}")
    print(f"Dimensions: {response.get('dimensions')}")
    print(f"Number of embeddings: {len(response.get('embeddings', []))}")
    print(f"Tokens: {response.get('usage', {}).get('total_tokens', 'N/A')}")

    # Calculate cosine similarity between embeddings
    embeddings = response.get("embeddings", [])
    if embeddings:
        print("\nCalculating cosine similarity between embeddings...")

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = cosine_similarity(embeddings[i], embeddings[j])
                print(f"Similarity between text {i+1} and text {j+1}: {similarity:.4f}")

except Exception as e:
    print(f"Error: {e}")
finally:
    # Close the client
    client.close()
