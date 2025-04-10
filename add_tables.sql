-- Create usage_daily_summary table
CREATE TABLE IF NOT EXISTS usage_daily_summary (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_requests INTEGER DEFAULT 0,
    total_tokens_input INTEGER DEFAULT 0,
    total_tokens_output INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Create api_requests table
CREATE TABLE IF NOT EXISTS api_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key_id INTEGER REFERENCES api_keys(id) ON DELETE SET NULL,
    request_id VARCHAR(255) NOT NULL,
    endpoint VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_total INTEGER DEFAULT 0,
    cost DECIMAL(10, 6) NOT NULL DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    status_code INTEGER DEFAULT 200,
    error_message TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    request_params JSONB,
    response_summary TEXT
); 