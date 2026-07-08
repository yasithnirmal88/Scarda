# Alert Engine

Deterministic rule-based anomaly detection engine for Solar AIM.

## Architecture

```
alert_engine/
├── alert_engine.py          # Main orchestrator
├── alert_generator.py       # Creates AlertData from rule results
├── alert_repository.py      # In-memory alert storage (Base + InMemory)
├── baseline_provider.py     # Expected values provider (Base + Static)
├── config.py                # Threshold configuration
├── confirmation_engine.py   # Pending/confirmation logic
├── deviation_calculator.py  # Deviation calculation
├── recommandations.py       # Rule-based recommendation mapping
├── rule_engine.py           # Modular rules with registry
├── types.py                 # Pydantic models and enums
└── README.md
```

## Design Principles

- **SOLID**: Single responsibility per class, dependency injection, interface segregation
- **Clean Architecture**: Independent of data source (FakeDataProvider / HuaweiDataProvider)
- **Deterministic**: No ML, no AI — pure rule-based anomaly detection

## Alert States

```
Pending → Active → Acknowledged → Resolved
                     ↓
                 Suppressed
```

## Confirmation Logic

A single anomalous reading creates a **pending** state. Only after N consecutive bad readings (default 2) is a **confirmed alert** created. If a reading returns to normal while pending, the pending state is cleared.

## Rules

| Rule                 | Condition                                      | Severity    |
|----------------------|------------------------------------------------|-------------|
| Current Low          | Current below threshold                        | WARNING+    |
| Voltage Low          | Voltage below threshold                        | WARNING+    |
| Power Low            | Power below threshold                          | WARNING+    |
| Offline              | Near-zero current AND voltage                  | CRITICAL    |
| Communication Failure| Status is offline                              | CRITICAL    |

## Usage

```python
from app.services.alert_engine import AlertEngine
from app.services.alert_engine.types import Reading
from datetime import datetime

engine = AlertEngine()

reading = Reading(
    string_id="SEC01-INV01-STR01",
    timestamp=datetime.now(),
    current=9.8,
    voltage=820.0,
    power=8036.0,
)

alerts = engine.process_reading(reading)
active = engine.get_active_alerts()
```
