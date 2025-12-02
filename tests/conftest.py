"""
Pytest configuration file for indoxhub tests.

This file contains common fixtures and configuration for the pytest test suite.
"""

import os
import pytest
from indoxhub import Client


# Skip integration tests if the API key is not set
def pytest_configure(config):
    """Configure pytest based on environment variables."""
    # Register markers
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line(
        "markers", "integration: mark a test as an integration test"
    )

    # Skip integration tests if the API key is not set
    if not os.environ.get("INDOX_ROUTER_API_KEY"):
        config.addinivalue_line(
            "markers",
            "skip_if_no_api_key: skip test if INDOX_ROUTER_API_KEY is not set",
        )

        # Apply the marker to all integration tests
        paths = config.getini("testpaths")
        integration_path = next(
            (path for path in paths if path.endswith("integration")), None
        )
        if integration_path:
            config.option.markexpr = "not integration"


@pytest.fixture
def api_key():
    """Return a mock API key for testing."""
    return "test_api_key"


@pytest.fixture
def base_url():
    """Return a base URL for testing."""
    return os.environ.get("INDOX_ROUTER_BASE_URL", "https://api.example.com")


@pytest.fixture
def client(api_key):
    """Return a Client instance with a mock API key."""
    client = Client(api_key=api_key)
    yield client
    client.close()


@pytest.fixture
def live_client():
    """Return a Client instance with a real API key for integration tests."""
    api_key = os.environ.get("INDOX_ROUTER_API_KEY")
    base_url = os.environ.get("INDOX_ROUTER_BASE_URL")

    if not api_key:
        pytest.skip("INDOX_ROUTER_API_KEY environment variable not set")

    # Create client with base_url if provided
    if base_url:
        client = Client(api_key=api_key, base_url=base_url)
    else:
        client = Client(api_key=api_key)

    yield client
    client.close()
