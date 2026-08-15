#!/bin/bash
# Phase 3: verify TimescaleDB hypertables, dimensions, indexes, constraints.
set -u
DBEXEC="docker exec docker-db-1 psql -U postgres -d solar_aim"

q() { sg docker -c "$DBEXEC -c \"$1\"" 2>&1; }

echo "=== 1. Hypertables ==="
q "SELECT hypertable_name FROM timescaledb_information.hypertables ORDER BY 1;"

echo ""; echo "=== 2. string_readings time dimension ==="
q "SELECT column_name, time_interval FROM timescaledb_information.dimensions WHERE hypertable_name='string_readings';"

echo ""; echo "=== 3. weather_readings time dimension ==="
q "SELECT column_name, time_interval FROM timescaledb_information.dimensions WHERE hypertable_name='weather_readings';"

echo ""; echo "=== 4. string_readings indexes ==="
q "SELECT indexname, indexdef FROM pg_indexes WHERE tablename='string_readings' ORDER BY indexname;"

echo ""; echo "=== 5. weather_readings indexes ==="
q "SELECT indexname, indexdef FROM pg_indexes WHERE tablename='weather_readings' ORDER BY indexname;"

echo ""; echo "=== 6. string_readings constraints ==="
q "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='string_readings'::regclass ORDER BY conname;"

echo ""; echo "=== 7. weather_readings constraints ==="
q "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='weather_readings'::regclass ORDER BY conname;"

echo ""; echo "=== 8. compression settings ==="
q "SELECT hypertable_name, config FROM timescaledb_information.compression_settings ORDER BY hypertable_name;"

echo ""; echo "=== 9. continuous aggregates ==="
q "SELECT view_name FROM timescaledb_information.continuous_aggregates ORDER BY view_name;"

echo ""; echo "=== 10. row counts (empty before backfill) ==="
q "SELECT 'string_readings' AS tbl, count(*) FROM string_readings UNION ALL SELECT 'weather_readings', count(*) FROM weather_readings;"
