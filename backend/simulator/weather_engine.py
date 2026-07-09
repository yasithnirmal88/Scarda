from __future__ import annotations

import math
import random
from datetime import datetime

from simulator.models import WeatherState, WeatherType


class WeatherEngine:
    """Simulates weather conditions that affect irradiance and temperature.

    Weather types have distinct irradiance multipliers:
        SUNNY:  0.9 - 1.0
        CLOUDY: 0.5 - 0.8
        RAINY:  0.1 - 0.4
        STORM:  0.0 - 0.15

    Weather changes smoothly 1-2 times per day. Within each weather
    block, irradiance has gentle stochastic variation.
    """

    WEATHER_PROFILES: dict[WeatherType, dict] = {
        WeatherType.SUNNY: {
            "irr_range": (0.9, 1.0),
            "temp_offset": 0,
            "humidity_range": (40, 60),
            "wind_range": (0, 10),
            "desc": "Clear skies",
        },
        WeatherType.CLOUDY: {
            "irr_range": (0.5, 0.8),
            "temp_offset": -5,
            "humidity_range": (60, 80),
            "wind_range": (5, 20),
            "desc": "Overcast with clouds",
        },
        WeatherType.RAINY: {
            "irr_range": (0.1, 0.4),
            "temp_offset": -8,
            "humidity_range": (80, 100),
            "wind_range": (10, 25),
            "desc": "Rain showers",
        },
        WeatherType.STORM: {
            "irr_range": (0.0, 0.15),
            "temp_offset": -12,
            "humidity_range": (85, 100),
            "wind_range": (30, 60),
            "desc": "Thunderstorm",
        },
    }

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._state = WeatherState()
        self._transitions: list[tuple[int, WeatherType]] = []
        self._resolved = False

    def _resolve_day(self, day_start: datetime) -> None:
        """Generate the weather pattern for a given day."""
        self._transitions = []
        num_changes = self._rng.randint(1, 2)
        hours = sorted(self._rng.sample(range(3, 21), num_changes))
        types = [WeatherType.SUNNY, WeatherType.CLOUDY, WeatherType.RAINY]
        # bias heavily toward sunny
        weights = [0.55, 0.30, 0.10, 0.05]

        for h in hours:
            wt = self._rng.choices(
                [WeatherType.SUNNY, WeatherType.CLOUDY, WeatherType.RAINY, WeatherType.STORM],
                weights=weights,
                k=1,
            )[0]
            self._transitions.append((h, wt))

        self._resolved = True

    def get_weather(self, dt: datetime) -> WeatherState:
        """Return the weather state at a given datetime."""
        day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)

        if not self._resolved or (dt - day_start).days > 0:
            self._resolve_day(day_start)

        hour = dt.hour + dt.minute / 60.0
        active_type: WeatherType = WeatherType.SUNNY
        for h, wt in self._transitions:
            if hour >= h:
                active_type = wt

        profile = self.WEATHER_PROFILES[active_type]
        irr_min, irr_max = profile["irr_range"]
        mult = self._rng.uniform(irr_min, irr_max)
        hum = self._rng.uniform(*profile["humidity_range"])
        wind = self._rng.uniform(*profile["wind_range"])

        self._state = WeatherState(
            weather_type=active_type,
            irradiance_multiplier=round(mult, 4),
            description=profile["desc"],
            temperature_base=30.0 + profile["temp_offset"],
            humidity_base=round(hum, 1),
            wind_speed_base=round(wind, 1),
        )
        return self._state

    def base_irradiance(self, dt: datetime) -> float:
        """Compute the clear-sky irradiance (W/m²) based on solar position.

        Uses a sine-squared model:
            irradiance = 1000 * sin²(π * (t - sunrise) / (day_length))
        Zero before sunrise and after sunset.
        """
        sunrise = 6.0
        sunset = 18.0
        day_length = sunset - sunrise
        hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0

        if hour < sunrise or hour > sunset:
            return 0.0

        fraction = (hour - sunrise) / day_length
        return 1000.0 * (math.sin(math.pi * fraction) ** 2)

    def effective_irradiance(self, dt: datetime) -> float:
        """Return weather-adjusted irradiance at a given time."""
        base = self.base_irradiance(dt)
        weather = self.get_weather(dt)
        return base * weather.irradiance_multiplier
