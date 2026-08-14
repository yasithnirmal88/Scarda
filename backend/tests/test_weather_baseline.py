"""Focused unit tests for the weather-aware physics baseline.

These exercise ``WeatherAwareBaselineProvider`` directly, independent of the
alert engine, to verify the irradiance / temperature model that underpins the
"no false alert under cloud cover" contract.
"""

from __future__ import annotations

import pytest

from app.services.alert_engine.baseline_provider import (
    StaticBaselineProvider,
    WeatherAwareBaselineProvider,
)
from app.services.alert_engine.config import AlertEngineConfig


@pytest.fixture
def provider() -> WeatherAwareBaselineProvider:
    return WeatherAwareBaselineProvider(AlertEngineConfig())


class TestWeatherScaling:
    def test_midday_baseline_matches_physics(self, provider: WeatherAwareBaselineProvider) -> None:
        # 850 W/m², 29 °C → irr_factor 0.85, temp_factor (1 - 0.004*4)=0.984
        b = provider.get_baseline("SEC01-INV01-STR01", {"irradiance": 850.0, "ambient_temperature": 29.0})
        assert b.expected_voltage == pytest.approx(820.0)
        assert b.expected_current == pytest.approx(8.364, rel=1e-3)
        assert b.expected_power == pytest.approx(209.1, rel=1e-3)

    def test_higher_irradiance_higher_power(self, provider: WeatherAwareBaselineProvider) -> None:
        low = provider.get_baseline("S1", {"irradiance": 400.0, "ambient_temperature": 25.0})
        high = provider.get_baseline("S1", {"irradiance": 900.0, "ambient_temperature": 25.0})
        assert high.expected_power > low.expected_power
        assert high.expected_current > low.expected_current

    def test_temperature_reduces_power(self, provider: WeatherAwareBaselineProvider) -> None:
        cool = provider.get_baseline("S1", {"irradiance": 850.0, "ambient_temperature": 20.0})
        hot = provider.get_baseline("S1", {"irradiance": 850.0, "ambient_temperature": 40.0})
        # Hotter cells produce less power (negative temperature coefficient).
        assert hot.expected_power < cool.expected_power

    def test_voltage_is_weather_insensitive(self, provider: WeatherAwareBaselineProvider) -> None:
        a = provider.get_baseline("S1", {"irradiance": 200.0, "ambient_temperature": 10.0})
        b = provider.get_baseline("S1", {"irradiance": 950.0, "ambient_temperature": 35.0})
        assert a.expected_voltage == b.expected_voltage

    def test_values_never_negative(self, provider: WeatherAwareBaselineProvider) -> None:
        b = provider.get_baseline("S1", {"irradiance": 5.0, "ambient_temperature": 50.0})
        assert b.expected_power >= 0.0
        assert b.expected_current >= 0.0


class TestNightHandling:
    def test_below_night_threshold_is_zero_output(self, provider: WeatherAwareBaselineProvider) -> None:
        b = provider.get_baseline("S1", {"irradiance": 5.0, "ambient_temperature": 15.0})
        assert b.expected_power == 0.0
        assert b.expected_current == 0.0

    def test_at_night_threshold_is_zero(self, provider: WeatherAwareBaselineProvider) -> None:
        cfg = AlertEngineConfig()
        b = provider.get_baseline("S1", {"irradiance": cfg.night_irradiance_wpm2, "ambient_temperature": 20.0})
        assert b.expected_power == 0.0


class TestFallback:
    def test_no_weather_falls_back_to_static(self, provider: WeatherAwareBaselineProvider) -> None:
        cfg = AlertEngineConfig()
        b = provider.get_baseline("S1", weather=None)
        assert b.expected_current == cfg.baseline_current
        assert b.expected_voltage == cfg.baseline_voltage
        assert b.expected_power == cfg.baseline_power

    def test_static_provider_ignores_weather(self) -> None:
        cfg = AlertEngineConfig()
        sp = StaticBaselineProvider(cfg)
        b = sp.get_baseline("S1", {"irradiance": 900.0, "ambient_temperature": 40.0})
        assert b.expected_power == cfg.baseline_power

    def test_missing_irradiance_treated_as_night(self, provider: WeatherAwareBaselineProvider) -> None:
        # irradiance None → coerced to 0 → below night threshold → 0 output.
        b = provider.get_baseline("S1", {"ambient_temperature": 25.0})
        assert b.expected_power == 0.0

    def test_missing_temperature_defaults_to_25c(self, provider: WeatherAwareBaselineProvider) -> None:
        # 850 W/m², temperature None → 25 °C → temp_factor = 1.0
        b = provider.get_baseline("S1", {"irradiance": 850.0})
        assert b.expected_power == pytest.approx(250.0 * 0.85, rel=1e-6)
