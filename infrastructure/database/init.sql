-- Solar AIM Database Initialization
-- This script runs automatically when the PostgreSQL container starts.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- ENUMS
-- ============================================================

DO $$ BEGIN
  CREATE TYPE user_role AS ENUM ('admin', 'engineer', 'manager');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE inverter_status AS ENUM ('online', 'offline', 'error', 'maintenance');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE string_status AS ENUM ('active', 'inactive', 'error');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE maintenance_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role            user_role    NOT NULL DEFAULT 'engineer',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

-- ============================================================
-- SECTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS sections (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ
);

-- ============================================================
-- INVERTERS
-- ============================================================

CREATE TABLE IF NOT EXISTS inverters (
    id           SERIAL PRIMARY KEY,
    section_id   INTEGER         NOT NULL REFERENCES sections(id),
    name         VARCHAR(100)    NOT NULL,
    model_number VARCHAR(100),
    status       inverter_status NOT NULL DEFAULT 'offline',
    created_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_inverters_section_id ON inverters(section_id);

-- ============================================================
-- STRINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS strings (
    id          SERIAL PRIMARY KEY,
    inverter_id INTEGER      NOT NULL REFERENCES inverters(id),
    name        VARCHAR(100) NOT NULL,
    panel_count INTEGER      NOT NULL DEFAULT 0,
    status      string_status NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_strings_inverter_id ON strings(inverter_id);

-- ============================================================
-- STRING READINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS string_readings (
    id          SERIAL PRIMARY KEY,
    string_id   INTEGER     NOT NULL REFERENCES strings(id),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    voltage     FLOAT,
    current     FLOAT,
    power       FLOAT,
    temperature FLOAT,
    irradiance  FLOAT
);

CREATE INDEX IF NOT EXISTS idx_string_readings_string_id ON string_readings(string_id);
CREATE INDEX IF NOT EXISTS idx_string_readings_recorded_at ON string_readings(recorded_at);

-- ============================================================
-- WEATHER READINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS weather_readings (
    id             SERIAL PRIMARY KEY,
    recorded_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    temperature    FLOAT,
    humidity       FLOAT,
    irradiance     FLOAT,
    wind_speed     FLOAT,
    wind_direction VARCHAR(10),
    precipitation  FLOAT
);

CREATE INDEX IF NOT EXISTS idx_weather_readings_recorded_at ON weather_readings(recorded_at);

-- ============================================================
-- BASELINES
-- ============================================================

CREATE TABLE IF NOT EXISTS baselines (
    id               SERIAL PRIMARY KEY,
    string_id        INTEGER NOT NULL REFERENCES strings(id),
    expected_power   FLOAT,
    expected_voltage FLOAT,
    expected_current FLOAT,
    expected_energy  FLOAT,
    valid_from       TIMESTAMPTZ,
    valid_until      TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_baselines_string_id ON baselines(string_id);

-- ============================================================
-- ALERTS
-- ============================================================

CREATE TABLE IF NOT EXISTS alerts (
    id          SERIAL PRIMARY KEY,
    inverter_id INTEGER REFERENCES inverters(id),
    string_id   INTEGER REFERENCES strings(id),
    type        VARCHAR(50)    NOT NULL,
    severity    alert_severity NOT NULL,
    message     TEXT           NOT NULL,
    status      alert_status   NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

-- ============================================================
-- MAINTENANCE LOGS
-- ============================================================

CREATE TABLE IF NOT EXISTS maintenance_logs (
    id             SERIAL PRIMARY KEY,
    inverter_id    INTEGER            REFERENCES inverters(id),
    string_id      INTEGER            REFERENCES strings(id),
    user_id        INTEGER            NOT NULL REFERENCES users(id),
    title          VARCHAR(200)       NOT NULL,
    description    TEXT,
    scheduled_date TIMESTAMP,
    completed_date TIMESTAMP,
    status         maintenance_status NOT NULL DEFAULT 'scheduled',
    created_at     TIMESTAMPTZ        NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_maintenance_logs_status ON maintenance_logs(status);

-- ============================================================
-- SYSTEM SETTINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS system_settings (
    id          SERIAL PRIMARY KEY,
    key         VARCHAR(100) NOT NULL UNIQUE,
    value       TEXT,
    description VARCHAR(255),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ
);

-- ============================================================
-- SEED DATA
-- ============================================================

INSERT INTO users (username, email, hashed_password, role, is_active)
VALUES
    ('admin', 'admin@solaraim.com', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5y7q8z9yF5a2b3c4d5e6f7g8h', 'admin', TRUE),
    ('engineer', 'engineer@solaraim.com', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5y7q8z9yF5a2b3c4d5e6f7g8h', 'engineer', TRUE),
    ('manager', 'manager@solaraim.com', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5y7q8z9yF5a2b3c4d5e6f7g8h', 'manager', TRUE)
ON CONFLICT (username) DO NOTHING;

INSERT INTO sections (name, description)
VALUES
    ('Section A', 'North field array'),
    ('Section B', 'East field array'),
    ('Section C', 'South field array'),
    ('Section D', 'West field array')
ON CONFLICT DO NOTHING;
