# Contributing to IndoxRouter

Thank you for your interest in contributing to IndoxRouter! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- MongoDB 6.0 or higher
- Git

### Local Development Environment

1. Clone the repository:

```bash
git clone https://github.com/yourusername/indoxrouter.git
cd indoxrouter
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Set up the environment variables:

```bash
cp development.env .env
```

5. Start the databases:

```bash
./run_local_db.sh
```

This script starts PostgreSQL and MongoDB using Docker for local development.

6. Run database migrations:

```bash
python -m scripts.init_db
```

7. Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

## Project Structure

```
indoxrouter_server/
├── app/                 # Main application package
│   ├── api/             # API endpoints
│   │   ├── dependencies/# FastAPI dependencies
│   │   └── routers/     # API routers
│   ├── core/            # Core functionality
│   ├── db/              # Database models and functions
│   ├── middleware/      # Middleware components
│   ├── models/          # Pydantic models
│   ├── providers/       # Provider implementations
│   └── utils/           # Utility functions
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── tests/               # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── .env                 # Environment variables
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies
```

## Coding Style

We follow PEP 8 and use the following tools for code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For linting
- **mypy**: For type checking

You can run all code quality checks with:

```bash
# Format code
black .
isort .

# Check code quality
flake8
mypy .
```

## Testing

We use pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific tests
pytest tests/unit/
pytest tests/integration/
```

## Adding a New Provider

To add a new provider:

1. Create a new file in `app/providers/` (e.g., `app/providers/new_provider.py`)
2. Implement the provider class by inheriting from `BaseProvider`
3. Create a JSON model definition file in `app/providers/json/` (e.g., `app/providers/json/new_provider.json`)
4. Add the provider to the factory mapping in `app/providers/factory.py`
5. Add the provider to `AVAILABLE_PROVIDERS` in `app/constants.py`
6. Add tests for the provider in `tests/unit/providers/`

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting to ensure code quality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation only changes
- `style:` - Changes that do not affect the meaning of the code
- `refactor:` - Code change that neither fixes a bug nor adds a feature
- `perf:` - Code change that improves performance
- `test:` - Adding missing tests or correcting existing tests
- `chore:` - Changes to the build process or auxiliary tools

Example:

```
feat(provider): add support for new provider

This adds support for the new provider, including:
- Provider implementation
- Model definitions
- Integration tests
```

## Documentation

When adding or changing features, please update the relevant documentation:

1. API changes should be documented in [api-reference.md](api-reference.md)
2. Database changes should be documented in [database-schema.md](database-schema.md)
3. New providers should be documented in [provider-integration.md](provider-integration.md)

## License

By contributing to IndoxRouter, you agree that your contributions will be licensed under the project's license.
