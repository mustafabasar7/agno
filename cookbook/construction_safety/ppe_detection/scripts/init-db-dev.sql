-- Development database initialization script
-- Includes additional test data and development utilities

-- Run the main initialization
\i /docker-entrypoint-initdb.d/init.sql

-- Create development-specific schemas
CREATE SCHEMA IF NOT EXISTS testing;

-- Grant permissions for development
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA testing TO dev_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA testing TO dev_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA testing TO dev_user;

-- Enable additional extensions for development
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "tablefunc";

-- Create a function to truncate all tables (useful for testing)
CREATE OR REPLACE FUNCTION testing.truncate_all_tables() RETURNS void AS $$
DECLARE
    statements CURSOR FOR
        SELECT tablename FROM pg_tables
        WHERE schemaname IN ('detection', 'monitoring', 'analytics', 'testing')
        AND tablename NOT LIKE 'alembic%';
BEGIN
    FOR stmt IN statements LOOP
        EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.tablename) || ' CASCADE;';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create a function to generate test data
CREATE OR REPLACE FUNCTION testing.generate_test_data() RETURNS void AS $$
BEGIN
    RAISE NOTICE 'Generating test data...';
    -- Add test data generation logic here
    -- This will be implemented based on your schema
END;
$$ LANGUAGE plpgsql;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Development database initialization completed successfully';
END$$;
