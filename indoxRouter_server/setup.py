"""
Setup script for indoxRouter server.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="indoxrouter-server",
    version="0.2.0",
    author="indoxRouter Team",
    author_email="ashkan.eskandari.dev@gmail.com",
    description="A unified API server for various AI providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/indoxrouter/indoxrouter-server",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={
        "app": ["providers/json/*.json"],
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
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0,<0.30.0",
        "starlette>=0.27.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "python-multipart>=0.0.6",
        "bcrypt>=4.0.1",
        "httpx>=0.24.0",
        "requests>=2.31.0",
        "aiohttp>=3.8.0",
        "openai>=1.0.0",
        "mistralai>=1.6.0",
        "mistral-common==1.5.4",
        "tiktoken>=0.5.0",
        "python-dotenv>=1.0.0",
        "tenacity>=8.0.0",
        "cryptography>=40.0.0",
        "psycopg2-binary>=2.9.9",
        "pymongo[srv]>=4.6.1",
        "dnspython>=2.4.0",
        "redis>=5.0.0,<=5.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "indoxrouter-server=main:run_server",
        ],
    },
)
