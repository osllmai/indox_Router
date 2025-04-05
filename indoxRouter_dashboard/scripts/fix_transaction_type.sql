-- Fix schema issues script for IndoxRouter Dashboard
-- This script adds the transaction_type column to the billing_transactions table if it doesn't exist

-- Check if transaction_type column exists in billing_transactions and add it if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'billing_transactions' AND column_name = 'transaction_type'
    ) THEN
        RAISE NOTICE 'Adding transaction_type column to billing_transactions table';
        ALTER TABLE billing_transactions 
        ADD COLUMN transaction_type VARCHAR(50) NOT NULL DEFAULT 'purchase';
    ELSE
        RAISE NOTICE 'transaction_type column already exists in billing_transactions table';
    END IF;
END $$;

-- Confirmation message
DO $$
BEGIN
    RAISE NOTICE 'Schema fixes have been applied';
END $$; 