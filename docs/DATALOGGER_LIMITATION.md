# Datalogger Frequency & Alerting Limitation

## Operational Assumption

Scarda's alert engine is designed around **frequent measurements** (currently
10-minute intervals via the scheduler). The anomaly detection, historical
similarity, and confirmation engine all assume that readings arrive
approximately every 10 minutes.

## If the Real Datalogger Uploads Daily

If the company's Huawei datalogger only uploads data once per day (a common
scenario for some FusionSolar installations), the following behaviors apply:

| Capability | Status | Notes |
|-----------|--------|-------|
| **Storage** | ✅ Works | Daily readings are stored in TimescaleDB without issue |
| **Historical analysis** | ✅ Works | Historical similarity algorithm functions with daily data |
| **Backfill** | ✅ Works | 90-day backfill retrieves whatever resolution the API provides |
| **Near-real-time alerts** | ❌ Retrospective only | Alerts fire after the daily upload, not when the fault occurs |
| **Confirmation engine** | ⚠️ Degraded | The 2-cycle confirmation threshold would span 2 days instead of 20 minutes |
| **WebSocket live feed** | ❌ No live updates | Frontend would only see new data once per day |

## Impact on Alert Timing

With 10-minute data:
- Fault occurs at 12:00
- First bad reading at 12:10 → Pending created
- Second bad reading at 12:20 → Alert confirmed (20 minutes)

With daily data:
- Fault occurs at 12:00 on Day 1
- First bad reading arrives Day 2 (daily upload) → Pending created
- Second bad reading arrives Day 3 → Alert confirmed (up to 48 hours late)

## Recommendation

Near-real-time alarming requires an appropriate real-time or high-frequency data
source. **Do NOT fake a solution.** If the company's datalogger only provides
daily uploads:

1. Document that alerts are **retrospective**, not real-time
2. Consider integrating a separate high-frequency monitoring source if real-time
   alerting is required
3. Adjust the confirmation threshold (`THRESHOLD_CONFIRMATION_CYCLES`) and
   `THRESHOLD_MAX_CONFIRMATION_DELAY_MINUTES` to account for the daily cycle

## What Scarda Does NOT Do

- Scarda does NOT interpolate or fabricate readings between actual measurements
- Scarda does NOT generate synthetic data (Mock FusionSolar is the only data
  generator, used exclusively for development/testing)
- Scarda does NOT pretend to have real-time data when the source is daily

## Configuration

The polling interval is configurable via `SCHEDULER_SIMULATOR_INTERVAL_MINUTES`
(default: 10). If the real datalogger provides data at a different frequency,
adjust this setting to match. The system will work correctly at any interval,
but alert latency scales with the polling period.
