"""
Example of using streaming responses with indoxRouter in a UI.
This example shows how to use the generator to yield chunks of the response.
"""

import sys
import os

# Add the parent directory to the path so we can import indoxRouter
module_path = os.path.abspath("..")
if module_path not in sys.path:
    sys.path.append(module_path)

from indoxRouter import Client
from indoxRouter.models import ChatMessage

# Initialize the client
client = Client(api_key="dev-api-key")


def simple_streaming_example():
    """
    Simple example of using the generator to yield chunks of the response.
    """
    print("Example: Simple Streaming with Generator")

    # Define the prompt
    prompt = "Write a short story about a robot learning to paint."

    print("\nPrompt:", prompt)
    print("\nResponse:")

    # Make the streaming request with return_generator=True
    generator = client.completion(
        prompt=prompt,
        model="openai/gpt-4o-mini",
        temperature=0.7,
        max_tokens=300,
        stream=True,
        return_generator=True,
    )

    # Iterate through the generator and print each chunk
    response_text = ""
    usage_info = None

    for chunk in generator:
        # Check if this is the final usage info chunk
        if isinstance(chunk, dict) and chunk.get("is_usage_info"):
            usage_info = chunk
            continue  # Skip printing this chunk

        # Otherwise, it's a text chunk
        response_text += chunk
        print(chunk, end="", flush=True)

    print("\n\nStreaming complete!")

    # Print usage information if available
    if usage_info:
        print("\nUsage Information:")
        print(f"Prompt tokens: {usage_info['usage']['tokens_prompt']}")
        print(f"Completion tokens: {usage_info['usage']['tokens_completion']}")
        print(f"Total tokens: {usage_info['usage']['tokens_total']}")
        print(f"Cost: ${usage_info['cost']:.6f}")
        if usage_info.get("finish_reason"):
            print(f"Finish reason: {usage_info['finish_reason']}")


def ui_streaming_example():
    """
    Example of how you might use the generator in a UI.
    This is a simplified example - in a real UI, you would use a framework like Flask, FastAPI, etc.
    """
    print("Example: UI Streaming with Generator")

    # Define the messages
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Explain quantum computing in simple terms."),
    ]

    print("\nMessages:", [f"{msg.role}: {msg.content}" for msg in messages])
    print("\nResponse:")

    # Make the streaming request with return_generator=True
    generator = client.chat(
        messages=messages,
        model="openai/gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        stream=True,
        return_generator=True,
    )

    # In a real UI, you would yield each chunk to the client
    # Here we just simulate it by printing each chunk
    response_text = ""
    usage_info = None

    for chunk in generator:
        # Check if this is the final usage info chunk
        if isinstance(chunk, dict) and chunk.get("is_usage_info"):
            usage_info = chunk
            continue  # Skip printing this chunk

        # Otherwise, it's a text chunk
        response_text += chunk
        print(chunk, end="", flush=True)

    print("\n\nStreaming complete!")

    # Print usage information if available
    if usage_info:
        print("\nUsage Information:")
        print(f"Prompt tokens: {usage_info['usage']['tokens_prompt']}")
        print(f"Completion tokens: {usage_info['usage']['tokens_completion']}")
        print(f"Total tokens: {usage_info['usage']['tokens_total']}")
        print(f"Cost: ${usage_info['cost']:.6f}")
        if usage_info.get("finish_reason"):
            print(f"Finish reason: {usage_info['finish_reason']}")


def fastapi_example_code():
    """
    Example code for using the generator with FastAPI.
    This is just example code, not meant to be run.
    """
    print("Example FastAPI Code:")
    print(
        """
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from indoxRouter import Client
from indoxRouter.models import ChatMessage
import json

app = FastAPI()
client = Client(api_key="your_api_key")

@app.post("/stream-chat/")
async def stream_chat(request_data: dict):
    messages = [ChatMessage(**msg) for msg in request_data["messages"]]
    
    async def generate():
        generator = client.chat(
            messages=messages,
            model=request_data["model"],
            temperature=request_data.get("temperature", 0.7),
            max_tokens=request_data.get("max_tokens", 500),
            stream=True,
            return_generator=True
        )
        
        usage_info = None
        for chunk in generator:
            # Check if this is the final usage info chunk
            if isinstance(chunk, dict) and chunk.get("is_usage_info"):
                # Store usage info to send at the end
                usage_info = chunk
                continue
            
            # Otherwise, it's a text chunk
            yield f"data: {json.dumps({'text': chunk})}\\n\\n"
        
        # After all text chunks, send the usage info as a special event
        if usage_info:
            yield f"event: usage\\ndata: {json.dumps(usage_info)}\\n\\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
"""
    )


def flask_example_code():
    """
    Example code for using the generator with Flask.
    This is just example code, not meant to be run.
    """
    print("Example Flask Code:")
    print(
        """
from flask import Flask, request, Response
from indoxRouter import Client
from indoxRouter.models import ChatMessage
import json

app = Flask(__name__)
client = Client(api_key="your_api_key")

@app.route('/stream-chat', methods=['POST'])
def stream_chat():
    request_data = request.json
    messages = [ChatMessage(**msg) for msg in request_data["messages"]]
    
    def generate():
        generator = client.chat(
            messages=messages,
            model=request_data["model"],
            temperature=request_data.get("temperature", 0.7),
            max_tokens=request_data.get("max_tokens", 500),
            stream=True,
            return_generator=True
        )
        
        usage_info = None
        for chunk in generator:
            # Check if this is the final usage info chunk
            if isinstance(chunk, dict) and chunk.get("is_usage_info"):
                # Store usage info to send at the end
                usage_info = chunk
                continue
            
            # Otherwise, it's a text chunk
            yield f"data: {json.dumps({'text': chunk})}\\n\\n"
        
        # After all text chunks, send the usage info as a special event
        if usage_info:
            yield f"event: usage\\ndata: {json.dumps(usage_info)}\\n\\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream'
    )
"""
    )


if __name__ == "__main__":
    simple_streaming_example()
    print("\n" + "-" * 50 + "\n")
    ui_streaming_example()
    print("\n" + "-" * 50 + "\n")
    fastapi_example_code()
    print("\n" + "-" * 50 + "\n")
    flask_example_code()
