"""Unit tests for the Tier-2 HistoricalBaselineProvider.

Uses a fake reading repository to verify the provider returns the empirical
median when enough history exists and degrades to the physics model otherwise.
"""

from __future__ import annotations

import pytest

from app.services.alert_engine.baseline_provider import HistoricalBaselineProvider
from app.services.alert_engine.config import AlertEngineConfig


class _FakeRepo:
    """Minimal fake of ReadingRepository for baseline testing."""

    def __init__(self, median_value: float | None) -> None:
        self._median = median_value
        self.calls: list[tuple] = []

    def median_power_for_conditions(
        self, string_id: int, irradiance: float, temperature: float,
        **kwargs,
    ) -> float | None:
        self.calls.append((string_id, irradiance, temperature))
        return self._median


class _FailingRepo:
    def median_power_for_conditions(self, *a, **kw) -> float | None:
        raise RuntimeError("db down")


class _NoRepoFactory:
    """Factory that simulates no DB available."""

    def __call__(self):
        return None


@pytest.fixture
def weather_midday() -> dict:
    return {"irradiance": 850.0, "ambient_temperature": 29.0}


class TestHistoricalFallback:
    def test_no_db_falls_back_to_physics(self, weather_midday) -> None:
        provider = HistoricalBaselineProvider(
            AlertEngineConfig(), reading_repo_factory=lambda: None
        )
        b = provider.get_baseline("1", weather_midday)
        # physics model at 850/29 -> ~209 W
        assert b.expected_power == pytest.approx(209.1, rel=1e-3)

    def test_thin_history_falls_back_to_physics(self, weather_midday) -> None:
        repo = _FakeRepo(median_value=None)  # repo says not enough data
        provider = HistoricalBaselineProvider(
            AlertEngineConfig(), reading_repo_factory=lambda: repo, min_samples=5
        )
        b = provider.get_baseline("1", weather_midday)
        assert b.expected_power == pytest.approx(209.1, rel=1e-3)
        assert len(repo.calls) == 1

    def test_no_weather_falls_back_to_physics_then_static(self) -> None:
        provider = HistoricalBaselineProvider(
            AlertEngineConfig(), reading_repo_factory=lambda: _FakeRepo(500.0)
        )
        b = provider.get_baseline("1", weather=None)
        cfg = AlertEngineConfig()
        assert b.expected_power == cfg.baseline_power  # static fallback

    def test_repo_error_falls_back_to_physics(self, weather_midday) -> None:
        provider = HistoricalBaselineProvider(
            AlertEngineConfig(), reading_repo_factory=lambda: _FailingRepo()
        )
        b = provider.get_baseline("1", weather_midday)
        assert b.expected_power == pytest.approx(209.1, rel=1e-3)

    def test_non_integer_id_falls_back_to_physics(self, weather_midday) -> None:
        # Scarda composite ids like SEC01-INV01-STR01 can't be queried by FK.
        repo = _FakeRepo(median_value=150.0)
        provider = HistoricalBaselineProvider(
            AlertEngineConfig(), reading_repo_factory=lambda: repo
        )
        b = provider.get_baseline("SEC01-INV01-STR01", weather_midday)
        assert b.expected_power == pytest.approx(209.1, rel=1e-3)
        assert repo.calls == []  # never queried


class TestHistoricalMedian:
    def test_rich_history_uses_median(self, weather_midday) -> None:
        repo = _FakeRepo(median_value=180.0)
        provider = HistoricalBaselineProvider(
            AlertEngineConfig(), reading_repo_factory=lambda: repo, min_samples=5
        )
        b = provider.get_baseline("1", weather_midday)
        assert b.expected_power == 180.0
        # current scaled proportionally: 180/209.1 * 8.364 ~ 7.20
        assert b.expected_current == pytest.approx(7.20, rel=1e-2)
        # voltage unchanged from physics model
        assert b.expected_voltage == pytest.approx(820.0)

    def test_query_uses_parsed_id_and_conditions(self, weather_midday) -> None:
        repo = _FakeRepo(median_value=150.0)
        provider = HistoricalBaselineProvider(
            AlertEngineConfig(), reading_repo_factory=lambda: repo, min_samples=5
        )
        provider.get_baseline("42", weather_midday)
        assert repo.calls == [(42, 850.0, 29.0)]


class TestNightHandling:
    def test_night_returns_physics_zero_baseline(self) -> None:
        repo = _FakeRepo(median_value=150.0)
        provider = HistoricalBaselineProvider(
            AlertEngineConfig(), reading_repo_factory=lambda: repo
        )
        b = provider.get_baseline("1", {"irradiance": 5.0, "ambient_temperature": 15.0})
        assert b.expected_power == 0.0  # physics night model
        assert repo.calls == []  # never queries at night
