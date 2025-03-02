#!/usr/bin/env python3
"""
New Providers Example

This script demonstrates how to use the new providers added to IndoxRouter:
- Llama
- NVIDIA
- Deepseek
- Databricks

Make sure to set the appropriate API keys in your environment variables before running this script.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the indoxRouter package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indoxRouter.client import Client

# Load environment variables from .env file
load_dotenv()

# Initialize the client with your API key
# You can get an API key by creating a user and generating an API key
client = Client(api_key=os.environ.get("INDOX_API_KEY", "your_api_key"))

# The prompt to use for all examples
PROMPT = "Explain the concept of quantum computing in simple terms."


def print_response(provider, model, response):
    """Print the response in a formatted way."""
    print(f"\n{'=' * 80}")
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"{'=' * 80}")
    print(f"Response: {response['text']}")
    print(f"Cost: ${response['cost']:.6f}")
    print(f"Input tokens: {response['usage']['input_tokens']}")
    print(f"Output tokens: {response['usage']['output_tokens']}")
    print(f"{'=' * 80}\n")


def main():
    """Run the examples for each provider."""
    print("IndoxRouter New Providers Example")
    print("=================================")

    # Example 1: Llama
    try:
        print("\nGenerating response using Llama...")
        response_llama = client.generate(
            provider="llama",
            model="meta-llama-3-70b-instruct",
            prompt=PROMPT,
            max_tokens=500,
        )
        print_response("Llama", "meta-llama-3-70b-instruct", response_llama)
    except Exception as e:
        print(f"Error with Llama provider: {str(e)}")

    # Example 2: NVIDIA
    try:
        print("\nGenerating response using NVIDIA...")
        response_nvidia = client.generate(
            provider="nvidia",
            model="nvidia-tensorrt-llm-mixtral-8x7b-instruct",
            prompt=PROMPT,
            max_tokens=500,
        )
        print_response(
            "NVIDIA", "nvidia-tensorrt-llm-mixtral-8x7b-instruct", response_nvidia
        )
    except Exception as e:
        print(f"Error with NVIDIA provider: {str(e)}")

    # Example 3: Deepseek
    try:
        print("\nGenerating response using Deepseek...")
        response_deepseek = client.generate(
            provider="deepseek",
            model="deepseek-llm-67b-chat",
            prompt=PROMPT,
            max_tokens=500,
        )
        print_response("Deepseek", "deepseek-llm-67b-chat", response_deepseek)
    except Exception as e:
        print(f"Error with Deepseek provider: {str(e)}")

    # Example 4: Databricks
    try:
        print("\nGenerating response using Databricks...")
        response_databricks = client.generate(
            provider="databricks",
            model="databricks-dbrx-instruct",
            prompt=PROMPT,
            max_tokens=500,
        )
        print_response("Databricks", "databricks-dbrx-instruct", response_databricks)
    except Exception as e:
        print(f"Error with Databricks provider: {str(e)}")

    # Example 5: Compare all providers
    print("\nComparing all providers...")
    providers = [
        ("llama", "meta-llama-3-70b-instruct"),
        ("nvidia", "nvidia-tensorrt-llm-mixtral-8x7b-instruct"),
        ("deepseek", "deepseek-llm-67b-chat"),
        ("databricks", "databricks-dbrx-instruct"),
    ]

    results = []
    for provider, model in providers:
        try:
            start_time = time.time()
            response = client.generate(
                provider=provider,
                model=model,
                prompt=PROMPT,
                max_tokens=100,  # Shorter response for comparison
            )
            end_time = time.time()

            results.append(
                {
                    "provider": provider,
                    "model": model,
                    "cost": response["cost"],
                    "time": end_time - start_time,
                    "tokens": response["usage"]["output_tokens"],
                }
            )
        except Exception as e:
            print(f"Error with {provider} provider: {str(e)}")

    # Print comparison table
    print("\nProvider Comparison:")
    print(
        f"{'Provider':<15} {'Model':<40} {'Cost':<10} {'Time (s)':<10} {'Tokens':<10}"
    )
    print("-" * 85)

    for result in results:
        print(
            f"{result['provider']:<15} {result['model']:<40} ${result['cost']:<9.6f} {result['time']:<10.2f} {result['tokens']:<10}"
        )


if __name__ == "__main__":
    main()
