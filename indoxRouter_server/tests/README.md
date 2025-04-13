# IndoxRouter Testing Guide

This guide explains how to test both MongoDB and PostgreSQL databases in the IndoxRouter server.

## MongoDB Testing with mongomock_motor

This project uses `mongomock_motor` to create isolated MongoDB test environments. This allows tests to run without connecting to a real MongoDB database, making tests faster and more reliable.

### How to Use the MongoDB Fixture

The `mongo_db` fixture in `conftest.py` provides a mocked MongoDB client for your tests:

```python
@pytest.fixture
async def mongo_db():
    """Fixture to provide a mock MongoDB connection for testing."""
    # Create a mock MongoDB client
    mock_client = AsyncMongoMockClient()
    db = mock_client["indoxrouter"]

    # Initialize collections and seed test data
    ...

    yield db
```

#### Basic Usage in Tests

To use this fixture in your tests:

1. First, make your test method `async` and add the `@pytest.mark.asyncio` decorator
2. Add the `mongo_db` parameter to your test function
3. Use the provided MongoDB client for your operations

```python
@pytest.mark.asyncio
async def test_your_feature(mongo_db):
    # Use mongo_db for database operations
    result = await mongo_db.collection_name.insert_one({"test": "data"})
    assert result.inserted_id is not None
```

#### Testing Database Functions

When testing functions that use MongoDB, you need to patch the database access:

```python
@pytest.mark.asyncio
async def test_database_function(mongo_db):
    # Patch the database access function to use our mock
    with patch("app.db.database.get_mongo_db", return_value=mongo_db):
        result = await your_function()

    # Assert expected behaviors
    assert result is not None
```

## PostgreSQL Testing with Mocks

For PostgreSQL testing, we use Python's `unittest.mock` library to create mock connections and cursors. This approach allows us to test database functions without requiring an actual PostgreSQL server.

### How to Mock PostgreSQL

There are two approaches to mocking PostgreSQL:

1. **Using MagicMock**: Simple mocking with less control but easier setup
2. **Using Our Custom Fixtures**: More control over behavior, better for complex tests

#### Approach 1: Using MagicMock

```python
@patch("app.db.database.pg_pool")
def test_database_function(self, mock_pg_pool):
    # Create a mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Configure the mocks
    mock_pg_pool.getconn.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Set expected return values
    mock_cursor.fetchone.return_value = {"id": 123, "username": "testuser"}

    # Call the function under test
    result = get_user_by_id(123)

    # Assert expected behaviors
    assert result["id"] == 123
    assert result["username"] == "testuser"

    # Verify SQL execution
    mock_cursor.execute.assert_called_once()
```

#### Approach 2: Using Our Custom Fixtures

We provide reusable PostgreSQL fixtures in `tests/fixtures/pg_test_fixture.py`:

```python
# Import our custom PostgreSQL fixtures
from tests.fixtures.pg_test_fixture import (
    MockCursor,
    MockConnection,
    setup_mock_user_response,
    patched_pg_pool
)

def test_database_function(self, patched_pg_pool):
    # Unpack the fixture - it gives you mock_pg_pool, mock_conn, and mock_cursor
    mock_pg_pool, mock_conn, mock_cursor = patched_pg_pool

    # Setup the mock with our helper function
    user_data = setup_mock_user_response(mock_cursor, user_id=123)

    # Call the function under test
    result = get_user_by_id(123)

    # Assert expected behaviors
    assert result["id"] == 123
    assert result["username"] == "testuser"

    # Verify SQL execution - our mock records all calls
    assert len(mock_cursor.execute_calls) == 1
    sql, params = mock_cursor.execute_calls[0]
    assert "user" in sql.lower()
```

### Available PostgreSQL Fixtures

Our `pg_test_fixture.py` file provides several useful tools:

1. `MockCursor` class: A realistic mock cursor that records SQL executions and returns configurable values
2. `MockConnection` class: A mock connection that supports context managers and tracks commit/rollback calls
3. `patched_pg_pool` fixture: Patches the database pool and returns pre-configured mocks
4. Helper functions like `setup_mock_user_response` to prepare common test data

### Example Test Files

#### MongoDB Tests

- `test_mongo_db.py`: Shows basic MongoDB operations with mongomock_motor
- `test_conversation_db.py`: Tests the conversation-related database functions

#### PostgreSQL Tests

- `test_postgres_db.py`: Shows basic PostgreSQL operations with mocks
- `test_user_db.py`: Tests the user-related database functions

## Test Data Seeding

### MongoDB Seeding

The `mongo_db` fixture in `conftest.py` seeds the database with test data:

- Users (with API keys)
- Models (with pricing information)
- Provider information
- Usage data
- Conversations

### PostgreSQL Mocking

For PostgreSQL tests, you can:

1. Configure mock values directly in each test function
2. Use the helper functions in `pg_test_fixture.py` to set up common test data
3. Create your own helper functions for specific test cases

## Running the Tests

To run the tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_conversation_db.py

# Run with verbose output
pytest -v tests/unit/test_postgres_db.py
```
