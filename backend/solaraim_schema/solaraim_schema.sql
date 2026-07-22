-- ============================================================
-- SolarAIM TimescaleDB Schema
-- Run against the `solaraim` database
-- Usage:
--   docker exec -i timescaledb psql -U postgres -d solaraim < solaraim_schema.sql
-- ============================================================

-- Make sure the extension is enabled (safe if already enabled)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================
-- 1. HIERARCHY TABLES: sections -> inverters -> strings
-- ============================================================

CREATE TABLE IF NOT EXISTS sections (
    id          SERIAL PRIMARY KEY,
    code        TEXT UNIQUE NOT NULL,        -- e.g. 'Section-A'
    name        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inverters (
    id          SERIAL PRIMARY KEY,
    code        TEXT UNIQUE NOT NULL,        -- e.g. 'INV-01'
    section_id  INTEGER NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    name        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_inverters_section_id ON inverters(section_id);

CREATE TABLE IF NOT EXISTS strings (
    id          SERIAL PRIMARY KEY,
    code        TEXT UNIQUE NOT NULL,        -- e.g. 'STR-03'
    inverter_id INTEGER NOT NULL REFERENCES inverters(id) ON DELETE CASCADE,
    name        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_strings_inverter_id ON strings(inverter_id);

-- ============================================================
-- 2. TELEMETRY (HYPERTABLE) - one row per string per interval
--    Expected interval: every 10 minutes
-- ============================================================

CREATE TABLE IF NOT EXISTS string_readings (
    time         TIMESTAMPTZ NOT NULL,
    string_id    INTEGER NOT NULL REFERENCES strings(id) ON DELETE CASCADE,
    current      DOUBLE PRECISION,   -- amps
    voltage      DOUBLE PRECISION,   -- volts
    power        DOUBLE PRECISION,   -- watts (can be derived, but stored for query speed)
    temperature  DOUBLE PRECISION,   -- deg C (panel/ambient temp)
    irradiance   DOUBLE PRECISION,   -- W/m^2
    PRIMARY KEY (string_id, time)
);

-- Convert to a hypertable partitioned by time
SELECT create_hypertable(
    'string_readings',
    'time',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_string_readings_string_time
    ON string_readings (string_id, time DESC);

-- Compression: readings older than 7 days get compressed to save space
ALTER TABLE string_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'string_id'
);

SELECT add_compression_policy('string_readings', INTERVAL '7 days', if_not_exists => TRUE);

-- Optional: drop raw data older than 1 year (adjust/remove as needed)
-- SELECT add_retention_policy('string_readings', INTERVAL '365 days', if_not_exists => TRUE);

-- ============================================================
-- 3. CONTINUOUS AGGREGATE - hourly rollups for dashboards
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS string_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
    string_id,
    time_bucket('1 hour', time) AS bucket,
    AVG(current)     AS avg_current,
    AVG(voltage)      AS avg_voltage,
    AVG(power)        AS avg_power,
    AVG(temperature)  AS avg_temperature,
    AVG(irradiance)   AS avg_irradiance,
    MIN(power)        AS min_power,
    MAX(power)        AS max_power
FROM string_readings
GROUP BY string_id, bucket
WITH NO DATA;

SELECT add_continuous_aggregate_policy('string_readings_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset   => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '30 minutes',
    if_not_exists => TRUE
);

-- ============================================================
-- 4. BASELINES - expected operating ranges per string
--    Used by the alert engine to detect deviation from normal
-- ============================================================

CREATE TABLE IF NOT EXISTS string_baselines (
    string_id           INTEGER PRIMARY KEY REFERENCES strings(id) ON DELETE CASCADE,
    expected_current     DOUBLE PRECISION,
    expected_voltage      DOUBLE PRECISION,
    expected_power        DOUBLE PRECISION,
    tolerance_pct         DOUBLE PRECISION NOT NULL DEFAULT 10.0,  -- % deviation allowed before flagging
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 5. ALERTS - confirmed alerts (after repeated deviation checks)
-- ============================================================

CREATE TABLE IF NOT EXISTS alerts (
    id               SERIAL PRIMARY KEY,
    string_id        INTEGER NOT NULL REFERENCES strings(id) ON DELETE CASCADE,
    alert_type       TEXT NOT NULL,          -- e.g. 'low_power', 'high_temp', 'voltage_drop'
    severity         TEXT NOT NULL DEFAULT 'warning',  -- 'warning' | 'critical'
    status           TEXT NOT NULL DEFAULT 'active',   -- 'active' | 'resolved'
    deviation_count  INTEGER NOT NULL DEFAULT 1,       -- number of consecutive deviations seen
    details          JSONB,                  -- flexible extra info (values at trigger time, etc.)
    started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_string_id ON alerts(string_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);

-- ============================================================
-- Done. Verify with:
--   \dt
--   \d+ string_readings
-- ============================================================
