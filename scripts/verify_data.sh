#!/bin/bash
DBEXEC="docker exec docker-db-1 psql -U postgres -d solar_aim"
q() { sg docker -c "$DBEXEC -c \"$1\"" 2>&1; }
echo "=== string_readings COUNT ==="; q "SELECT COUNT(*) FROM string_readings;"
echo "=== string_readings MIN/MAX recorded_at ==="; q "SELECT MIN(recorded_at), MAX(recorded_at) FROM string_readings;"
echo "=== string_readings DISTINCT string_id ==="; q "SELECT COUNT(DISTINCT string_id) FROM string_readings;"
echo "=== weather_readings COUNT ==="; q "SELECT COUNT(*) FROM weather_readings;"
echo "=== weather_readings MIN/MAX recorded_at ==="; q "SELECT MIN(recorded_at), MAX(recorded_at) FROM weather_readings;"
echo "=== chunks ==="; q "SELECT hypertable_name, count(*) AS chunks FROM timescaledb_information.chunks GROUP BY 1;"
echo "=== duplicate protection test (insert dup must fail) ==="
q "INSERT INTO string_readings (string_id, recorded_at, current, voltage, power, temperature, irradiance, status, created_at) SELECT string_id, recorded_at, current, voltage, power, temperature, irradiance, status, now() FROM string_readings LIMIT 1;"
