"""
Database models for IndoxRouter.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Float,
)
from sqlalchemy.orm import relationship

from indoxRouter.utils.database import Base, get_session


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    api_keys = relationship(
        "ApiKey", back_populates="user", cascade="all, delete-orphan"
    )
    request_logs = relationship(
        "RequestLog", back_populates="user", cascade="all, delete-orphan"
    )

    @classmethod
    def get_by_id(cls, user_id):
        """Get a user by ID."""
        session = get_session()
        try:
            user = session.query(cls).filter(cls.id == user_id).first()
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_admin": user.is_admin,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                }
            return None
        finally:
            session.close()

    @classmethod
    def get_by_email(cls, email):
        """Get a user by email."""
        session = get_session()
        try:
            user = session.query(cls).filter(cls.email == email).first()
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_admin": user.is_admin,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                }
            return None
        finally:
            session.close()

    @classmethod
    def create(
        cls, email, password_hash, first_name=None, last_name=None, is_admin=False
    ):
        """Create a new user."""
        session = get_session()
        try:
            user = cls(
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                is_admin=is_admin,
                is_active=True,
            )
            session.add(user)
            session.commit()
            return user.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class ApiKey(Base):
    """API key model."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_name = Column(String(100), nullable=False)
    key_prefix = Column(String(20), nullable=False)
    key_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")
    request_logs = relationship(
        "RequestLog", back_populates="api_key", cascade="all, delete-orphan"
    )

    @classmethod
    def get_by_id(cls, key_id):
        """Get an API key by ID."""
        session = get_session()
        try:
            key = session.query(cls).filter(cls.id == key_id).first()
            if key:
                return {
                    "id": key.id,
                    "user_id": key.user_id,
                    "key_name": key.key_name,
                    "key_prefix": key.key_prefix,
                    "key_hash": key.key_hash,
                    "is_active": key.is_active,
                    "expires_at": key.expires_at,
                    "last_used_at": key.last_used_at,
                    "created_at": key.created_at,
                    "updated_at": key.updated_at,
                }
            return None
        finally:
            session.close()

    @classmethod
    def get_by_prefix(cls, prefix):
        """Get an API key by prefix."""
        session = get_session()
        try:
            key = (
                session.query(cls)
                .filter(cls.key_prefix == prefix, cls.is_active == True)
                .first()
            )
            if key:
                return {
                    "id": key.id,
                    "user_id": key.user_id,
                    "key_name": key.key_name,
                    "key_prefix": key.key_prefix,
                    "key_hash": key.key_hash,
                    "is_active": key.is_active,
                    "expires_at": key.expires_at,
                    "last_used_at": key.last_used_at,
                    "created_at": key.created_at,
                    "updated_at": key.updated_at,
                }
            return None
        finally:
            session.close()

    @classmethod
    def create(cls, user_id, key_name, key_prefix, key_hash, expires_at=None):
        """Create a new API key."""
        session = get_session()
        try:
            key = cls(
                user_id=user_id,
                key_name=key_name,
                key_prefix=key_prefix,
                key_hash=key_hash,
                is_active=True,
                expires_at=expires_at,
            )
            session.add(key)
            session.commit()
            return key.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def update_last_used(cls, key_id):
        """Update the last used timestamp for an API key."""
        session = get_session()
        try:
            key = session.query(cls).filter(cls.id == key_id).first()
            if key:
                key.last_used_at = datetime.utcnow()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class RequestLog(Base):
    """Request log model."""

    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    api_key_id = Column(Integer, ForeignKey("api_keys.id"))
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    latency_ms = Column(Float)
    status_code = Column(Integer)
    error_message = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="request_logs")
    api_key = relationship("ApiKey", back_populates="request_logs")

    @classmethod
    def create(
        cls,
        provider,
        model,
        prompt,
        response=None,
        tokens_input=0,
        tokens_output=0,
        latency_ms=0,
        status_code=200,
        error_message=None,
        ip_address=None,
        user_agent=None,
        user_id=None,
        api_key_id=None,
    ):
        """Create a new request log."""
        session = get_session()
        try:
            log = cls(
                user_id=user_id,
                api_key_id=api_key_id,
                provider=provider,
                model=model,
                prompt=prompt,
                response=response,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                latency_ms=latency_ms,
                status_code=status_code,
                error_message=error_message,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            session.add(log)
            session.commit()
            return log.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class ProviderConfig(Base):
    """Provider configuration model."""

    __tablename__ = "provider_configs"

    id = Column(Integer, primary_key=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    config_json = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_by_name(cls, provider_name):
        """Get a provider configuration by name."""
        session = get_session()
        try:
            config = (
                session.query(cls)
                .filter(cls.provider_name == provider_name, cls.is_active == True)
                .first()
            )
            if config:
                return {
                    "id": config.id,
                    "provider_name": config.provider_name,
                    "config_json": config.config_json,
                    "is_active": config.is_active,
                    "created_at": config.created_at,
                    "updated_at": config.updated_at,
                }
            return None
        finally:
            session.close()


class Cache:
    """Cache model for storing temporary data."""

    @staticmethod
    def get(key: str) -> Optional[str]:
        """Get a value from the cache."""
        query = "SELECT value FROM cache WHERE key = %s AND expires_at > NOW()"
        results = execute_query(query, (key,))
        return results[0]["value"] if results else None

    @staticmethod
    def set(key: str, value: str, ttl_seconds: int = 300) -> bool:
        """Set a value in the cache."""
        # Delete existing key if it exists
        execute_query("DELETE FROM cache WHERE key = %s", (key,), fetch=False)

        # Insert new value
        query = """
        INSERT INTO cache (key, value, expires_at)
        VALUES (%s, %s, NOW() + INTERVAL '%s seconds')
        """
        execute_query(query, (key, value, ttl_seconds), fetch=False)
        return True

    @staticmethod
    def delete(key: str) -> bool:
        """Delete a value from the cache."""
        query = "DELETE FROM cache WHERE key = %s"
        execute_query(query, (key,), fetch=False)
        return True

    @staticmethod
    def clear_expired() -> int:
        """Clear expired cache entries and return count of deleted entries."""
        query = "DELETE FROM cache WHERE expires_at <= NOW() RETURNING key"
        results = execute_query(query)
        return len(results) if results else 0
