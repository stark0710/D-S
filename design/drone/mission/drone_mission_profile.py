"""
DroneMissionProfile Subsystem

Purpose:
    Defines the `DroneMissionProfile` domain model representing a multirotor-specific mission profile.

Role in Architecture:
    `DroneMissionProfile` encapsulates multirotor-specific mission parameters (hover time, cruise time, target range,
    payload weight, wind tolerance, operating altitude, redundancy level).
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.requirements.mission_type import MissionType


@dataclass(slots=True)
class DroneMissionProfile:
    """
    Multirotor-specific mission profile definition.

    Attributes:
        mission_type (MissionType): Mission category type.
        payload_weight_kg (float): Required payload mass in kg.
        target_hover_time_min (float): Required hover flight time in minutes.
        target_cruise_time_min (float): Required forward cruise time in minutes.
        target_range_km (float): Required mission flight distance in km.
        cruise_speed_kmh (float): Target cruise speed in km/h.
        max_wind_speed_m_s (float): Max expected operating wind speed in m/s.
        operating_altitude_m (float): Target operating altitude in meters MSL.
        required_redundancy (str): Required motor redundancy ('NONE', 'HEXA_SINGLE_FAIL', 'OCTO_DUAL_FAIL').
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    mission_type: MissionType
    payload_weight_kg: float
    target_hover_time_min: float
    target_cruise_time_min: float
    target_range_km: float
    cruise_speed_kmh: float
    max_wind_speed_m_s: float = 10.0
    operating_altitude_m: float = 100.0
    required_redundancy: str = "HEXA_SINGLE_FAIL"
    metadata: dict[str, Any] = field(default_factory=dict)
