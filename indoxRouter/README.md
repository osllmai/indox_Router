# IndoxRouter

IndoxRouter is a powerful, production-ready LLM routing system that provides a unified interface to multiple AI providers including OpenAI, Anthropic, Google, Meta, Mistral, Cohere, AI21 Labs, Llama, NVIDIA, Deepseek, and Databricks.

## Features

- **Multi-Provider Support**: Seamlessly route requests to different LLM providers
- **Cost Management**: Track and manage usage costs across providers
- **User Authentication**: Built-in user management with API key authentication
- **Credit System**: Prepaid credit system for controlling usage
- **Database Integration**: Production-ready database support with PostgreSQL
- **Caching**: Response caching for improved performance and reduced costs
- **Comprehensive Logging**: Detailed logging of all requests and responses
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Testing Dashboard**: Gradio-based dashboard for testing and managing the application

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher (recommended for production)

### Quick Start

1. Clone the repository:

```bash
git clone https://github.com/yourusername/indoxRouter.git
cd indoxRouter
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Create a .env file
cp .env.example .env

# Edit the .env file with your provider API keys
nano .env
```

4. Initialize the database:

```bash
python -m indoxRouter.utils.migrations init
python -m indoxRouter.utils.migrations create "initial_schema"
python -m indoxRouter.utils.migrations upgrade
```

5. Run the application:

```bash
uvicorn indoxRouter.main:app --reload
```

For detailed deployment instructions, see our [Deployment Guide](docs/deployment_guide.md).

## PostgreSQL Setup

IndoxRouter uses PostgreSQL for production deployments. Follow these steps to set up PostgreSQL:

### Using pgAdmin (Windows)

1. **Create a Database**:

   - Open pgAdmin
   - Right-click on "Databases" in the browser tree
   - Select "Create" > "Database..."
   - Enter "indoxrouter" as the database name
   - Click "Save"

2. **Create a User** (if you don't want to use the default postgres user):

   - Right-click on "Login/Group Roles" in the browser tree
   - Select "Create" > "Login/Group Role..."
   - On the "General" tab, enter "indoxuser" as the name
   - On the "Definition" tab, enter a password
   - On the "Privileges" tab, enable "Can login?" and "Create database"
   - Click "Save"

3. **Grant Privileges**:
   - Right-click on the "indoxrouter" database
   - Select "Properties"
   - Go to the "Security" tab
   - Click "+" to add a new privilege
   - Select "indoxuser" and grant all privileges
   - Click "Save"

### Using Command Line (Linux/macOS)

1. **Install PostgreSQL** (if not already installed):

   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib

   # macOS with Homebrew
   brew install postgresql
   ```

2. **Create Database and User**:

   ```bash
   # Connect to PostgreSQL as the postgres user
   sudo -u postgres psql

   # Create a new user
   CREATE USER indoxuser WITH PASSWORD 'your_password';

   # Create a new database
   CREATE DATABASE indoxrouter;

   # Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE indoxrouter TO indoxuser;

   # Exit PostgreSQL
   \q
   ```

3. **Update Configuration**:

   Edit your `config.json` file to include the PostgreSQL connection details:

   ```json
   "database": {
     "type": "postgres",
     "host": "localhost",
     "port": 5432,
     "user": "indoxuser",
     "password": "your_password",
     "database": "indoxrouter"
   }
   ```

4. **Run Database Migrations**:
   ```bash
   python indoxRouter/run_migration.py
   ```

### Docker Setup

If you're using Docker, the PostgreSQL setup is handled automatically by the Docker Compose configuration. Just make sure to update the environment variables in your `.env` file:

```bash
INDOX_DATABASE_TYPE=postgres
INDOX_DATABASE_HOST=postgres
INDOX_DATABASE_PORT=5432
INDOX_DATABASE_USER=indoxuser
INDOX_DATABASE_PASSWORD=your_password
INDOX_DATABASE_DATABASE=indoxrouter
```

### Docker Deployment

For production deployment, use Docker Compose:

```bash
docker-compose up -d
```

## Configuration

IndoxRouter can be configured using a JSON file or environment variables.

### Configuration File

Create a `config.json` file:

```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "database": {
    "type": "postgres",
    "host": "localhost",
    "port": 5432,
    "user": "indoxuser",
    "password": "your_password",
    "database": "indoxrouter"
  },
  "providers": {
    "default_timeout": 30,
    "retry_attempts": 3
  }
}
```

### Environment Variables

You can also configure IndoxRouter using environment variables:

```bash
# API configuration
export INDOX_API_HOST=0.0.0.0
export INDOX_API_PORT=8000

# Database configuration
export INDOX_DATABASE_TYPE=postgres
export INDOX_DATABASE_HOST=localhost
export INDOX_DATABASE_USER=indoxuser
export INDOX_DATABASE_PASSWORD=your_password
export INDOX_DATABASE_DATABASE=indoxrouter

# Provider API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-...
export MISTRAL_API_KEY=...
export COHERE_API_KEY=...
export GOOGLE_API_KEY=...
export META_API_KEY=...
export AI21_API_KEY=...
export LLAMA_API_KEY=...
export NVIDIA_API_KEY=...
export DEEPSEEK_API_KEY=...
export DATABRICKS_API_KEY=...
```

## Usage

### Creating a User

```python
from indoxRouter.utils.auth import AuthManager

auth_manager = AuthManager()
user = auth_manager.create_user(email="user@example.com", name="Test User", initial_balance=10.0)
api_key = auth_manager.generate_api_key(user_id=user.id)

print(f"User created with ID: {user.id}")
print(f"API Key: {api_key}")
```

### Making a Request

```python
from indoxRouter.client import Client

# Initialize the client with your API key
client = Client(api_key="your_api_key")

# Generate a completion using OpenAI
response = client.generate(
    provider="openai",
    model="gpt-4o",
    prompt="Explain quantum computing in simple terms",
    max_tokens=500
)

print(response["text"])
```

### Routing Between Providers

```python
# Using OpenAI
response_openai = client.generate(
    provider="openai",
    model="gpt-4o",
    prompt="Explain quantum computing in simple terms"
)

# Using Anthropic
response_anthropic = client.generate(
    provider="anthropic",
    model="claude-3-opus-20240229",
    prompt="Explain quantum computing in simple terms"
)

# Using Google
response_google = client.generate(
    provider="google",
    model="gemini-1.5-pro",
    prompt="Explain quantum computing in simple terms"
)

# Using NVIDIA
response_nvidia = client.generate(
    provider="nvidia",
    model="nvidia-tensorrt-llm-mixtral-8x7b-instruct",
    prompt="Explain quantum computing in simple terms"
)
```

## Testing Dashboard

IndoxRouter includes a Gradio-based dashboard for testing and managing the application. The dashboard provides a user-friendly interface for:

- Generating and managing API keys
- Testing completions with different providers and models
- Checking the security of your configuration

To run the dashboard:

```bash
python indoxRouter/run_dashboard.py
```

This will start the dashboard on port 7860. You can access it by opening a web browser and navigating to `http://localhost:7860`.

Default login credentials:

- Username: `admin`
- Password: `admin`

For more information, see [Dashboard Documentation](docs/dashboard.md).

## Supported Providers

IndoxRouter supports the following providers:

- **OpenAI**: GPT-3.5, GPT-4, GPT-4o
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Google**: Gemini 1.0 and 1.5 models
- **Meta**: Llama 2 and Llama 3 models
- **Mistral**: Mistral 7B, 8x7B, Medium, Large
- **Cohere**: Command, Command R, Command R+
- **AI21 Labs**: Jurassic-2, Jamba
- **Llama**: Llama 3 (8B, 70B, 405B) models
- **NVIDIA**: TensorRT-LLM Mixtral, Nemotron, NeMo Sirius
- **Deepseek**: LLM, Coder, Math, Vision models
- **Databricks**: DBRX, Mosaic models

## Testing

Run the test suite:

```bash
pytest
```

For more detailed testing information, see [tests/README.md](tests/README.md).

## Documentation

For more detailed documentation, see:

- [Deployment Guide](docs/deployment_guide.md)
- [API Reference](docs/api.md)
- [Provider Configuration](docs/providers.md)
- [Dashboard Documentation](docs/dashboard.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Thanks to all the LLM providers for their amazing APIs
- Built with FastAPI, SQLAlchemy, and other open-source technologies
