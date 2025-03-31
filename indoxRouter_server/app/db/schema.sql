-- IndoxRouter Server Database Schema
-- This file contains the SQL schema for the PostgreSQL database

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    credits DECIMAL(10, 4) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    account_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP
);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    permissions JSONB DEFAULT '{}'::jsonb
);

-- API Requests table (for tracking usage)
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

-- Billing Transactions table
CREATE TABLE IF NOT EXISTS billing_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id VARCHAR(255) NOT NULL UNIQUE,
    amount DECIMAL(10, 4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    transaction_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    payment_method VARCHAR(50),
    description TEXT,
    reference_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Usage Daily Summary (for dashboard metrics)
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

-- Pricing Plans
CREATE TABLE IF NOT EXISTS pricing_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    monthly_price DECIMAL(10, 2) NOT NULL,
    annual_price DECIMAL(10, 2) NOT NULL,
    credit_amount DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    features JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- User Subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES pricing_plans(id),
    subscription_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    start_date TIMESTAMP NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP,
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    auto_renew BOOLEAN DEFAULT TRUE,
    payment_provider VARCHAR(50),
    payment_provider_subscription_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Provider Configurations (API keys, defaults, etc.)
CREATE TABLE IF NOT EXISTS providers (
    id SERIAL PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255),
    is_enabled BOOLEAN DEFAULT TRUE,
    configuration JSONB DEFAULT '{}'::jsonb,
    cost_per_1k_input_tokens DECIMAL(10, 6) DEFAULT 0,
    cost_per_1k_output_tokens DECIMAL(10, 6) DEFAULT 0,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Models (all available models across providers)
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL REFERENCES providers(provider_id),
    model_id VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    capabilities JSONB DEFAULT '["chat", "completion"]'::jsonb,
    cost_per_1k_input_tokens DECIMAL(10, 6) DEFAULT 0,
    cost_per_1k_output_tokens DECIMAL(10, 6) DEFAULT 0,
    context_length INTEGER DEFAULT 4096,
    token_limit INTEGER DEFAULT 4096,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(provider_id, model_id)
);

-- System Settings
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, description)
VALUES 
('default_provider', '"openai"', 'Default provider for API requests'),
('default_chat_model', '"gpt-4o-mini"', 'Default model for chat completion requests'),
('default_completion_model', '"gpt-4o-mini"', 'Default model for text completion requests'),
('default_embedding_model', '"text-embedding-3-large"', 'Default model for embedding requests'),
('rate_limit_enabled', 'true', 'Whether rate limiting is enabled'),
('rate_limit_requests', '100', 'Number of requests allowed per period'),
('rate_limit_period_seconds', '60', 'Rate limit period in seconds')
ON CONFLICT (setting_key) DO NOTHING;

-- Insert default providers
INSERT INTO providers (provider_id, display_name, is_enabled, cost_per_1k_input_tokens, cost_per_1k_output_tokens)
VALUES 
('openai', 'OpenAI', TRUE, 0.0005, 0.0015),
('anthropic', 'Anthropic', TRUE, 0.0008, 0.0024),
('cohere', 'Cohere', TRUE, 0.0001, 0.0003),
('google', 'Google', TRUE, 0.0002, 0.0006),
('mistral', 'Mistral', TRUE, 0.0002, 0.0006)
ON CONFLICT (provider_id) DO NOTHING; 