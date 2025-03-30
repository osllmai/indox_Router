# Credit System

IndoxRouter includes a credit system that tracks and manages user credits for API usage. This guide explains how the credit system works and how to manage user credits.

## Overview

The credit system tracks the cost of each API request and deducts credits from the user's account accordingly. Credits are calculated based on the model used, the number of tokens processed, and the operation type.

## How Credits Are Calculated

Credits are calculated in real-time using the pricing information from the provider's model configuration. The calculation is done in the following steps:

1. The resource class (Chat, Completions, Embeddings, or Images) processes the request and gets the token usage from the provider's response.
2. The `calculate_cost` function from the `model_info` module calculates the cost based on the token usage and the pricing information in the provider's JSON configuration file.
3. The `_update_user_credit` method of the `BaseResource` class calls the `update_user_credit` function in the `database` module to update the user's credit in the database.

### Text Generation (Chat and Completions)

For text generation (chat and completions), the cost is calculated based on the number of tokens in the prompt and the completion:

```
cost = (tokens_prompt / 1000) * input_price + (tokens_completion / 1000) * output_price
```

Where:

- `tokens_prompt` is the number of tokens in the prompt
- `tokens_completion` is the number of tokens in the completion
- `input_price` is the price per 1,000 tokens for input
- `output_price` is the price per 1,000 tokens for output

### Embeddings

For embeddings, the cost is calculated based on the number of tokens in the text:

```
cost = (tokens_prompt / 1000) * input_price
```

Where:

- `tokens_prompt` is the number of tokens in the text
- `input_price` is the price per 1,000 tokens for input

### Image Generation

For image generation, the cost is calculated based on the model, size, quality, and number of images:

```
cost = base_cost * size_multiplier * quality_multiplier * n
```

Where:

- `base_cost` is the base cost per image
- `size_multiplier` is a multiplier based on the image size
- `quality_multiplier` is a multiplier based on the image quality
- `n` is the number of images

## Database Schema

The credit system uses the following database tables:

### Users Table

The `users` table stores user information, including their credit balance:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    credits DECIMAL(10, 4) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### API Requests Table

The `api_requests` table logs all API requests, including the cost and token usage:

```sql
CREATE TABLE api_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    endpoint VARCHAR(255) NOT NULL,
    cost DECIMAL(10, 4) NOT NULL,
    tokens INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Updating User Credits

The `update_user_credit` function in the `database` module updates a user's credit in the database:

```python
def update_user_credit(user_id: int, cost: float, endpoint: str, tokens_total: int = 0) -> bool:
    """
    Update a user's credit in the database.

    Args:
        user_id: The user ID.
        cost: The cost of the request.
        endpoint: The endpoint that was called.
        tokens_total: The total number of tokens used.

    Returns:
        True if successful, False otherwise.
    """
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # First, log the API request
                cur.execute(
                    """
                    INSERT INTO api_requests (user_id, endpoint, cost, tokens, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (user_id, endpoint, cost, tokens_total),
                )

                # Then, update the user's credit
                cur.execute(
                    """
                    UPDATE users
                    SET credits = credits - %s,
                        updated_at = NOW()
                    WHERE id = %s AND credits >= %s
                    RETURNING id, credits
                    """,
                    (cost, user_id, cost),
                )

                result = cur.fetchone()

                # If no rows were updated, the user doesn't have enough credits
                if not result:
                    logger.warning(f"User {user_id} doesn't have enough credits for this request")
                    # Rollback the transaction
                    conn.rollback()
                    return False

                # Commit the transaction
                conn.commit()
                logger.info(f"Updated credits for user {user_id}. New balance: {result[1]}")
                return True
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error updating user credit: {e}")
        return False
```

## Checking User Credits

The `get_user_usage` function in the `database` module gets a user's API usage statistics:

```python
def get_user_usage(user_id: int) -> Dict[str, Any]:
    """
    Get a user's API usage statistics from the external website database.

    Args:
        user_id: The user ID to look up

    Returns:
        Usage statistics
    """
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Adjust this query to match your website's database schema
                cur.execute(
                    """
                    SELECT
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN endpoint = 'chat' THEN 1 ELSE 0 END) as chat_requests,
                        SUM(CASE WHEN endpoint = 'embeddings' THEN 1 ELSE 0 END) as embedding_requests,
                        SUM(CASE WHEN endpoint = 'images' THEN 1 ELSE 0 END) as image_requests
                    FROM api_requests
                    WHERE user_id = %s AND created_at > NOW() - INTERVAL '30 days'
                    """,
                    (user_id,),
                )
                usage = cur.fetchone()
                return usage or {}
        finally:
            release_connection(conn)
    except Exception as e:
        logger.error(f"Error getting user usage: {e}")
        return {}
```

## Handling Insufficient Credits

If a user doesn't have enough credits for a request, the `update_user_credit` function returns `False`, and the API returns an `InsufficientCreditsError` exception.

## Adding Credits to a User's Account

To add credits to a user's account, you can use the following SQL query:

```sql
UPDATE users
SET credits = credits + :amount,
    updated_at = NOW()
WHERE id = :user_id
RETURNING id, credits;
```

Where:

- `:amount` is the amount of credits to add
- `:user_id` is the user ID

## Monitoring Credit Usage

You can monitor credit usage using the following SQL queries:

### Total Credit Usage by User

```sql
SELECT
    u.id,
    u.username,
    u.email,
    SUM(ar.cost) as total_cost,
    COUNT(*) as total_requests
FROM users u
JOIN api_requests ar ON u.id = ar.user_id
WHERE ar.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.id, u.username, u.email
ORDER BY total_cost DESC;
```

### Credit Usage by Endpoint

```sql
SELECT
    ar.endpoint,
    SUM(ar.cost) as total_cost,
    COUNT(*) as total_requests,
    AVG(ar.cost) as avg_cost_per_request
FROM api_requests ar
WHERE ar.created_at > NOW() - INTERVAL '30 days'
GROUP BY ar.endpoint
ORDER BY total_cost DESC;
```

### Credit Usage by Day

```sql
SELECT
    DATE_TRUNC('day', ar.created_at) as day,
    SUM(ar.cost) as total_cost,
    COUNT(*) as total_requests
FROM api_requests ar
WHERE ar.created_at > NOW() - INTERVAL '30 days'
GROUP BY day
ORDER BY day DESC;
```

## Best Practices

- Set a minimum credit threshold for users to prevent them from running out of credits unexpectedly.
- Implement a notification system to alert users when their credit balance is low.
- Provide a way for users to check their credit balance and usage history.
- Consider implementing a credit top-up system to allow users to add credits to their account.
- Monitor credit usage to identify patterns and optimize costs.
