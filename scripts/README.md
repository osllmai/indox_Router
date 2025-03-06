# indoxRouter Scripts

This directory contains utility scripts for indoxRouter development and maintenance.

## Available Scripts

### `setup_postgres.py`

Sets up a PostgreSQL database for testing and development.

```bash
# Usage
python scripts/setup_postgres.py [--connection-string CONNECTION_STRING]
```

If no connection string is provided, it will use the `INDOX_ROUTER_DB_URL` environment variable or fall back to the default `postgresql://postgres:postgres@localhost:5432/indoxrouter`.

### `setup_config.py`

Sets up the configuration for indoxRouter, including provider API keys.

```bash
# Usage
python scripts/setup_config.py [--providers PROVIDER1 PROVIDER2 ...] [--config-path CONFIG_PATH]
```

If no providers are specified, it will prompt for API keys for all supported providers. If no config path is provided, it will save the configuration to the default path (`~/.indoxRouter/config.json`).

### `create_provider_json.py`

Creates a new provider JSON file with template data.

```bash
# Usage
python scripts/create_provider_json.py PROVIDER_NAME [--output-path OUTPUT_PATH]
```

If no output path is provided, it will save the file to the `indoxRouter/providers` directory.

## Development

To run these scripts, you may need to install additional dependencies:

```bash
pip install -r requirements-dev.txt
```
