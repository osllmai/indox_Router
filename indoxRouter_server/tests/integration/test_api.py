"""
Integration tests for the indoxRouter server API.
"""

import os
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Get authentication headers."""
    # In a real test, you would get a token from the auth endpoint
    return {"Authorization": f"Bearer test_token"}


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["message"] == "IndoxRouter Server is running"


def test_get_providers(client, auth_headers):
    """Test the get_providers endpoint."""
    response = client.get("/api/v1/models/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_provider(client, auth_headers):
    """Test the get_provider endpoint."""
    # This test assumes that the OpenAI provider is available
    response = client.get("/api/v1/models/openai", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "openai"
    assert "models" in response.json()


def test_get_model(client, auth_headers):
    """Test the get_model endpoint."""
    # This test assumes that the OpenAI provider and gpt-3.5-turbo model are available
    response = client.get("/api/v1/models/openai/gpt-3.5-turbo", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "gpt-3.5-turbo"
    assert response.json()["provider"] == "openai"


def test_chat_completion(client, auth_headers):
    """Test the chat completion endpoint."""
    # Skip this test if no API key is available
    if not settings.OPENAI_API_KEY:
        pytest.skip("No OpenAI API key available")

    response = client.post(
        "/api/v1/chat/completions",
        headers=auth_headers,
        json={
            "messages": [{"role": "user", "content": "Say hello"}],
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "max_tokens": 10,
        },
    )
    assert response.status_code == 200
    assert "choices" in response.json()
    assert len(response.json()["choices"]) > 0
    assert "message" in response.json()["choices"][0]
    assert "content" in response.json()["choices"][0]["message"]


def test_text_completion(client, auth_headers):
    """Test the text completion endpoint."""
    # Skip this test if no API key is available
    if not settings.OPENAI_API_KEY:
        pytest.skip("No OpenAI API key available")

    response = client.post(
        "/api/v1/completions",
        headers=auth_headers,
        json={
            "prompt": "Say hello",
            "provider": "openai",
            "model": "gpt-3.5-turbo-instruct",
            "max_tokens": 10,
        },
    )
    assert response.status_code == 200
    assert "choices" in response.json()
    assert len(response.json()["choices"]) > 0
    assert "text" in response.json()["choices"][0]


def test_embedding(client, auth_headers):
    """Test the embedding endpoint."""
    # Skip this test if no API key is available
    if not settings.OPENAI_API_KEY:
        pytest.skip("No OpenAI API key available")

    response = client.post(
        "/api/v1/embeddings",
        headers=auth_headers,
        json={
            "text": "Embed this text",
            "provider": "openai",
            "model": "text-embedding-ada-002",
        },
    )
    assert response.status_code == 200
    assert "embeddings" in response.json()
    assert len(response.json()["embeddings"]) > 0
    assert "dimensions" in response.json()


def test_image_generation(client, auth_headers):
    """Test the image generation endpoint."""
    # Skip this test if no API key is available
    if not settings.OPENAI_API_KEY:
        pytest.skip("No OpenAI API key available")

    response = client.post(
        "/api/v1/images/generations",
        headers=auth_headers,
        json={
            "prompt": "A cute cat",
            "provider": "openai",
            "model": "dall-e-3",
            "n": 1,
        },
    )
    assert response.status_code == 200
    assert "images" in response.json()
    assert len(response.json()["images"]) > 0
    assert "url" in response.json()["images"][0]


def test_authentication(client):
    """Test authentication."""
    # Test without authentication
    response = client.get("/api/v1/models/")
    assert response.status_code == 401

    # Test with invalid token
    response = client.get(
        "/api/v1/models/",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401

    # Test login endpoint
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"
    assert "expires_in" in response.json()
