"""
Example of using the indoxRouter client for chat completions.
"""

import os
import sys
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
    # Get available providers and models
    providers = client.models()
    print("Available providers:")
    for provider in providers:
        print(f"- {provider['name']} ({provider['id']})")
        print(f"  Capabilities: {', '.join(provider['capabilities'])}")
        print(f"  Models: {len(provider['models'])}")

    # Get a specific provider
    openai_provider = client.models("openai")
    print("\nOpenAI models:")
    for model in openai_provider["models"]:
        print(f"- {model['name']} ({model['id']})")
        print(f"  Capabilities: {', '.join(model['capabilities'])}")

    # Send a chat completion request
    print("\nSending chat completion request...")
    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a short joke."},
        ],
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=50,
    )

    # Print the response
    print("\nChat completion response:")
    print(f"Model: {response.get('model')}")
    print(f"Provider: {response.get('provider')}")
    print(f"Response: {response['choices'][0]['message']['content']}")
    print(f"Tokens: {response.get('usage', {}).get('total_tokens', 'N/A')}")

    # Send a streaming chat completion request
    print("\nSending streaming chat completion request...")
    print("Response: ", end="", flush=True)
    for chunk in client.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me another short joke."},
        ],
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=50,
        stream=True,
    ):
        if "choices" in chunk and len(chunk["choices"]) > 0:
            content = chunk["choices"][0].get("delta", {}).get("content", "")
            print(content, end="", flush=True)
    print("\n")

except Exception as e:
    print(f"Error: {e}")
finally:
    # Close the client
    client.close()
