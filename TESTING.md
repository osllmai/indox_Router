# Testing the IndoxRouter Application

This document provides instructions for running the tests for both the client and server components of the IndoxRouter application.

## Test Structure

The test suite is organized as follows:

```
indoxRouter_server/
├── tests/
│   ├── unit/
│   │   └── test_database.py
│   └── integration/
│       └── test_db_integration.py
└── run_tests.py

indoxRouter_client/
├── tests/
│   ├── unit/
│   │   └── test_client.py
│   └── integration/
│       └── test_client_integration.py
└── run_tests.py
```

## Prerequisites

Before running the tests, make sure you have:

1. A running PostgreSQL database for server integration tests
2. A running MongoDB instance for server integration tests
3. A running IndoxRouter server for client integration tests
4. Required environment variables set (details below)

## Environment Variables

### For Server Tests

- `DATABASE_URL`: PostgreSQL connection string (required for integration tests)
- `MONGODB_URI`: MongoDB connection string (required for integration tests)

### For Client Tests

- `INDOX_ROUTER_API_KEY`: Valid API key for the IndoxRouter service (required for integration tests)

## Running the Tests

### Server Tests

Navigate to the server directory:

```bash
cd indoxRouter_server
```

To run all tests:

```bash
python run_tests.py
```

To run only unit tests:

```bash
python run_tests.py --unit
```

To run only integration tests:

```bash
python run_tests.py --integration
```

To run tests with more detailed output:

```bash
python run_tests.py --verbose
```

### Client Tests

Navigate to the client directory:

```bash
cd indoxRouter_client
```

To run all tests:

```bash
python run_tests.py
```

To run only unit tests:

```bash
python run_tests.py --unit
```

To run only integration tests:

```bash
python run_tests.py --integration
```

To run tests with more detailed output:

```bash
python run_tests.py --verbose
```

## Setting Up the Test Environment

### Starting the Databases for Server Tests

You can use Docker to run the required databases:

```bash
docker-compose up -d postgres mongodb
```

Then set the environment variables:

```bash
# Unix/Linux/Mac
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/indoxrouter"
export MONGODB_URI="mongodb://localhost:27017/indoxrouter"

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/indoxrouter"
$env:MONGODB_URI="mongodb://localhost:27017/indoxrouter"
```

### Starting the Server for Client Tests

Start the IndoxRouter server:

```bash
cd indoxRouter_server
docker-compose up -d
```

Then set the API key environment variable:

```bash
# Unix/Linux/Mac
export INDOX_ROUTER_API_KEY="your_api_key"

# Windows (PowerShell)
$env:INDOX_ROUTER_API_KEY="your_api_key"
```

## Troubleshooting

### Common Issues

1. **Database connection errors**: Ensure the databases are running and the connection URLs are correct.
2. **Authentication errors**: Check that the API key is valid and correctly set in the environment.

3. **Import errors**: Make sure you're running the tests from the correct directory and have installed all requirements.

### Getting Help

If you encounter issues with the tests, please check the logs for detailed error messages or consult the project documentation.
