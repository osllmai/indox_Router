# IndoxRouter Tests

This directory contains tests for the IndoxRouter application.

## Test Structure

The tests are organized by module:

- `test_auth.py`: Tests for the authentication functionality.
- `test_client.py`: Tests for the client.
- `test_api.py`: Tests for the API.
- `test_dashboard.py`: Tests for the dashboard.
- `test_migrations.py`: Tests for the migrations.
- `test_models.py`: Tests for the database models.
- `test_new_providers.py`: Tests for the newly added providers (Llama, NVIDIA, Deepseek, and Databricks).

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest indoxRouter/tests/test_auth.py
```

To run a specific test:

```bash
pytest indoxRouter/tests/test_auth.py::TestAuth::test_create_user
```

To run tests with coverage:

```bash
pytest --cov=indoxRouter
```

## Test Coverage

The tests cover the following areas:

### Authentication

- User creation and authentication
- API key generation and verification
- JWT token generation and verification

### Client

- Client initialization
- API requests
- Error handling

### API

- API endpoints
- Authentication middleware
- Request validation

### Dashboard

- User login and registration
- API key management
- Model testing

### Database

- Database models
- Migrations
- Data validation

### Provider Implementations

- OpenAI provider
- Anthropic provider
- Mistral provider
- Cohere provider
- Google provider
- Meta provider
- AI21 provider
- Llama provider
- NVIDIA provider
- Deepseek provider
- Databricks provider

## Adding New Tests

When adding new tests, please follow these guidelines:

1. Create a new test file if you're testing a new module.
2. Use the `unittest` framework for consistency.
3. Mock external dependencies to avoid making actual API calls.
4. Use descriptive test names that explain what is being tested.
5. Add docstrings to test classes and methods.
6. Maintain test coverage above 80%.

## Test Dependencies

The tests require the following dependencies:

- pytest
- pytest-cov
- pytest-mock
- unittest.mock

These dependencies are included in the `requirements.txt` file.
