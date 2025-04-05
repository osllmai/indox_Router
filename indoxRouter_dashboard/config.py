"""
Configuration settings for the IndoxRouter Dashboard.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Database settings
POSTGRES_URI = os.getenv(
    "POSTGRES_URI", "postgresql://postgres:postgrespassword@localhost:5432/indoxrouter"
)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/indoxrouter")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "indoxrouter")

# API settings
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Pricing tiers
PRICING_TIERS = {
    "free": {
        "name": "Free Tier",
        "price": 0,
        "credits": 5,
        "description": "Get started with basic access to models",
        "features": ["Access to basic models", "5 credits included", "API access"],
    },
    "starter": {
        "name": "Starter",
        "price": 9.99,
        "credits": 10,
        "description": "Perfect for individuals and small projects",
        "features": [
            "Access to all models",
            "10 credits included",
            "Priority support",
            "API access",
        ],
    },
    "pro": {
        "name": "Professional",
        "price": 29.99,
        "credits": 30,
        "description": "For businesses and power users",
        "features": [
            "Access to all models including GPT-4",
            "30 credits included",
            "Priority support",
            "Higher rate limits",
            "Team API keys",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 99.99,
        "credits": 100,
        "description": "For large teams and organizations",
        "features": [
            "Access to all models",
            "100 credits included",
            "Dedicated support",
            "Custom rate limits",
            "Team management",
            "Usage analytics",
        ],
    },
}

# Secret key for session management
SECRET_KEY = os.getenv("SECRET_KEY", "indoxrouter-dashboard-dev-secret-key")
