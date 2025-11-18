-- Database initialization script for PPE Detection
-- This script runs automatically when the PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS detection;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set default search path
ALTER DATABASE ppe_detection SET search_path TO public, detection, monitoring, analytics;

-- Create custom types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ppe_type') THEN
        CREATE TYPE ppe_type AS ENUM ('hardhat', 'safety_vest', 'safety_glasses', 'gloves', 'boots');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'violation_severity') THEN
        CREATE TYPE violation_severity AS ENUM ('low', 'medium', 'high', 'critical');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'alert_status') THEN
        CREATE TYPE alert_status AS ENUM ('pending', 'sent', 'acknowledged', 'resolved');
    END IF;
END$$;

-- Grant permissions
GRANT USAGE ON SCHEMA detection TO postgres;
GRANT USAGE ON SCHEMA monitoring TO postgres;
GRANT USAGE ON SCHEMA analytics TO postgres;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA detection TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA monitoring TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO postgres;

-- Create indexes for performance (will be created by Alembic migrations)
-- This is just for initial setup

-- Set timezone
SET timezone = 'UTC';

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully';
END$$;
