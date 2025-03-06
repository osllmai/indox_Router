"""
Setup script for indoxRouter.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="indoxRouter",
    version="0.1.0",
    author="indoxRouter Team",
    author_email="info@indoxrouter.com",
    description="A unified interface for various LLM providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/indoxrouter/indoxrouter",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "indoxRouter": ["providers/*.json"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "cohere-api>=1.0.0",
        "google-generativeai>=0.1.0",
        "mistralai>=0.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.5",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "psycopg2-binary>=2.9.5",
        ],
    },
)
