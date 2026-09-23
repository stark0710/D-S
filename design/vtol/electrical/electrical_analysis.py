"""
VTOL Electrical Sizing Analysis Subsystem

Purpose:
    Defines the consolidated `ElectricalAnalysis` class.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ElectricalAnalysis:
    """
    Volumetric and loading efficiency scores of the sized electrical system.

    Attributes:
        mission_energy_wh (float): Sized total mission energy demand.
        hover_energy_wh (float): Sized hover segment energy consumption.
        transition_energy_wh (float): Sized transition segment energy.
        cruise_energy_wh (float): Sized cruise segment energy.
        reserve_energy_wh (float): reserve energy buffer.
        battery_utilization_percent (float): Sized depth of discharge usage percentage.
        voltage_sag_v (float): Voltage sag under hover current.
        current_margins_percent (float): margin between max battery rating and max current.
        thermal_loading_index (float): heat index.
        charging_time_hr (float): charging time duration.
        lifecycle_rating (float): lifespan metric.
        metadata (Dict[str, Any]): Sizing details.
    """

    mission_energy_wh: float
    hover_energy_wh: float
    transition_energy_wh: float
    cruise_energy_wh: float
    reserve_energy_wh: float
    battery_utilization_percent: float
    voltage_sag_v: float
    current_margins_percent: float
    thermal_loading_index: float
    charging_time_hr: float
    lifecycle_rating: float
    metadata: Dict[str, Any] = field(default_factory=dict)
