"""
VTOL Phase 12 Flight Conditions & Operating Limits Engine.

Enforces pre-established site operating limits (Prompt Section 8) and validates
observed meteorological conditions before every flight sortie.
"""

from __future__ import annotations
from typing import Tuple, List

from .flight_test_models import (
    OperatingLimits,
    WeatherConditions,
    FlightReadinessStatus,
)


class FlightConditionsEngine:
    """
    Manages test-site operating boundaries and meteorological validations.
    """

    @classmethod
    def get_default_operating_limits(cls) -> OperatingLimits:
        """
        Returns authorized site operational boundaries established by flight-test safety office.
        """
        return OperatingLimits(
            max_permitted_wind_mps=7.0,
            max_permitted_gust_mps=9.0,
            min_visibility_km=5.0,
            min_field_area_m2=2500.0,
            max_test_altitude_m_agl=50.0,
            max_horizontal_distance_m=300.0,
            min_battery_reserve_pct=25.0,
            max_ambient_temp_c=38.0,
            min_ambient_temp_c=5.0,
        )

    @classmethod
    def evaluate_weather(
        cls,
        weather: WeatherConditions,
        limits: OperatingLimits,
    ) -> Tuple[FlightReadinessStatus, List[str]]:
        """
        Validates real-time weather against test site operating limits.
        """
        violations: List[str] = []

        if weather.wind_speed_mps > limits.max_permitted_wind_mps:
            violations.append(
                f"Wind speed ({weather.wind_speed_mps:.1f} m/s) exceeds maximum permitted limit ({limits.max_permitted_wind_mps:.1f} m/s)"
            )

        if weather.wind_gust_mps > limits.max_permitted_gust_mps:
            violations.append(
                f"Wind gusts ({weather.wind_gust_mps:.1f} m/s) exceed maximum permitted limit ({limits.max_permitted_gust_mps:.1f} m/s)"
            )

        if weather.visibility_km < limits.min_visibility_km:
            violations.append(
                f"Visibility ({weather.visibility_km:.1f} km) is below minimum safe limit ({limits.min_visibility_km:.1f} km)"
            )

        if weather.temperature_c > limits.max_ambient_temp_c:
            violations.append(
                f"Ambient temperature ({weather.temperature_c:.1f}C) exceeds maximum limit ({limits.max_ambient_temp_c:.1f}C)"
            )

        if weather.temperature_c < limits.min_ambient_temp_c:
            violations.append(
                f"Ambient temperature ({weather.temperature_c:.1f}C) is below minimum safe limit ({limits.min_ambient_temp_c:.1f}C)"
            )

        if violations:
            weather.within_limits = False
            return FlightReadinessStatus.FLIGHT_BLOCKED, violations

        weather.within_limits = True
        return FlightReadinessStatus.FLIGHT_READY, []
