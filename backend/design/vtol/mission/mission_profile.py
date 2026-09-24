"""
VTOL Mission Profile Subsystem

Purpose:
    Defines the `MissionProfile` class, storing calculated aerodynamic profiles
    and phase energy budgets.
"""

from dataclasses import dataclass, field
from typing import Any, Dict
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory, VTOLType


@dataclass(slots=True)
class MissionProfile:
    """
    Constructed engineering profile summarizing the mission constraints,
    air densities, and calculated segment energy estimates.

    Attributes:
        mission_category (VTOLMissionCategory): Sized category of the mission.
        vtol_type (VTOLType): Mechanical vehicle layout.
        payload_kg (float): Payload requirement in kg.
        total_endurance_min (float): Consolidated total duration in minutes.
        total_range_km (float): Consolidated flight range in kilometers.
        air_density_hover_kg_m3 (float): Standard air density at hover altitude.
        air_density_cruise_kg_m3 (float): Standard air density at cruise altitude.
        energy_demand_hover_kwh (float): Estimated electrical energy spent during hover.
        energy_demand_cruise_kwh (float): Estimated electrical energy spent during cruise.
        energy_demand_transition_kwh (float): Estimated electrical energy spent during transition.
        total_energy_demand_kwh (float): Total energy needed for complete flight.
        complexity_score (float): Normalized mission complexity rating (0.0 to 1.0).
        complexity_category (str): Qualitative complexity rating (Low, Medium, High).
        metadata (Dict[str, Any]): Additional operational properties.
    """

    mission_category: VTOLMissionCategory
    vtol_type: VTOLType
    payload_kg: float
    total_endurance_min: float
    total_range_km: float
    air_density_hover_kg_m3: float
    air_density_cruise_kg_m3: float
    energy_demand_hover_kwh: float
    energy_demand_cruise_kwh: float
    energy_demand_transition_kwh: float
    total_energy_demand_kwh: float
    complexity_score: float
    complexity_category: str
    metadata: Dict[str, Any] = field(default_factory=dict)
