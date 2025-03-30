# IndoxRouter Dashboard

A Streamlit-based dashboard that simulates the IndoxRouter website functionality for local testing and development.

## Features

- User authentication (signup/login)
- API key management
- Chat interface with model selection
- Dashboard with usage statistics
- Integration with the IndoxRouter server

## Prerequisites

- Python 3.8+
- PostgreSQL database
- IndoxRouter server running locally

## Setup

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Set up the PostgreSQL database**

Make sure you have created the necessary tables as described in the `LOCAL_TESTING_INSTRUCTIONS.md` file in the parent directory. The dashboard will automatically create additional tables for user credentials and chat history.

3. **Configure environment variables**

Edit the `.env` file to match your local setup:

```
# Database settings
DATABASE_URL=postgresql://postgres:12345@localhost:5432/indoxrouter_test

# Secret key for JWT tokens
SECRET_KEY=indoxrouter-dashboard-secret-2024
ACCESS_TOKEN_EXPIRE_MINUTES=30

# IndoxRouter server settings
INDOXROUTER_API_URL=http://localhost:8000/api/v1
```

## Running the Dashboard

```bash
cd dashboard
streamlit run app.py
```

The dashboard will be available at http://localhost:8501

## Usage

1. **Register a new user**

   - Go to the Register tab on the login page
   - Fill in your details and create an account

2. **Generate an API key**

   - After logging in, navigate to the API Keys page
   - Create a new API key with a descriptive name

3. **Chat with AI models**
   - Go to the Chat page
   - Start a new chat and select a model
   - Send messages and receive responses

## Database Schema

The dashboard uses the following tables:

- `users` - User information
- `user_credentials` - Password hashes for users
- `api_keys` - API keys for users
- `chat_history` - Chat sessions
- `chat_messages` - Individual messages in chats

## Integration with IndoxRouter Server

The dashboard communicates with the IndoxRouter server using the API client. Make sure the server is running locally before using the chat functionality.

## Development

To modify the dashboard:

1. Edit the `app.py` file to change the UI and functionality
2. Edit the `database.py` file to modify database operations
3. Edit the `api.py` file to change how the dashboard communicates with the IndoxRouter server
