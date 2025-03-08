# indoxRouter Tests

This directory contains tests for the indoxRouter package.

## Test Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests that test multiple components together
- `conftest.py`: Common fixtures and configuration for tests

## Running Tests

### Running All Tests

```bash
pytest
```

### Running Unit Tests Only

```bash
pytest tests/unit
```

### Running Integration Tests

Integration tests are disabled by default because they require valid API keys and make actual API calls. To enable them:

```bash
RUN_INTEGRATION_TESTS=1 pytest tests/integration
```

### Running Expensive Tests

Some tests make API calls that may incur costs. These are disabled by default. To enable them:

```bash
RUN_EXPENSIVE_TESTS=1 pytest tests/integration/test_client_integration.py::TestClientAPIIntegration
```

## Test Configuration

The test configuration is in `pytest.ini` in the root directory. It defines:

- Test paths and patterns
- Markers for categorizing tests
- Verbosity settings
- Warning filters

## Writing Tests

### Unit Tests

Unit tests should test a single component in isolation. They should mock external dependencies.

Example:

```python
def test_something():
    # Arrange
    expected = "expected result"

    # Act
    result = function_under_test()

    # Assert
    assert result == expected
```

### Integration Tests

Integration tests should test multiple components together. They may make actual API calls.

Example:

```python
@pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS") != "1",
    reason="Integration tests are disabled. Set RUN_INTEGRATION_TESTS=1 to enable."
)
def test_integration():
    # Test that multiple components work together
    client = Client(api_key="test-key")
    result = client.some_method()
    assert result is not None
```
