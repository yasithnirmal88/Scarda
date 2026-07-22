-- Solar AIM Database Initialization
-- This script runs automatically when the PostgreSQL container starts.
--
-- NOTE: The full schema is managed by Alembic migrations
-- (backend/alembic/versions/initial_schema.py).
-- This file handles only PostgreSQL extensions and very small startup
-- tasks that must run before Alembic.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- For development / demo environments only: uncomment the INSERT
-- statements below to seed initial data.  In production, use Alembic
-- data migrations or a separate seed script.
--
-- INSERT INTO users (username, email, hashed_password, role, is_active)
-- VALUES
--     ('admin', 'admin@solaraim.com', '<bcrypt-hash>', 'admin', TRUE),
--     ('engineer', 'engineer@solaraim.com', '<bcrypt-hash>', 'engineer', TRUE),
--     ('manager', 'manager@solaraim.com', '<bcrypt-hash>', 'manager', TRUE)
-- ON CONFLICT (username) DO NOTHING;
