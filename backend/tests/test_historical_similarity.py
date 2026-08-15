"""Integration tests for the historical-similarity anomaly algorithm.

Covers the Phase-19 acceptance scenarios using a fake reading repository that
implements ``similarity_for_conditions``:

* Test 7 — expected power + deviation + anomaly status computed from history.
* Test 2 (Phase 13) — cloud transition must NOT produce a false anomaly.
* Test 3 (Phase 14) — a degraded string under otherwise similar weather must
  be flagged abnormal.

These exercise the real ``HistoricalBaselineProvider.explain_reading`` logic
end-to-end; no mocks of the provider itself.
"""

from __future__ import annotations

import pytest

from app.services.alert_engine.baseline_provider import (
    HistoricalBaselineProvider,
    WeatherAwareBaselineProvider,
)
from app.services.alert_engine.config import AlertEngineConfig


class _FakeSimilarityRepo:
    """Fake repo implementing the robust similarity contract.

    Returns canned stats so the provider's decision logic is exercised
    deterministically without a database.
    """

    def __init__(self, stats: dict | None) -> None:
        self._stats = stats
        self.calls: list[dict] = []

    def similarity_for_conditions(
        self,
        string_id: int,
        irradiance: float,
        temperature: float,
        *,
        reference_at=None,
        irradiance_band=None,
        temp_band=None,
        time_of_day_band_hours=None,
        lookback_days=None,
        min_samples=None,
    ) -> dict | None:
        self.calls.append(
            {
                "string_id": string_id,
                "irradiance": irradiance,
                "temperature": temperature,
                "irradiance_band": irradiance_band,
                "temp_band": temp_band,
                "lookback_days": lookback_days,
                "min_samples": min_samples,
            }
        )
        return self._stats


def _provider(stats: dict | None) -> HistoricalBaselineProvider:
    cfg = AlertEngineConfig()
    return HistoricalBaselineProvider(
        config=cfg,
        reading_repo_factory=lambda: _FakeSimilarityRepo(stats),
        physics_provider=WeatherAwareBaselineProvider(cfg),
    )


# --- Test 7: expected power / deviation / status from known history ---------


class TestHistoricalSimilarityComputation:
    def test_explain_returns_expected_and_deviation(self) -> None:
        # 37 historical samples, median 4.2 kW, MAD 0.15 kW
        stats = {
            "sample_count": 37,
            "median_power": 4200.0,
            "mad": 150.0,
            "iqr": 200.0,
            "min_power": 3900.0,
            "max_power": 4500.0,
            "powers": [4200.0],
        }
        provider = _provider(stats)
        result = provider.explain_reading(
            "17",
            power=1800.0,
            weather={"irradiance": 820.0, "ambient_temperature": 29.0},
        )
        assert result["historical_sample_count"] == 37
        assert result["expected_power"] == pytest.approx(4200.0)
        assert result["deviation"] == pytest.approx(-2400.0)
        assert result["deviation_pct"] < 0
        assert result["status"] == "abnormal"
        assert result["method"] == "historical_similarity"

    def test_query_passes_configured_tolerances(self) -> None:
        stats = {
            "sample_count": 10,
            "median_power": 4000.0,
            "mad": 100.0,
            "iqr": 150.0,
            "min_power": 3800.0,
            "max_power": 4200.0,
            "powers": [4000.0],
        }
        cfg = AlertEngineConfig()
        repo = _FakeSimilarityRepo(stats)
        provider = HistoricalBaselineProvider(
            config=cfg,
            reading_repo_factory=lambda: repo,
            physics_provider=WeatherAwareBaselineProvider(cfg),
        )
        provider.explain_reading(
            "1", power=2000.0, weather={"irradiance": 820.0, "ambient_temperature": 29.0}
        )
        call = repo.calls[0]
        assert call["irradiance_band"] == cfg.historical_irradiance_band
        assert call["temp_band"] == cfg.historical_temp_band
        assert call["lookback_days"] == cfg.historical_lookback_days
        assert call["min_samples"] == cfg.historical_min_samples


# --- Test 2 (Phase 13): cloud transition must NOT alert ---------------------


class TestCloudTransitionNoFalseAlert:
    def test_cloud_drop_matches_historical_cloud_power(self) -> None:
        # Under 400 W/m² the string historically produced ~2.0-2.2 kW.
        # Current power 2.1 kW under the same irradiance → expected ~2.1 kW
        # → no deviation → NO anomaly.
        stats = {
            "sample_count": 22,
            "median_power": 2100.0,
            "mad": 120.0,
            "iqr": 180.0,
            "min_power": 1900.0,
            "max_power": 2300.0,
            "powers": [2100.0],
        }
        provider = _provider(stats)
        result = provider.explain_reading(
            "5",
            power=2100.0,
            weather={"irradiance": 400.0, "ambient_temperature": 27.0},
        )
        assert result["status"] == "normal"
        assert result["deviation_pct"] == pytest.approx(0.0, abs=1.0)
        assert result["expected_power"] == pytest.approx(2100.0)

    def test_slightly_below_median_but_within_band_is_normal(self) -> None:
        # Current 2.0 kW vs median 2.1 kW, MAD 0.12 → within MAD*multiplier
        # band → normal (cloud noise, not a fault).
        stats = {
            "sample_count": 22,
            "median_power": 2100.0,
            "mad": 120.0,
            "iqr": 180.0,
            "min_power": 1900.0,
            "max_power": 2300.0,
            "powers": [2100.0],
        }
        provider = _provider(stats)
        result = provider.explain_reading(
            "5",
            power=2000.0,
            weather={"irradiance": 400.0, "ambient_temperature": 27.0},
        )
        assert result["status"] == "normal"


# --- Test 3 (Phase 14): degraded string detected ---------------------------


class TestDegradedStringDetected:
    def test_low_power_under_good_weather_is_abnormal(self) -> None:
        # Historically ~4.2 kW under 820 W/m². Current 1.8 kW is a severe
        # underperformance → anomaly.
        stats = {
            "sample_count": 37,
            "median_power": 4200.0,
            "mad": 150.0,
            "iqr": 220.0,
            "min_power": 3900.0,
            "max_power": 4500.0,
            "powers": [4200.0],
        }
        provider = _provider(stats)
        result = provider.explain_reading(
            "17",
            power=1800.0,
            weather={"irradiance": 820.0, "ambient_temperature": 29.0},
        )
        assert result["status"] == "abnormal"
        assert result["deviation"] == pytest.approx(-2400.0)
        assert result["anomaly_score"] > 0

    def test_moderate_underperformance_is_abnormal(self) -> None:
        # Expected 4.2 kW, actual 2.0 kW (Phase-5 degraded-string example).
        stats = {
            "sample_count": 37,
            "median_power": 4200.0,
            "mad": 150.0,
            "iqr": 220.0,
            "min_power": 3900.0,
            "max_power": 4500.0,
            "powers": [4200.0],
        }
        provider = _provider(stats)
        result = provider.explain_reading(
            "17",
            power=2000.0,
            weather={"irradiance": 820.0, "ambient_temperature": 29.0},
        )
        assert result["status"] == "abnormal"


# --- Edge cases: insufficient history, night, unresolved id -----------------


class TestExplainFallbacks:
    def test_insufficient_history_reports_status(self) -> None:
        provider = _provider(None)  # repo returns None → not enough samples
        result = provider.explain_reading(
            "1", power=2000.0, weather={"irradiance": 820.0, "ambient_temperature": 29.0}
        )
        assert result["status"] == "insufficient_history"
        assert result["historical_sample_count"] == 0
        assert result["method"] == "physics_fallback"

    def test_night_uses_physics_zero(self) -> None:
        provider = _provider(
            {"sample_count": 5, "median_power": 0.0, "mad": 0.0, "iqr": 0.0,
             "min_power": 0.0, "max_power": 0.0, "powers": [0.0]}
        )
        result = provider.explain_reading(
            "1", power=0.0, weather={"irradiance": 5.0, "ambient_temperature": 15.0}
        )
        assert result["status"] == "night"
        assert result["expected_power"] == 0.0

    def test_composite_id_unresolved_uses_physics(self) -> None:
        provider = _provider(
            {"sample_count": 5, "median_power": 4200.0, "mad": 150.0, "iqr": 200.0,
             "min_power": 3900.0, "max_power": 4500.0, "powers": [4200.0]}
        )
        result = provider.explain_reading(
            "SEC01-INV01-STR01",
            power=1800.0,
            weather={"irradiance": 820.0, "ambient_temperature": 29.0},
        )
        # Composite ids can't be resolved to a FK in the unit-test path, so
        # the provider reports unresolved_id and falls back to physics.
        assert result["status"] == "unresolved_id"
        assert result["method"] == "physics_fallback"
