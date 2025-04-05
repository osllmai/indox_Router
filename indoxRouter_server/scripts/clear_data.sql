-- Clear data script for IndoxRouter
-- This script clears all user data while maintaining the database schema

-- Disable foreign key constraints temporarily
SET session_replication_role = 'replica';

-- Clear all the tables
TRUNCATE TABLE api_requests;
TRUNCATE TABLE api_keys;
TRUNCATE TABLE billing_transactions;
TRUNCATE TABLE usage_daily_summary;
TRUNCATE TABLE user_subscriptions;
TRUNCATE TABLE users;

-- System tables clearing optional - use these with caution
-- TRUNCATE TABLE system_settings;
-- TRUNCATE TABLE models;
-- TRUNCATE TABLE providers;

-- Re-enable foreign key constraints
SET session_replication_role = 'origin';

-- Confirmation message
DO $$
BEGIN
    RAISE NOTICE 'All data has been cleared from IndoxRouter database.';
END $$; 