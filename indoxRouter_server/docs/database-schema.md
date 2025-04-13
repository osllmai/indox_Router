# Database Schema

IndoxRouter uses a dual-database approach with PostgreSQL for relational data and MongoDB for document data.

## PostgreSQL Schema

PostgreSQL is used for storing user-related data, API keys, and aggregated usage statistics.

### Tables

#### users

Stores user account information.

| Column        | Type         | Description                     |
| ------------- | ------------ | ------------------------------- |
| id            | SERIAL       | Primary key                     |
| username      | VARCHAR(255) | Unique username                 |
| email         | VARCHAR(255) | Unique email address            |
| password      | VARCHAR(255) | Hashed password                 |
| credits       | DECIMAL      | Available credits for API usage |
| is_active     | BOOLEAN      | Account status                  |
| account_tier  | VARCHAR(50)  | User's subscription tier        |
| created_at    | TIMESTAMP    | Account creation timestamp      |
| updated_at    | TIMESTAMP    | Last update timestamp           |
| last_login_at | TIMESTAMP    | Last login timestamp            |

#### api_keys

Stores API keys associated with user accounts.

| Column       | Type         | Description                     |
| ------------ | ------------ | ------------------------------- |
| id           | SERIAL       | Primary key                     |
| user_id      | INTEGER      | Foreign key to users table      |
| api_key      | VARCHAR(255) | Unique API key                  |
| name         | VARCHAR(255) | Key name/description            |
| is_active    | BOOLEAN      | Key status                      |
| created_at   | TIMESTAMP    | Creation timestamp              |
| expires_at   | TIMESTAMP    | Expiration timestamp (optional) |
| last_used_at | TIMESTAMP    | Last usage timestamp            |
| permissions  | JSONB        | Key-specific permissions        |

#### api_requests

Stores a log of API requests.

| Column           | Type         | Description                      |
| ---------------- | ------------ | -------------------------------- |
| id               | SERIAL       | Primary key                      |
| user_id          | INTEGER      | Foreign key to users table       |
| api_key_id       | INTEGER      | Foreign key to api_keys table    |
| request_id       | VARCHAR(255) | Unique request identifier        |
| endpoint         | VARCHAR(50)  | API endpoint                     |
| model            | VARCHAR(100) | Model identifier                 |
| provider         | VARCHAR(50)  | Provider identifier              |
| tokens_input     | INTEGER      | Input token count                |
| tokens_output    | INTEGER      | Output token count               |
| tokens_total     | INTEGER      | Total token count                |
| cost             | DECIMAL      | Request cost                     |
| duration_ms      | INTEGER      | Request duration in milliseconds |
| status_code      | INTEGER      | HTTP response status code        |
| error_message    | TEXT         | Error message (if any)           |
| ip_address       | VARCHAR(50)  | Client IP address                |
| user_agent       | TEXT         | Client user agent                |
| created_at       | TIMESTAMP    | Request timestamp                |
| request_params   | JSONB        | Request parameters               |
| response_summary | TEXT         | Summary of the response          |

#### billing_transactions

Stores billing transactions for credit purchases or usage.

| Column           | Type         | Description                   |
| ---------------- | ------------ | ----------------------------- |
| id               | SERIAL       | Primary key                   |
| user_id          | INTEGER      | Foreign key to users table    |
| transaction_id   | VARCHAR(255) | Unique transaction identifier |
| amount           | DECIMAL      | Transaction amount            |
| currency         | VARCHAR(3)   | Currency code                 |
| transaction_type | VARCHAR(50)  | Type of transaction           |
| status           | VARCHAR(50)  | Transaction status            |
| payment_method   | VARCHAR(50)  | Payment method used           |
| description      | TEXT         | Transaction description       |
| reference_id     | VARCHAR(255) | External reference ID         |
| created_at       | TIMESTAMP    | Creation timestamp            |
| updated_at       | TIMESTAMP    | Last update timestamp         |

#### usage_daily_summary

Stores aggregated daily usage statistics by user.

| Column              | Type      | Description                |
| ------------------- | --------- | -------------------------- |
| id                  | SERIAL    | Primary key                |
| user_id             | INTEGER   | Foreign key to users table |
| date                | DATE      | Usage date                 |
| total_requests      | INTEGER   | Total number of requests   |
| total_tokens_input  | INTEGER   | Total input tokens         |
| total_tokens_output | INTEGER   | Total output tokens        |
| total_tokens        | INTEGER   | Total tokens               |
| total_cost          | DECIMAL   | Total cost                 |
| created_at          | TIMESTAMP | Creation timestamp         |
| updated_at          | TIMESTAMP | Last update timestamp      |

## MongoDB Collections

MongoDB is used for storing detailed usage logs, model information, caching, and other document-based data.

### Collections

#### model_usage

Stores detailed usage logs for each model request.

| Field             | Type     | Description                 |
| ----------------- | -------- | --------------------------- |
| \_id              | ObjectId | Unique identifier           |
| user_id           | Integer  | User ID                     |
| provider          | String   | Provider name               |
| model             | String   | Model name                  |
| tokens_prompt     | Integer  | Number of prompt tokens     |
| tokens_completion | Integer  | Number of completion tokens |
| tokens_total      | Integer  | Total token count           |
| cost              | Float    | Request cost                |
| latency           | Float    | Request latency in seconds  |
| request_id        | String   | Unique request identifier   |
| timestamp         | Date     | Request timestamp           |
| date              | String   | Request date (YYYY-MM-DD)   |
| session_id        | String   | Session identifier          |
| request           | Object   | Request details             |
| response          | Object   | Response details            |
| client_info       | Object   | Client information          |
| performance       | Object   | Performance metrics         |
| cache             | Object   | Cache information           |

#### model_cache

Stores cached model responses.

| Field        | Type     | Description                |
| ------------ | -------- | -------------------------- |
| \_id         | ObjectId | Unique identifier          |
| request_hash | String   | Unique hash of the request |
| provider     | String   | Provider name              |
| model        | String   | Model name                 |
| input_data   | Object   | Input request data         |
| output_data  | Object   | Output response data       |
| ttl          | Date     | Expiration timestamp       |
| created_at   | Date     | Creation timestamp         |

#### models

Stores information about available models.

| Field        | Type     | Description           |
| ------------ | -------- | --------------------- |
| \_id         | ObjectId | Unique identifier     |
| provider     | String   | Provider name         |
| name         | String   | Model name            |
| capabilities | Array    | Model capabilities    |
| description  | String   | Model description     |
| max_tokens   | Integer  | Maximum token limit   |
| pricing      | Object   | Pricing information   |
| metadata     | Object   | Additional metadata   |
| created_at   | Date     | Creation timestamp    |
| updated_at   | Date     | Last update timestamp |

#### conversations

Stores user conversations.

| Field      | Type     | Description              |
| ---------- | -------- | ------------------------ |
| \_id       | ObjectId | Unique identifier        |
| user_id    | Integer  | User ID                  |
| title      | String   | Conversation title       |
| messages   | Array    | Array of message objects |
| created_at | Date     | Creation timestamp       |
| updated_at | Date     | Last update timestamp    |

#### embeddings

Stores user-generated embeddings.

| Field      | Type     | Description              |
| ---------- | -------- | ------------------------ |
| \_id       | ObjectId | Unique identifier        |
| user_id    | Integer  | User ID                  |
| text       | String   | Original text            |
| embedding  | Array    | Vector embedding         |
| model      | String   | Model used for embedding |
| metadata   | Object   | Additional metadata      |
| created_at | Date     | Creation timestamp       |
