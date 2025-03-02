import pytest
from indoxRouter.utils.auth import AuthManager
from indoxRouter.utils.exceptions import AuthenticationError


class TestAuthManager:
    """Test suite for the AuthManager class"""

    def test_create_user(self, auth_manager):
        """Test creating a new user"""
        user_id, api_key = auth_manager.create_user(
            email="new_user@example.com", name="New User", initial_balance=50.0
        )

        # Check that user_id and api_key are returned
        assert user_id is not None
        assert api_key is not None
        assert api_key.startswith("indox_")

        # Check that user was created with correct data
        user = auth_manager.get_user_by_id(user_id)
        assert user is not None
        assert user["email"] == "new_user@example.com"
        assert user["name"] == "New User"
        assert user["balance"] == 50.0
        assert user["is_active"] is True

    def test_authenticate_user_valid(self, auth_manager, test_user):
        """Test authenticating a user with a valid API key"""
        user = auth_manager.authenticate_user(test_user["api_key"])
        assert user is not None
        assert user["id"] == test_user["id"]
        assert user["email"] == test_user["email"]

    def test_authenticate_user_invalid(self, auth_manager):
        """Test authenticating a user with an invalid API key"""
        user = auth_manager.authenticate_user("invalid_api_key")
        assert user is None

    def test_deactivate_api_key(self, auth_manager, test_user):
        """Test deactivating an API key"""
        # Deactivate the API key
        result = auth_manager.deactivate_api_key(test_user["api_key"])
        assert result is True

        # Try to authenticate with the deactivated key
        user = auth_manager.authenticate_user(test_user["api_key"])
        assert user is None

    def test_deactivate_user(self, auth_manager, test_user):
        """Test deactivating a user"""
        # Deactivate the user
        result = auth_manager.deactivate_user(test_user["id"])
        assert result is True

        # Check that user is inactive
        user = auth_manager.get_user_by_id(test_user["id"])
        assert user["is_active"] is False

        # Try to authenticate with the API key
        user = auth_manager.authenticate_user(test_user["api_key"])
        assert user is None

    def test_add_credits(self, auth_manager, test_user):
        """Test adding credits to a user's balance"""
        # Add credits
        result = auth_manager.add_credits(test_user["id"], 50.0)
        assert result is True

        # Check that balance was updated
        user = auth_manager.get_user_by_id(test_user["id"])
        assert user["balance"] == 150.0  # 100 initial + 50 added

    def test_deduct_credits_sufficient(self, auth_manager, test_user):
        """Test deducting credits when user has sufficient balance"""
        # Deduct credits
        result = auth_manager.deduct_credits(test_user["id"], 50.0)
        assert result is True

        # Check that balance was updated
        user = auth_manager.get_user_by_id(test_user["id"])
        assert user["balance"] == 50.0  # 100 initial - 50 deducted

    def test_deduct_credits_insufficient(self, auth_manager, test_user):
        """Test deducting credits when user has insufficient balance"""
        # Try to deduct more credits than available
        result = auth_manager.deduct_credits(test_user["id"], 150.0)
        assert result is False

        # Check that balance was not changed
        user = auth_manager.get_user_by_id(test_user["id"])
        assert user["balance"] == 100.0  # Unchanged

    def test_get_user_by_id(self, auth_manager, test_user):
        """Test getting a user by ID"""
        user = auth_manager.get_user_by_id(test_user["id"])
        assert user is not None
        assert user["id"] == test_user["id"]
        assert user["email"] == test_user["email"]

    def test_get_user_by_api_key(self, auth_manager, test_user):
        """Test getting a user by API key"""
        user = auth_manager.get_user_by_api_key(test_user["api_key"])
        assert user is not None
        assert user["id"] == test_user["id"]
        assert user["email"] == test_user["email"]

    def test_list_users(self, auth_manager, test_user):
        """Test listing all users"""
        # Create another user
        auth_manager.create_user(
            email="another@example.com", name="Another User", initial_balance=25.0
        )

        # List all users
        users = auth_manager.list_users()
        assert len(users) >= 2  # At least 2 users (test_user and the new one)

        # Check that test_user is in the list
        user_ids = [user["id"] for user in users]
        assert test_user["id"] in user_ids

    def test_list_api_keys(self, auth_manager, test_user):
        """Test listing API keys for a user"""
        # Generate another API key for the user
        auth_manager.generate_api_key(test_user["id"])

        # List API keys for the user
        api_keys = auth_manager.list_api_keys(test_user["id"])
        assert len(api_keys) >= 2  # At least 2 keys (original and new one)

        # Check that the original API key is in the list
        api_key_values = [api_key["key"] for api_key in api_keys]
        assert test_user["api_key"] in api_key_values

    def test_generate_api_key(self, auth_manager, test_user):
        """Test generating a new API key for a user"""
        # Generate a new API key
        new_api_key = auth_manager.generate_api_key(test_user["id"])
        assert new_api_key is not None
        assert new_api_key.startswith("indox_")

        # Check that the new API key is valid
        user = auth_manager.authenticate_user(new_api_key)
        assert user is not None
        assert user["id"] == test_user["id"]
