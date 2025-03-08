# Installation

This guide covers how to install indoxRouter and set up your environment.

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Basic Installation

You can install indoxRouter using pip:

```bash
pip install indoxRouter
```

This will install the core package with all required dependencies, including:

- requests
- openai
- anthropic
- cohere-api
- google-generativeai
- mistralai

## Development Installation

If you're planning to contribute to indoxRouter or need the development tools, you can install the development version:

```bash
pip install indoxRouter[dev]
```

This includes additional packages for development:

- pytest and pytest-cov for testing
- black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

## Optional Features

### PostgreSQL Support

If you want to use PostgreSQL for data storage (for advanced usage scenarios):

```bash
pip install indoxRouter[postgres]
```

This will install the `psycopg2-binary` package for PostgreSQL database connectivity.

### All Features

To install all optional dependencies:

```bash
pip install indoxRouter[all]
```

## Verifying Installation

You can verify that indoxRouter is installed correctly by running:

```python
import indoxRouter
print(indoxRouter.__version__)
```

## Next Steps

After installation, you'll need to:

1. [Configure your API key](configuration.md)
2. [Try the quick start guide](quickstart.md)

## Troubleshooting

If you encounter any issues during installation:

- Make sure you have the latest version of pip: `pip install --upgrade pip`
- If you're using a virtual environment, ensure it's activated
- Check that you have the required Python version: `python --version`
- For Windows users, you might need to install the Microsoft C++ Build Tools if you encounter compilation errors

If problems persist, please [open an issue](https://github.com/indoxrouter/indoxrouter/issues) on our GitHub repository.
