# IndoxRouter Client Tests

This directory contains tests for the IndoxRouter client.

## Test Structure

The tests are organized into the following directories:

- `unit/` - Unit tests that don't require an API connection
- `integration/` - Integration tests that require a valid API key and server connection

## Running Tests

There are several ways to run the tests:

### 1. Using the `run_tests.py` Script

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests (requires server)
python run_tests.py --integration

# Generate coverage report
python run_tests.py --coverage

# Run tests with verbose output
python run_tests.py --verbose
```

### 2. Using pytest Directly

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests (requires server)
pytest tests/integration/

# Generate coverage report
pytest --cov=indoxRouter --cov-report=term --cov-report=html:coverage_html
```

## Running Tests in GitHub Actions

The project is configured to run **only unit tests** automatically in GitHub Actions on pushes and pull requests to main branches. You can see the workflow configuration in `.github/workflows/python-tests.yml`.

> **Note:** Integration tests are NOT run in GitHub Actions because they require a live server connection. The workflow is designed to only run tests that can function without a server connection.

### GitHub Actions Workflow

Our GitHub Actions workflow:

1. Runs on pushes to master, main, and development branches
2. Tests with Python 3.9, 3.10, and 3.11
3. Only installs client dependencies
4. Only runs unit tests (not integration tests)
5. Generates and uploads coverage reports

### Enabling Integration Tests in GitHub Actions

To enable integration tests in GitHub Actions when your server is available:

1. Add the following secrets in your GitHub repository settings:

   - `ENABLE_INTEGRATION_TESTS` - Set to "true" to enable integration tests
   - `INDOX_ROUTER_API_KEY` - Your API key
   - `INDOX_ROUTER_BASE_URL` - Your server URL (e.g., `http://91.107.253.133:8000`)

2. The workflow will automatically run integration tests when these are set.

## Environment Variables

Integration tests require the following environment variables to be set:

- `INDOX_ROUTER_API_KEY` - Your IndoxRouter API key
- `INDOX_ROUTER_BASE_URL` - Your server URL (optional, defaults to the standard URL)

You can set these in a `.env` file or in your environment.

For tests that involve actual API calls, you need to set:

- `RUN_LIVE_TESTS=1` - Set this to run tests marked with `@pytest.mark.skipif(not os.environ.get("RUN_LIVE_TESTS"), reason="Live tests disabled")`

## When to Run Integration Tests

Integration tests should be run locally when:

1. You have a live server running
2. You have set the `INDOX_ROUTER_API_KEY` environment variable
3. You want to test the actual API interactions

They are not included in the automated GitHub Actions workflow by default to avoid failures when running without a server.

## Connecting to Production Server

To test against the production server (91.107.253.133), create a `.env` file in the project root with:

```
INDOX_ROUTER_API_KEY=your_api_key
INDOX_ROUTER_BASE_URL=http://91.107.253.133:port
```

Replace `port` with the actual port your server is running on (e.g. 8000, 80, etc.)

Make sure the server has proper firewall rules to allow connections from your IP address.
