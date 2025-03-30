"""
IndoxRouter Dashboard

A Streamlit application that simulates the IndoxRouter website dashboard.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json

# Import local modules
import database as db
import auth
from api import IndoxRouterClient

# Page configuration
st.set_page_config(
    page_title="IndoxRouter Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .api-key {
        font-family: monospace;
        padding: 0.5rem;
        background-color: #f1f3f5;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }
    .chat-message {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e9f5ff;
        text-align: right;
    }
    .assistant-message {
        background-color: #f1f3f5;
    }
    .system-message {
        background-color: #fff3cd;
        font-style: italic;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_client" not in st.session_state:
    st.session_state.api_client = None


# Helper functions
def login_user(username, password):
    """Login a user and set session state."""
    user = db.verify_user(username, password)
    if user:
        # Create access token
        access_token = auth.create_access_token(
            {"sub": username, "user_id": user["id"]}
        )

        # Set session state
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.access_token = access_token

        # Get user's API keys
        api_keys = db.get_user_api_keys(user["id"])
        if api_keys:
            # Use the first API key to initialize the client
            st.session_state.api_client = IndoxRouterClient(api_keys[0]["api_key"])

        return True
    return False


def logout_user():
    """Logout a user and reset session state."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.page = "login"
    st.session_state.chat_history = []
    st.session_state.current_chat_id = None
    st.session_state.messages = []
    st.session_state.api_client = None


def register_user(username, email, password, password_confirm):
    """Register a new user."""
    if password != password_confirm:
        return False, "Passwords do not match"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Check if user already exists
    if db.get_user_by_username(username):
        return False, "Username already exists"

    if db.get_user_by_email(email):
        return False, "Email already exists"

    # Create user
    user = db.create_user(username, email, password)
    if user:
        return True, "User created successfully"

    return False, "Failed to create user"


def create_new_api_key(name):
    """Create a new API key for the current user."""
    if not st.session_state.authenticated or not st.session_state.user:
        return None

    key = db.create_api_key(st.session_state.user["id"], name)
    return key


def load_chat_history():
    """Load chat history for the current user."""
    if not st.session_state.authenticated or not st.session_state.user:
        return []

    chats = db.get_user_chat_history(st.session_state.user["id"])
    st.session_state.chat_history = chats
    return chats


def create_new_chat(title, model):
    """Create a new chat for the current user."""
    if not st.session_state.authenticated or not st.session_state.user:
        return None

    chat = db.create_chat(st.session_state.user["id"], title, model)
    if chat:
        st.session_state.current_chat_id = chat["id"]
        st.session_state.messages = []
        load_chat_history()
    return chat


def load_chat_messages(chat_id):
    """Load messages for a specific chat."""
    if not st.session_state.authenticated or not st.session_state.user:
        return []

    messages = db.get_chat_messages(chat_id)
    st.session_state.messages = messages
    st.session_state.current_chat_id = chat_id
    return messages


def add_message_to_chat(role, content):
    """Add a message to the current chat."""
    if (
        not st.session_state.authenticated
        or not st.session_state.user
        or not st.session_state.current_chat_id
    ):
        return None

    message = db.add_chat_message(st.session_state.current_chat_id, role, content)
    if message:
        st.session_state.messages.append(message)
    return message


def send_message_to_api(messages, model=None):
    """Send a message to the IndoxRouter API."""
    if not st.session_state.api_client:
        return {"error": "No API client available"}

    # Format messages for the API
    formatted_messages = [
        {"role": msg["role"], "content": msg["content"]} for msg in messages
    ]

    # Send to API
    response = st.session_state.api_client.chat(formatted_messages, model=model)
    return response


# Navigation
def navigate_to(page):
    """Navigate to a specific page."""
    st.session_state.page = page


# Pages
def render_login_page():
    """Render the login page."""
    st.markdown(
        '<div class="main-header">IndoxRouter Dashboard</div>', unsafe_allow_html=True
    )

    # Create tabs for login and register
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if login_user(username, password):
                    st.success("Login successful!")
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")

            if submit:
                success, message = register_user(
                    new_username, new_email, new_password, confirm_password
                )
                if success:
                    st.success(message)
                    # Auto-login after registration
                    if login_user(new_username, new_password):
                        st.session_state.page = "dashboard"
                        st.rerun()
                else:
                    st.error(message)


def render_dashboard_page():
    """Render the dashboard page."""
    if not st.session_state.authenticated:
        navigate_to("login")
        st.rerun()

    # Sidebar
    with st.sidebar:
        st.markdown(f"**Welcome, {st.session_state.user['username']}!**")
        st.markdown(f"Credits: **{st.session_state.user.get('credits', 10.0):.2f}**")

        st.markdown("---")

        if st.button("Dashboard"):
            navigate_to("dashboard")
            st.rerun()

        if st.button("Chat"):
            navigate_to("chat")
            st.rerun()

        if st.button("API Keys"):
            navigate_to("api_keys")
            st.rerun()

        st.markdown("---")

        if st.button("Logout"):
            logout_user()
            st.rerun()

    # Main content
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)

    # Create a 2x2 grid of cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">API Usage</div>', unsafe_allow_html=True)

        # Create sample data for the chart
        dates = [
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)
        ]
        usage = [int(10 * i / 7) for i in range(7)]

        df = pd.DataFrame({"Date": dates, "Requests": usage})

        fig = px.line(df, x="Date", y="Requests", title="API Requests (Last 7 Days)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Credit Usage</div>', unsafe_allow_html=True
        )

        # Create sample data for the chart
        labels = ["Chat", "Embeddings", "Images"]
        values = [70, 20, 10]

        df = pd.DataFrame({"Category": labels, "Percentage": values})

        fig = px.pie(
            df, values="Percentage", names="Category", title="Credit Usage by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Recent Activity</div>', unsafe_allow_html=True
        )

        # Create sample data for recent activity
        activities = [
            {"type": "Chat", "model": "gpt-4o-mini", "time": "2 hours ago"},
            {
                "type": "Embedding",
                "model": "text-embedding-ada-002",
                "time": "Yesterday",
            },
            {"type": "Image", "model": "dall-e-3", "time": "3 days ago"},
        ]

        for activity in activities:
            st.markdown(
                f"**{activity['type']}** with {activity['model']} - {activity['time']}"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Quick Actions</div>', unsafe_allow_html=True
        )

        if st.button("New Chat"):
            navigate_to("chat")
            st.rerun()

        if st.button("Generate API Key"):
            navigate_to("api_keys")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def render_chat_page():
    """Render the chat page."""
    if not st.session_state.authenticated:
        navigate_to("login")
        st.rerun()

    # Sidebar
    with st.sidebar:
        st.markdown(f"**Welcome, {st.session_state.user['username']}!**")
        st.markdown(f"Credits: **{st.session_state.user.get('credits', 10.0):.2f}**")

        st.markdown("---")

        if st.button("Dashboard", key="dashboard_btn"):
            navigate_to("dashboard")
            st.rerun()

        if st.button("Chat", key="chat_btn"):
            navigate_to("chat")
            st.rerun()

        if st.button("API Keys", key="api_keys_btn"):
            navigate_to("api_keys")
            st.rerun()

        st.markdown("---")

        # Chat history
        st.markdown("**Chat History**")

        # Load chat history
        chats = load_chat_history()

        # New chat button
        if st.button("New Chat"):
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            st.rerun()

        # Display chat history
        for chat in chats:
            if st.button(
                f"{chat['title']} ({chat['model']})", key=f"chat_{chat['id']}"
            ):
                load_chat_messages(chat["id"])
                st.rerun()

        st.markdown("---")

        if st.button("Logout", key="logout_btn"):
            logout_user()
            st.rerun()

    # Main content
    st.markdown('<div class="main-header">Chat</div>', unsafe_allow_html=True)

    # If no current chat, show new chat form
    if not st.session_state.current_chat_id:
        st.markdown(
            '<div class="sub-header">Start a New Chat</div>', unsafe_allow_html=True
        )

        with st.form("new_chat_form"):
            chat_title = st.text_input("Chat Title", value="New Chat")

            # Model selection
            model_options = [
                "gpt-4o-mini",
                "gpt-3.5-turbo",
                "claude-3-haiku",
                "gemini-pro",
            ]
            selected_model = st.selectbox("Model", model_options)

            submit = st.form_submit_button("Start Chat")

            if submit:
                create_new_chat(chat_title, selected_model)
                st.rerun()
    else:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="chat-message user-message">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )
            elif message["role"] == "assistant":
                st.markdown(
                    f'<div class="chat-message assistant-message">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )
            elif message["role"] == "system":
                st.markdown(
                    f'<div class="chat-message system-message">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )

        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area("Message", height=100)
            submit = st.form_submit_button("Send")

            if submit and user_input:
                # Add user message to chat
                add_message_to_chat("user", user_input)

                # Get current chat
                current_chat = next(
                    (
                        c
                        for c in st.session_state.chat_history
                        if c["id"] == st.session_state.current_chat_id
                    ),
                    None,
                )

                if current_chat and st.session_state.api_client:
                    # Get all messages for the API
                    all_messages = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages
                    ]

                    # Send to API
                    with st.spinner("Thinking..."):
                        response = send_message_to_api(
                            all_messages, model=current_chat["model"]
                        )

                    # Process response
                    if "error" in response:
                        st.error(f"API Error: {response['error']}")
                        add_message_to_chat("system", f"Error: {response['error']}")
                    elif "choices" in response and len(response["choices"]) > 0:
                        assistant_message = response["choices"][0]["message"]["content"]
                        add_message_to_chat("assistant", assistant_message)
                    else:
                        st.error("Unexpected API response format")
                        add_message_to_chat(
                            "system", "Error: Unexpected API response format"
                        )

                st.rerun()


def render_api_keys_page():
    """Render the API keys page."""
    if not st.session_state.authenticated:
        navigate_to("login")
        st.rerun()

    # Sidebar
    with st.sidebar:
        st.markdown(f"**Welcome, {st.session_state.user['username']}!**")
        st.markdown(f"Credits: **{st.session_state.user.get('credits', 10.0):.2f}**")

        st.markdown("---")

        if st.button("Dashboard", key="dashboard_btn"):
            navigate_to("dashboard")
            st.rerun()

        if st.button("Chat", key="chat_btn"):
            navigate_to("chat")
            st.rerun()

        if st.button("API Keys", key="api_keys_btn"):
            navigate_to("api_keys")
            st.rerun()

        st.markdown("---")

        if st.button("Logout", key="logout_btn"):
            logout_user()
            st.rerun()

    # Main content
    st.markdown('<div class="main-header">API Keys</div>', unsafe_allow_html=True)

    # Get user's API keys
    api_keys = db.get_user_api_keys(st.session_state.user["id"])

    # Display existing API keys
    if api_keys:
        st.markdown(
            '<div class="sub-header">Your API Keys</div>', unsafe_allow_html=True
        )

        for key in api_keys:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**Name:** {key['name']}")
            st.markdown(
                f"**Created:** {key['created_at'].strftime('%Y-%m-%d %H:%M:%S')}"
            )
            st.markdown(f"**Status:** {'Active' if key['is_active'] else 'Inactive'}")
            st.markdown('<div class="api-key">', unsafe_allow_html=True)
            st.code(key["api_key"], language=None)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Create new API key
    st.markdown(
        '<div class="sub-header">Create New API Key</div>', unsafe_allow_html=True
    )

    with st.form("new_api_key_form"):
        key_name = st.text_input("Key Name", value="My API Key")
        submit = st.form_submit_button("Generate API Key")

        if submit:
            new_key = create_new_api_key(key_name)
            if new_key:
                st.success("API key created successfully!")

                # Initialize API client if not already done
                if not st.session_state.api_client:
                    st.session_state.api_client = IndoxRouterClient(new_key["api_key"])

                st.rerun()
            else:
                st.error("Failed to create API key")


# Main app
def main():
    """Main application entry point."""
    # Render the appropriate page based on session state
    if st.session_state.page == "login":
        render_login_page()
    elif st.session_state.page == "dashboard":
        render_dashboard_page()
    elif st.session_state.page == "chat":
        render_chat_page()
    elif st.session_state.page == "api_keys":
        render_api_keys_page()
    else:
        render_login_page()


if __name__ == "__main__":
    main()
