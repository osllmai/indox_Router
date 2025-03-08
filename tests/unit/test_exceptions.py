"""
Unit tests for the exceptions module.
"""

import pytest
from datetime import datetime

from indoxRouter.exceptions import (
    IndoxRouterError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    InvalidParametersError
)


class TestIndoxRouterError:
    """Tests for the IndoxRouterError class."""

    def test_init(self):
        """Test initialization."""
        error = IndoxRouterError("Test error message")
        assert str(error) == "Test error message"


class TestAuthenticationError:
    """Tests for the AuthenticationError class."""

    def test_init(self):
        """Test initialization."""
        error = AuthenticationError("Invalid API key")
        assert str(error) == "Invalid API key"
        assert isinstance(error, IndoxRouterError)


class TestNetworkError:
    """Tests for the NetworkError class."""

    def test_init(self):
        """Test initialization."""
        error = NetworkError("Connection timeout")
        assert str(error) == "Connection timeout"
        assert isinstance(error, IndoxRouterError)


class TestRateLimitError:
    """Tests for the RateLimitError class."""

    def test_init_with_reset_time(self):
        """Test initialization with reset time."""
        reset_time = datetime.now()
        error = RateLimitError("Rate limit exceeded", reset_time=reset_time)
        assert str(error) == "Rate limit exceeded"
        assert error.reset_time == reset_time
        assert isinstance(error, IndoxRouterError)

    def test_init_without_reset_time(self):
        """Test initialization without reset time."""
        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert error.reset_time is None
        assert isinstance(error, IndoxRouterError)


class TestProviderError:
    """Tests for the ProviderError class."""

    def test_init(self):
        """Test initialization."""
        error = ProviderError("Provider error")
        assert str(error) == "Provider error"
        assert isinstance(error, IndoxRouterError)


class TestModelNotFoundError:
    """Tests for the ModelNotFoundError class."""

    def test_init(self):
        """Test initialization."""
        error = ModelNotFoundError("Model not found")
        assert str(error) == "Model not found"
        assert isinstance(error, ProviderError)
        assert isinstance(error, IndoxRouterError)


class TestProviderNotFoundError:
    """Tests for the ProviderNotFoundError class."""

    def test_init(self):
        """Test initialization."""
        error = ProviderNotFoundError("Provider not found")
        assert str(error) == "Provider not found"
        assert isinstance(error, ProviderError)
        assert isinstance(error, IndoxRouterError)


class TestInvalidParametersError:
    """Tests for the InvalidParametersError class."""

    def test_init(self):
        """Test initialization."""
        error = InvalidParametersError("Invalid parameters")
        assert str(error) == "Invalid parameters"
        assert isinstance(error, IndoxRouterError) 