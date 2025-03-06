"""
Example of using streaming responses with indoxRouter for a website.
This example shows how to use the StreamingGenerator to stream responses
and get usage information at any point, even if the stream is stopped early.
"""

import sys
import os
import time

# Add the parent directory to the path so we can import indoxRouter
module_path = os.path.abspath("..")
if module_path not in sys.path:
    sys.path.append(module_path)

from indoxRouter import Client
from indoxRouter.models import ChatMessage

# Initialize the client
client = Client(api_key="dev-api-key")


def streaming_with_usage_tracking():
    """
    Example of streaming with usage tracking.
    This simulates a website where the user might stop the stream early.
    """
    print("Example: Streaming with Usage Tracking")

    # Define the prompt
    prompt = "Write a long poem about artificial intelligence and creativity."

    print("\nPrompt:", prompt)
    print("\nResponse (streaming):")

    # Make the streaming request with return_generator=True
    generator = client.completion(
        prompt=prompt,
        model="openai/gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        stream=True,
        return_generator=True,
    )

    # Simulate streaming to a website
    # In a real website, you would send each chunk to the client
    response_text = ""
    char_count = 0
    max_chars = 200  # Simulate stopping after 200 characters

    try:
        for chunk in generator:
            response_text += chunk
            char_count += len(chunk)
            print(chunk, end="", flush=True)

            # Simulate the user stopping the stream after a certain number of characters
            if char_count >= max_chars:
                print("\n\n[User stopped the stream]")
                break
    except Exception as e:
        print(f"\n\nError during streaming: {e}")

    # Even if the stream was stopped early, we can still get usage information
    usage_info = generator.get_usage_info()

    print("\n\nUsage Information:")
    print(f"Prompt tokens: {usage_info['usage']['tokens_prompt']}")
    print(f"Completion tokens: {usage_info['usage']['tokens_completion']}")
    print(f"Total tokens: {usage_info['usage']['tokens_total']}")
    print(f"Cost: ${usage_info['cost']:.6f}")
    print(f"Finish reason: {usage_info['finish_reason'] or 'stopped by user'}")
    print(f"Is finished: {usage_info['is_finished']}")


def chat_streaming_with_usage_tracking():
    """
    Example of chat streaming with usage tracking.
    This simulates a website where the user might stop the stream early.
    """
    print("Example: Chat Streaming with Usage Tracking")

    # Define the messages
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Explain quantum computing in detail."),
    ]

    print("\nMessages:", [f"{msg.role}: {msg.content}" for msg in messages])
    print("\nResponse (streaming):")

    # Make the streaming request with return_generator=True
    generator = client.chat(
        messages=messages,
        model="openai/gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        stream=True,
        return_generator=True,
    )

    # Simulate streaming to a website
    # In a real website, you would send each chunk to the client
    response_text = ""
    start_time = time.time()
    max_time = 3  # Simulate stopping after 3 seconds

    try:
        for chunk in generator:
            response_text += chunk
            print(chunk, end="", flush=True)

            # Simulate the user stopping the stream after a certain amount of time
            if time.time() - start_time >= max_time:
                print("\n\n[User stopped the stream]")
                break
    except Exception as e:
        print(f"\n\nError during streaming: {e}")

    # Even if the stream was stopped early, we can still get usage information
    usage_info = generator.get_usage_info()

    print("\n\nUsage Information:")
    print(f"Prompt tokens: {usage_info['usage']['tokens_prompt']}")
    print(f"Completion tokens: {usage_info['usage']['tokens_completion']}")
    print(f"Total tokens: {usage_info['usage']['tokens_total']}")
    print(f"Cost: ${usage_info['cost']:.6f}")
    print(f"Finish reason: {usage_info['finish_reason'] or 'stopped by user'}")
    print(f"Is finished: {usage_info['is_finished']}")


def fastapi_example_code():
    """
    Example code for using the StreamingGenerator with FastAPI.
    This is just example code, not meant to be run.
    """
    print("Example FastAPI Code:")
    print(
        """
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from indoxRouter import Client
from indoxRouter.models import ChatMessage
import json
import asyncio

app = FastAPI()
client = Client(api_key="your_api_key")

# Store active generators for each request ID
active_generators = {}

@app.post("/stream-chat/")
async def stream_chat(request_data: dict):
    messages = [ChatMessage(**msg) for msg in request_data["messages"]]
    request_id = request_data.get("request_id", "default")
    
    # Create the generator
    generator = client.chat(
        messages=messages,
        model=request_data["model"],
        temperature=request_data.get("temperature", 0.7),
        max_tokens=request_data.get("max_tokens", 500),
        stream=True,
        return_generator=True
    )
    
    # Store the generator for this request
    active_generators[request_id] = generator
    
    async def generate():
        try:
            for chunk in generator:
                yield f"data: {json.dumps({'text': chunk})}\\n\\n"
                await asyncio.sleep(0)  # Allow other tasks to run
            
            # Stream is complete, send usage info
            usage_info = generator.get_usage_info()
            yield f"event: usage\\ndata: {json.dumps(usage_info)}\\n\\n"
            
            # Clean up
            if request_id in active_generators:
                del active_generators[request_id]
        except Exception as e:
            # Send error event
            yield f"event: error\\ndata: {json.dumps({'error': str(e)})}\\n\\n"
            
            # Clean up
            if request_id in active_generators:
                del active_generators[request_id]
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@app.post("/stop-stream/")
async def stop_stream(request_data: dict):
    request_id = request_data.get("request_id", "default")
    
    if request_id in active_generators:
        # Get usage info before removing the generator
        generator = active_generators[request_id]
        usage_info = generator.get_usage_info()
        
        # Remove the generator
        del active_generators[request_id]
        
        return {
            "status": "stopped",
            "usage_info": usage_info
        }
    
    return {"status": "not_found"}
"""
    )


def flask_example_code():
    """
    Example code for using the StreamingGenerator with Flask.
    This is just example code, not meant to be run.
    """
    print("Example Flask Code:")
    print(
        """
from flask import Flask, request, Response, jsonify
from indoxRouter import Client
from indoxRouter.models import ChatMessage
import json
import threading

app = Flask(__name__)
client = Client(api_key="your_api_key")

# Store active generators for each request ID
active_generators = {}
active_generators_lock = threading.Lock()

@app.route('/stream-chat', methods=['POST'])
def stream_chat():
    request_data = request.json
    messages = [ChatMessage(**msg) for msg in request_data["messages"]]
    request_id = request_data.get("request_id", "default")
    
    # Create the generator
    generator = client.chat(
        messages=messages,
        model=request_data["model"],
        temperature=request_data.get("temperature", 0.7),
        max_tokens=request_data.get("max_tokens", 500),
        stream=True,
        return_generator=True
    )
    
    # Store the generator for this request
    with active_generators_lock:
        active_generators[request_id] = generator
    
    def generate():
        try:
            for chunk in generator:
                yield f"data: {json.dumps({'text': chunk})}\\n\\n"
            
            # Stream is complete, send usage info
            usage_info = generator.get_usage_info()
            yield f"event: usage\\ndata: {json.dumps(usage_info)}\\n\\n"
            
            # Clean up
            with active_generators_lock:
                if request_id in active_generators:
                    del active_generators[request_id]
        except Exception as e:
            # Send error event
            yield f"event: error\\ndata: {json.dumps({'error': str(e)})}\\n\\n"
            
            # Clean up
            with active_generators_lock:
                if request_id in active_generators:
                    del active_generators[request_id]
    
    return Response(
        generate(),
        mimetype='text/event-stream'
    )

@app.route('/stop-stream', methods=['POST'])
def stop_stream():
    request_data = request.json
    request_id = request_data.get("request_id", "default")
    
    with active_generators_lock:
        if request_id in active_generators:
            # Get usage info before removing the generator
            generator = active_generators[request_id]
            usage_info = generator.get_usage_info()
            
            # Remove the generator
            del active_generators[request_id]
            
            return jsonify({
                "status": "stopped",
                "usage_info": usage_info
            })
    
    return jsonify({"status": "not_found"})
"""
    )


def javascript_client_example():
    """
    Example JavaScript client code for consuming the streaming API.
    This is just example code, not meant to be run.
    """
    print("Example JavaScript Client Code:")
    print(
        """
// Function to start streaming
function startStreaming() {
    const requestId = 'req_' + Math.random().toString(36).substring(2, 15);
    const messages = [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: document.getElementById('prompt').value }
    ];
    
    // Create EventSource for SSE
    const eventSource = new EventSource(`/stream-chat?request_id=${requestId}`);
    
    // Store the EventSource and request ID
    window.currentEventSource = eventSource;
    window.currentRequestId = requestId;
    
    // Clear the response area
    const responseArea = document.getElementById('response');
    responseArea.textContent = '';
    
    // Handle regular messages
    eventSource.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        if (data.text) {
            responseArea.textContent += data.text;
            // Auto-scroll to bottom
            responseArea.scrollTop = responseArea.scrollHeight;
        }
    });
    
    // Handle usage information
    eventSource.addEventListener('usage', (event) => {
        const usageInfo = JSON.parse(event.data);
        displayUsageInfo(usageInfo);
        
        // Close the connection
        eventSource.close();
        window.currentEventSource = null;
        window.currentRequestId = null;
        
        // Enable the start button, disable the stop button
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
    });
    
    // Handle errors
    eventSource.addEventListener('error', (event) => {
        console.error('Error in stream:', event);
        eventSource.close();
        window.currentEventSource = null;
        window.currentRequestId = null;
        
        // Enable the start button, disable the stop button
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
    });
    
    // Disable the start button, enable the stop button
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    
    // Send the actual request
    fetch('/stream-chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            request_id: requestId,
            messages: messages,
            model: 'openai/gpt-4o-mini'
        })
    });
}

// Function to stop streaming
function stopStreaming() {
    if (window.currentEventSource && window.currentRequestId) {
        // Close the EventSource
        window.currentEventSource.close();
        
        // Send request to stop the stream on the server
        fetch('/stop-stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                request_id: window.currentRequestId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'stopped' && data.usage_info) {
                displayUsageInfo(data.usage_info);
            }
            
            // Reset state
            window.currentEventSource = null;
            window.currentRequestId = null;
            
            // Enable the start button, disable the stop button
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        });
    }
}

// Function to display usage information
function displayUsageInfo(usageInfo) {
    const usageDiv = document.getElementById('usage');
    usageDiv.innerHTML = `
        <h3>Usage Information</h3>
        <p>Prompt tokens: ${usageInfo.usage.tokens_prompt}</p>
        <p>Completion tokens: ${usageInfo.usage.tokens_completion}</p>
        <p>Total tokens: ${usageInfo.usage.tokens_total}</p>
        <p>Cost: $${usageInfo.cost.toFixed(6)}</p>
        <p>Finish reason: ${usageInfo.finish_reason || 'stopped by user'}</p>
    `;
}
"""
    )


if __name__ == "__main__":
    streaming_with_usage_tracking()
    print("\n" + "-" * 50 + "\n")
    chat_streaming_with_usage_tracking()
    print("\n" + "-" * 50 + "\n")
    fastapi_example_code()
    print("\n" + "-" * 50 + "\n")
    flask_example_code()
    print("\n" + "-" * 50 + "\n")
    javascript_client_example()
