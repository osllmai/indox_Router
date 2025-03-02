"""
Authentication utility module for IndoxRouter.
Provides functions for user authentication and API key management.
"""

import os
import json
import hashlib
import secrets
import logging
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List

from ..models.database import User, ApiKey

# Configure logging
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file at {config_path}")
        raise


def hash_password(password: str) -> str:
    """
    Hash a password with a random salt.

    Args:
        password: The password to hash

    Returns:
        A string in the format "salt$hash"
    """
    salt = secrets.token_hex(8)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${password_hash}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify a password against a stored hash.

    Args:
        stored_password: The stored password hash in the format "salt$hash"
        provided_password: The password to verify

    Returns:
        True if the password matches, False otherwise
    """
    try:
        salt, stored_hash = stored_password.split("$", 1)
        calculated_hash = hashlib.sha256(
            (salt + provided_password).encode()
        ).hexdigest()
        return secrets.compare_digest(stored_hash, calculated_hash)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with email and password.

    Args:
        email: User email
        password: User password

    Returns:
        User data if authentication is successful, None otherwise
    """
    user = User.get_by_email(email)
    if not user:
        logger.warning(f"Authentication failed: User not found: {email}")
        return None

    if not user["is_active"]:
        logger.warning(f"Authentication failed: User is inactive: {email}")
        return None

    if not verify_password(user["password_hash"], password):
        logger.warning(f"Authentication failed: Invalid password for user: {email}")
        return None

    return user


def generate_jwt_token(
    user_id: int, is_admin: bool = False
) -> Tuple[str, str, int, int]:
    """
    Generate a JWT token and refresh token for a user.

    Args:
        user_id: User ID
        is_admin: Whether the user is an admin

    Returns:
        Tuple of (access_token, refresh_token, access_token_expiry, refresh_token_expiry)
    """
    config = load_config()
    auth_config = config["auth"]

    # Get token expiry times
    access_token_expiry = auth_config.get("token_expiry", 86400)  # 24 hours default
    refresh_token_expiry = auth_config.get(
        "refresh_token_expiry", 2592000
    )  # 30 days default

    # Calculate expiry timestamps
    access_token_exp = datetime.utcnow() + timedelta(seconds=access_token_expiry)
    refresh_token_exp = datetime.utcnow() + timedelta(seconds=refresh_token_expiry)

    # Create access token payload
    access_payload = {
        "sub": str(user_id),
        "admin": is_admin,
        "exp": access_token_exp,
        "iat": datetime.utcnow(),
        "type": "access",
    }

    # Create refresh token payload
    refresh_payload = {
        "sub": str(user_id),
        "exp": refresh_token_exp,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }

    # Get JWT secret
    jwt_secret = auth_config.get("jwt_secret", "your_jwt_secret_key_here")

    # Generate tokens
    access_token = jwt.encode(access_payload, jwt_secret, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, jwt_secret, algorithm="HS256")

    return access_token, refresh_token, access_token_expiry, refresh_token_expiry


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token.

    Args:
        token: JWT token

    Returns:
        Token payload if valid, None otherwise
    """
    config = load_config()
    jwt_secret = config["auth"].get("jwt_secret", "your_jwt_secret_key_here")

    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def refresh_access_token(refresh_token: str) -> Optional[Tuple[str, int]]:
    """
    Refresh an access token using a refresh token.

    Args:
        refresh_token: Refresh token

    Returns:
        Tuple of (new_access_token, expiry) if successful, None otherwise
    """
    payload = verify_jwt_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None

    user_id = int(payload["sub"])
    user = User.get_by_id(user_id)
    if not user or not user["is_active"]:
        return None

    # Generate new access token
    config = load_config()
    auth_config = config["auth"]
    jwt_secret = auth_config.get("jwt_secret", "your_jwt_secret_key_here")
    access_token_expiry = auth_config.get("token_expiry", 86400)

    access_token_exp = datetime.utcnow() + timedelta(seconds=access_token_expiry)
    access_payload = {
        "sub": str(user_id),
        "admin": user["is_admin"],
        "exp": access_token_exp,
        "iat": datetime.utcnow(),
        "type": "access",
    }

    access_token = jwt.encode(access_payload, jwt_secret, algorithm="HS256")
    return access_token, access_token_expiry


def generate_api_key(
    user_id: int, key_name: str, expires_days: Optional[int] = None
) -> Tuple[str, int]:
    """
    Generate a new API key for a user.

    Args:
        user_id: User ID
        key_name: Name for the API key
        expires_days: Number of days until the key expires (None for no expiry)

    Returns:
        Tuple of (api_key, key_id)
    """
    config = load_config()
    key_prefix = config["auth"].get("api_key_prefix", "indox_")

    # Generate a random key
    key_suffix = secrets.token_hex(16)
    api_key = f"{key_prefix}{key_suffix}"

    # Hash the key for storage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Calculate expiry date if provided
    expires_at = None
    if expires_days is not None:
        expires_at = datetime.now() + timedelta(days=expires_days)

    # Store the key in the database
    key_id = ApiKey.create(
        user_id=user_id,
        key_name=key_name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        expires_at=expires_at,
    )

    if not key_id:
        raise Exception("Failed to create API key")

    return api_key, key_id


def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Verify an API key and return the associated user.

    Args:
        api_key: API key to verify

    Returns:
        Dictionary with user and key information if valid, None otherwise
    """
    try:
        # Extract prefix
        config = load_config()
        expected_prefix = config["auth"].get("api_key_prefix", "indox_")

        if not api_key.startswith(expected_prefix):
            logger.warning(f"API key verification failed: Invalid prefix")
            return None

        # Hash the key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Look up the key in the database
        key_record = ApiKey.get_by_prefix(expected_prefix)
        if not key_record:
            logger.warning(f"API key verification failed: Key not found")
            return None

        # Check if the key is active
        if not key_record["is_active"]:
            logger.warning(f"API key verification failed: Key is inactive")
            return None

        # Check if the key has expired
        if key_record["expires_at"] and key_record["expires_at"] < datetime.now():
            logger.warning(f"API key verification failed: Key has expired")
            return None

        # Verify the hash
        if not secrets.compare_digest(key_record["key_hash"], key_hash):
            logger.warning(f"API key verification failed: Invalid key hash")
            return None

        # Update last used timestamp
        ApiKey.update_last_used(key_record["id"])

        # Get the associated user
        user = User.get_by_id(key_record["user_id"])
        if not user or not user["is_active"]:
            logger.warning(f"API key verification failed: User not found or inactive")
            return None

        return {"user": user, "key": key_record}
    except Exception as e:
        logger.error(f"Error verifying API key: {e}")
        return None


class AuthManager:
    """
    Authentication manager for IndoxRouter.
    Provides methods for user authentication and API key management.
    """

    def __init__(self):
        """Initialize the authentication manager."""
        self.config = load_config()

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password.

        Args:
            email: User email
            password: User password

        Returns:
            User data if authentication is successful, None otherwise
        """
        return authenticate_user(email, password)

    def generate_jwt_token(
        self, user_id: int, is_admin: bool = False
    ) -> Tuple[str, str, int, int]:
        """
        Generate a JWT token and refresh token for a user.

        Args:
            user_id: User ID
            is_admin: Whether the user is an admin

        Returns:
            Tuple of (access_token, refresh_token, access_token_expiry, refresh_token_expiry)
        """
        return generate_jwt_token(user_id, is_admin)

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token.

        Args:
            token: JWT token

        Returns:
            Token payload if valid, None otherwise
        """
        return verify_jwt_token(token)

    def refresh_access_token(self, refresh_token: str) -> Optional[Tuple[str, int]]:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            Tuple of (new_access_token, expiry) if successful, None otherwise
        """
        return refresh_access_token(refresh_token)

    def generate_api_key(
        self, user_id: int, key_name: str, expires_days: Optional[int] = None
    ) -> Tuple[str, int]:
        """
        Generate a new API key for a user.

        Args:
            user_id: User ID
            key_name: Name for the API key
            expires_days: Number of days until the key expires (None for no expiry)

        Returns:
            Tuple of (api_key, key_id)
        """
        return generate_api_key(user_id, key_name, expires_days)

    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify an API key and return the associated user.

        Args:
            api_key: API key to verify

        Returns:
            Dictionary with user and key information if valid, None otherwise
        """
        return verify_api_key(api_key)

    def hash_password(self, password: str) -> str:
        """
        Hash a password with a random salt.

        Args:
            password: The password to hash

        Returns:
            A string in the format "salt$hash"
        """
        return hash_password(password)

    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        """
        Verify a password against a stored hash.

        Args:
            stored_password: The stored password hash in the format "salt$hash"
            provided_password: The password to verify

        Returns:
            True if the password matches, False otherwise
        """
        return verify_password(stored_password, provided_password)

    def create_user(
        self,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        is_admin: bool = False,
    ) -> Optional[int]:
        """
        Create a new user.

        Args:
            email: User email
            password: Password (will be hashed)
            first_name: First name
            last_name: Last name
            is_admin: Whether the user is an admin

        Returns:
            User ID if successful, None otherwise
        """
        from .database import DatabaseManager

        # Hash the password
        password_hash = self.hash_password(password)

        # Create the user
        db = DatabaseManager()
        return db.create_user(email, password_hash, first_name, last_name, is_admin)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.

        Args:
            user_id: User ID

        Returns:
            User data if found, None otherwise
        """
        from .database import DatabaseManager

        db = DatabaseManager()
        return db.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email.

        Args:
            email: User email

        Returns:
            User data if found, None otherwise
        """
        from .database import DatabaseManager

        db = DatabaseManager()
        return db.get_user_by_email(email)

    def get_api_keys(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get API keys for a user.

        Args:
            user_id: User ID

        Returns:
            List of API keys
        """
        from .database import DatabaseManager

        db = DatabaseManager()
        return db.get_api_keys(user_id)

    def deactivate_api_key(self, key_id: int) -> bool:
        """
        Deactivate an API key.

        Args:
            key_id: API key ID

        Returns:
            True if successful, False otherwise
        """
        from .database import DatabaseManager

        db = DatabaseManager()
        return db.update_api_key(key_id, {"is_active": False})

    def delete_api_key(self, key_id: int) -> bool:
        """
        Delete an API key.

        Args:
            key_id: API key ID

        Returns:
            True if successful, False otherwise
        """
        from .database import DatabaseManager

        db = DatabaseManager()
        return db.delete_api_key(key_id)
