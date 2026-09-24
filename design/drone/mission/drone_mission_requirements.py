"""
DroneMissionRequirements Subsystem

Purpose:
    Defines the `DroneMissionRequirements` domain model representing multirotor engineering requirements derived from a mission profile.

Role in Architecture:
    `DroneMissionRequirements` encapsulates derived multirotor requirements (estimated AUW target, flight time target,
    range target, hover power margin, wind tolerance, redundancy level, environmental constraints, safety margins).
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DroneMissionRequirements:
    """
    Derived multirotor engineering requirements model.

    Attributes:
        required_payload_kg (float): Required payload mass in kg.
        estimated_auw_target_kg (float): Estimated All-Up Weight (AUW) target in kg.
        flight_time_target_min (float): Combined flight time target in minutes.
        range_target_km (float): Required operational range in km.
        hover_power_margin_min (float): Minimum hover thrust-to-weight ratio margin (e.g. 1.8 - 2.0).
        cruise_speed_target_kmh (float): Target cruise velocity in km/h.
        max_wind_tolerance_m_s (float): Required wind resistance capability in m/s.
        redundancy_level (str): Motor failure redundancy requirement string.
        environmental_constraints (dict[str, Any]): Thermal, dust, IP rating constraints.
        safety_margin_percent (float): Energy reserve safety margin percentage (default 20%).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    required_payload_kg: float
    estimated_auw_target_kg: float
    flight_time_target_min: float
    range_target_km: float
    hover_power_margin_min: float = 1.8
    cruise_speed_target_kmh: float = 50.0
    max_wind_tolerance_m_s: float = 10.0
    redundancy_level: str = "HEXA_SINGLE_FAIL"
    environmental_constraints: dict[str, Any] = field(default_factory=dict)
    safety_margin_percent: float = 20.0
    metadata: dict[str, Any] = field(default_factory=dict)
