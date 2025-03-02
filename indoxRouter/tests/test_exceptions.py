import pytest
from indoxRouter.utils.exceptions import (
    IndoxError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    ModelNotFoundError,
    ProviderNotFoundError,
    ProviderAPIError,
    ConfigurationError,
    TokenizerError,
    ValidationError,
)


class TestExceptions:
    """Test suite for the exception classes"""

    def test_indox_error(self):
        """Test the base IndoxError exception"""
        error = IndoxError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_authentication_error(self):
        """Test the AuthenticationError exception"""
        error = AuthenticationError("Invalid API key")
        assert str(error) == "Invalid API key"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_insufficient_credits_error(self):
        """Test the InsufficientCreditsError exception"""
        error = InsufficientCreditsError("Not enough credits")
        assert str(error) == "Not enough credits"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_rate_limit_error(self):
        """Test the RateLimitError exception"""
        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_model_not_found_error(self):
        """Test the ModelNotFoundError exception"""
        error = ModelNotFoundError("Model not found")
        assert str(error) == "Model not found"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_provider_not_found_error(self):
        """Test the ProviderNotFoundError exception"""
        error = ProviderNotFoundError("Provider not found")
        assert str(error) == "Provider not found"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_provider_api_error(self):
        """Test the ProviderAPIError exception"""
        error = ProviderAPIError("API error")
        assert str(error) == "API error"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_configuration_error(self):
        """Test the ConfigurationError exception"""
        error = ConfigurationError("Configuration error")
        assert str(error) == "Configuration error"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_tokenizer_error(self):
        """Test the TokenizerError exception"""
        error = TokenizerError("Tokenizer error")
        assert str(error) == "Tokenizer error"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_validation_error(self):
        """Test the ValidationError exception"""
        error = ValidationError("Validation error")
        assert str(error) == "Validation error"
        assert isinstance(error, IndoxError)
        assert isinstance(error, Exception)

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from IndoxError"""
        exceptions = [
            AuthenticationError,
            InsufficientCreditsError,
            RateLimitError,
            ModelNotFoundError,
            ProviderNotFoundError,
            ProviderAPIError,
            ConfigurationError,
            TokenizerError,
            ValidationError,
        ]

        for exception_class in exceptions:
            assert issubclass(exception_class, IndoxError)

    def test_exception_with_nested_exception(self):
        """Test exceptions with nested exceptions"""
        original_error = ValueError("Original error")
        error = ProviderAPIError("API error", original_error)

        assert str(error) == "API error"
        assert error.__cause__ == original_error
