#!/usr/bin/env python
# Example usage of the authentication system

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indoxRouter.utils.auth import AuthManager


def main():
    # Create an instance of the AuthManager
    auth_manager = AuthManager()

    print("=== IndoxRouter Authentication Example ===")

    # Create a new user
    user_id, api_key = auth_manager.create_user(
        email="user@example.com", name="Example User", initial_balance=10.0
    )

    print(f"Created new user:")
    print(f"  User ID: {user_id}")
    print(f"  API Key: {api_key}")
    print(f"  Initial Balance: 10.0 credits")
    print()

    # Authenticate the user
    user_data = auth_manager.authenticate_user(api_key)
    print(f"Authenticated user:")
    print(f"  User ID: {user_data['id']}")
    print(f"  Email: {user_data['email']}")
    print(f"  Name: {user_data['name']}")
    print(f"  Balance: {user_data['balance']} credits")
    print(f"  Active: {user_data['is_active']}")
    print()

    # Add credits
    auth_manager.add_credits(user_id, 5.0)
    user_data = auth_manager.get_user_by_id(user_id)
    print(f"Added 5.0 credits. New balance: {user_data['balance']} credits")

    # Deduct credits
    auth_manager.deduct_credits(user_id, 2.5)
    user_data = auth_manager.get_user_by_id(user_id)
    print(f"Deducted 2.5 credits. New balance: {user_data['balance']} credits")
    print()

    # Generate a second API key for the same user
    second_api_key = auth_manager.generate_api_key(user_id)
    print(f"Generated second API key: {second_api_key}")

    # List all API keys for the user
    api_keys = auth_manager.list_api_keys(user_id)
    print(f"User has {len(api_keys)} API keys:")
    for i, key_data in enumerate(api_keys, 1):
        print(f"  {i}. {key_data['key']} (created: {key_data['created_at']})")
    print()

    # Deactivate the first API key
    auth_manager.deactivate_api_key(api_key)
    print(f"Deactivated first API key: {api_key}")

    # Try to authenticate with the deactivated key
    user_data = auth_manager.authenticate_user(api_key)
    print(
        f"Authentication with deactivated key: {'Successful' if user_data else 'Failed'}"
    )

    # Authenticate with the second key
    user_data = auth_manager.authenticate_user(second_api_key)
    print(f"Authentication with second key: {'Successful' if user_data else 'Failed'}")
    print()

    # Deactivate the user
    auth_manager.deactivate_user(user_id)
    print(f"Deactivated user: {user_id}")

    # Try to authenticate with the second key after user deactivation
    user_data = auth_manager.authenticate_user(second_api_key)
    print(
        f"Authentication after user deactivation: {'Successful' if user_data else 'Failed'}"
    )
    print()

    print("=== Example Complete ===")


if __name__ == "__main__":
    main()
