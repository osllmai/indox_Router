# Building Chatbots with indoxhub

This guide shows how to build a simple but effective chatbot using the indoxhub client. By following these examples, you can create chatbots that leverage different AI models through a consistent interface.

## Basic Chatbot

Here's a simple example of a command-line chatbot:

```python
from indoxhub import Client

def simple_chatbot():
    """A simple command-line chatbot using indoxhub."""

    print("Welcome to indoxhub Chatbot!")
    print("Type 'exit' to end the conversation.\n")

    # Initialize the client
    with Client(api_key="your_api_key") as client:
        # Set up the conversation with a system message
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides concise answers."}
        ]

        while True:
            # Get user input
            user_input = input("You: ")

            # Check if user wants to exit
            if user_input.lower() in ("exit", "quit", "bye"):
                print("Assistant: Goodbye!")
                break

            # Add user message to conversation
            messages.append({"role": "user", "content": user_input})

            try:
                # Get response from the model
                response = client.chat(
                    messages=messages,
                    model="openai/gpt-4o-mini",
                    temperature=0.7
                )

                # Extract and print the assistant's response
                assistant_response = response["data"]
                print(f"Assistant: {assistant_response}")

                # Add assistant response to conversation history
                messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                print(f"Error: {str(e)}")
                messages.pop()

if __name__ == "__main__":
    simple_chatbot()
```

## Multi-Provider Chatbot

One of the key benefits of indoxhub is the ability to use multiple AI providers through a consistent interface. Here's an example of a chatbot that can switch between different providers:

```python
from indoxhub import Client
import argparse

def multi_provider_chatbot():
    """A chatbot that can use different AI providers."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Multi-provider chatbot")
    parser.add_argument("--provider", type=str, default="openai", help="Provider to use (openai, anthropic, google, mistral)")
    parser.add_argument("--model", type=str, help="Specific model to use")
    args = parser.parse_args()

    # Set up provider and model
    provider = args.provider.lower()

    # Default models for each provider
    provider_models = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-haiku-20240307",
        "google": "gemini-1.5-pro",
        "mistral": "mistral-small-latest",
        "deepseek": "deepseek-chat"
    }

    if args.model:
        model = args.model
    elif provider in provider_models:
        model = provider_models[provider]
    else:
        print(f"Unknown provider: {provider}. Using OpenAI as default.")
        provider = "openai"
        model = provider_models[provider]

    full_model = f"{provider}/{model}"
    print(f"Welcome to indoxhub Multi-Provider Chatbot!")
    print(f"Using model: {full_model}")
    print("Type 'exit' to end the conversation.")
    print("Type 'switch provider model' to change the AI model.\n")

    # Initialize the client
    with Client(api_key="your_api_key") as client:
        # Set up the conversation with a system message
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides concise answers."}
        ]

        while True:
            # Get user input
            user_input = input("You: ")

            # Check if user wants to exit
            if user_input.lower() in ("exit", "quit", "bye"):
                print("Assistant: Goodbye!")
                break

            # Check if user wants to switch model
            if user_input.lower().startswith("switch "):
                try:
                    _, new_provider, new_model = user_input.split()
                    full_model = f"{new_provider}/{new_model}"
                    print(f"Switching to {full_model}")

                    # Add system message explaining the switch
                    messages.append({"role": "system", "content": f"The conversation will now continue using {full_model}."})
                    continue
                except ValueError:
                    print("Invalid format. Use 'switch provider model'")
                    continue

            # Add user message to conversation
            messages.append({"role": "user", "content": user_input})

            try:
                # Get response from the model
                response = client.chat(
                    messages=messages,
                    model=full_model,
                    temperature=0.7
                )

                # Extract and print the assistant's response
                assistant_response = response["data"]
                print(f"Assistant: {assistant_response}")

                # Add assistant response to conversation history
                messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                print(f"Error: {str(e)}")
                messages.pop()  # Remove the user message from history

if __name__ == "__main__":
    multi_provider_chatbot()
```

## Web-Based Chatbot with Streamlit

You can also create a simple web-based chatbot using Streamlit:

```python
# Save as chatbot_app.py
import streamlit as st
from indoxhub import Client, ModelNotFoundError, ProviderError

# Set page title and configure
st.set_page_config(page_title="indoxhub Chatbot", page_icon="💬")
st.title("indoxhub Chatbot")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

if "current_model" not in st.session_state:
    st.session_state.current_model = "openai/gpt-4o-mini"

# API key input
api_key = st.sidebar.text_input("API Key", type="password")

# Model selection
provider_options = ["openai", "anthropic", "google", "mistral", "deepseek"]
selected_provider = st.sidebar.selectbox("Provider", provider_options)

model_options = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"],
    "google": ["gemini-1.5-pro", "gemini-1.5-flash"],
    "mistral": ["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"],
    "deepseek": ["deepseek-chat", "deepseek-coder"]
}

selected_model = st.sidebar.selectbox("Model", model_options[selected_provider])
st.session_state.current_model = f"{selected_provider}/{selected_model}"

# Temperature slider
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

# Display conversation history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

if user_input and api_key:
    # Add user message to conversation
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Get assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Initialize client
            with Client(api_key=api_key) as client:
                # Stream the response
                for chunk in client.chat(
                    messages=st.session_state.messages,
                    model=st.session_state.current_model,
                    temperature=temperature,
                    stream=True
                ):
                    if isinstance(chunk, dict) and "data" in chunk:
                        content = chunk["data"]
                        full_response += content
                        message_placeholder.write(full_response + "▌")

                message_placeholder.write(full_response)

            # Add assistant response to conversation
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except ModelNotFoundError as e:
            st.error(f"Model not found: {e}")
        except ProviderError as e:
            st.error(f"Provider error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

elif user_input and not api_key:
    st.warning("Please enter your API key in the sidebar.")

# Run with: streamlit run chatbot_app.py
```

To run the Streamlit app, install Streamlit and run:

```bash
pip install streamlit
streamlit run chatbot_app.py
```

## Best Practices for Chatbots

1. **Maintain Conversation Context**: Keep track of conversation history to provide contextual responses
2. **Set Clear System Instructions**: Use system messages to define the persona and behavior of your chatbot
3. **Handle Errors Gracefully**: Implement proper error handling to ensure a smooth user experience
4. **Optimize Token Usage**: Be mindful of the conversation length to avoid exceeding token limits
5. **Implement Rate Limiting**: Add rate limiting to prevent abuse and manage costs
6. **Consider Privacy**: Be transparent about data usage and implement appropriate data retention policies
7. **Test Different Models**: Experiment with different models to find the best balance of quality and cost
8. **Implement Fallbacks**: Have fallback mechanisms when a provider is unavailable or returns errors

## Next Steps

To further enhance your chatbot, consider:

- Implementing memory management for long conversations
- Adding message persistence using a database
- Implementing functions/tools for more interactive capabilities
- Creating a feedback mechanism to improve chatbot responses
- Fine-tuning models for specific use cases

_Last updated: Nov 08, 2025_