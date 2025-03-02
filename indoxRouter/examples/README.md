# IndoxRouter Examples

This directory contains example scripts for using the IndoxRouter application.

## Dashboard Demo

The `dashboard_demo.py` script demonstrates how to use the IndoxRouter dashboard. The dashboard provides a user-friendly interface for:

- Generating and managing API keys
- Testing completions with different providers and models
- Checking the security of your configuration

To run the dashboard demo:

```bash
python examples/dashboard_demo.py
```

This will start the dashboard on port 7860. You can access it by opening a web browser and navigating to `http://localhost:7860`.

Default login credentials:

- Username: `admin`
- Password: `admin`

## Client API Example

The `client_api_example.py` script demonstrates how to use the IndoxRouter client API to generate completions with different providers and models.

To run the client API example:

```bash
python examples/client_api_example.py
```

## New Providers Example

The `new_providers_example.py` script demonstrates how to use the newly added providers in IndoxRouter:

- Llama
- NVIDIA
- Deepseek
- Databricks

This example shows how to generate completions with each provider and compares their performance, cost, and output quality.

To run the new providers example:

```bash
python examples/new_providers_example.py
```

Make sure to set the appropriate API keys in your environment variables before running this script:

```bash
export LLAMA_API_KEY=your-llama-api-key
export NVIDIA_API_KEY=your-nvidia-api-key
export DEEPSEEK_API_KEY=your-deepseek-api-key
export DATABRICKS_API_KEY=your-databricks-api-key
```

## Provider API Example

The `provider_api_example.py` script demonstrates how to use the IndoxRouter provider API directly to generate completions.

To run the provider API example:

```bash
python examples/provider_api_example.py
```

## Database Example

The `database_example.py` script demonstrates how to use the IndoxRouter database API to create users, generate API keys, and log usage.

To run the database example:

```bash
python examples/database_example.py
```

## Security Example

The `security_example.py` script demonstrates how to use the IndoxRouter security utilities to generate and verify API keys, generate and verify HMAC signatures, and mask API keys.

To run the security example:

```bash
python examples/security_example.py
```

## Cache Example

The `cache_example.py` script demonstrates how to use the IndoxRouter cache utilities to cache responses and improve performance.

To run the cache example:

```bash
python examples/cache_example.py
```
