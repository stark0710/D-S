"""
VTOL Optimization Objectives Model.

Purpose:
    Typed objective definitions, optimization directions (MINIMIZE / MAXIMIZE),
    units, extraction mappings, and provenance tracking for Phase 7.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ObjectiveDirection(str, Enum):
    """Optimization search direction."""
    MINIMIZE = "MINIMIZE"
    MAXIMIZE = "MAXIMIZE"


@dataclass(slots=True)
class ObjectiveDefinition:
    """Explicit definition of a single multidisciplinary optimization objective."""
    name: str
    direction: ObjectiveDirection
    units: str
    source: str
    provenance: str = "DERIVED"
    description: str = ""
    attribute_key: str = ""

    def extract_value(self, evaluation_data: Dict[str, Any]) -> float:
        """Extracts numerical objective value from evaluated candidate dictionary."""
        key = self.attribute_key or self.name
        if key in evaluation_data:
            return float(evaluation_data[key])
        
        # Search nested dicts if needed
        for sub in ["sizing", "energy_and_power", "performance", "stability_and_control", "variables"]:
            if sub in evaluation_data and isinstance(evaluation_data[sub], dict):
                if key in evaluation_data[sub]:
                    return float(evaluation_data[sub][key])
        
        raise KeyError(f"Objective '{self.name}' (key='{key}') not found in evaluation outputs")

    def to_minimization_score(self, value: float) -> float:
        """
        Converts the objective value into a standardized minimization score
        where lower is strictly better for all Pareto dominance comparisons.
        """
        if self.direction == ObjectiveDirection.MINIMIZE:
            return float(value)
        else:
            return -float(value)

    def standardized_score(self, value: float) -> float:
        """Alias for to_minimization_score."""
        return self.to_minimization_score(value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "direction": self.direction.value,
            "units": self.units,
            "source": self.source,
            "provenance": self.provenance,
            "description": self.description,
            "attribute_key": self.attribute_key or self.name,
        }


# Standard authoritative objective definitions supported by Phases 1-6
STANDARD_OBJECTIVES: Dict[str, ObjectiveDefinition] = {
    "mtow_kg": ObjectiveDefinition(
        name="mtow_kg",
        direction=ObjectiveDirection.MINIMIZE,
        units="kg",
        source="PHASE_5_MASS_PROPERTIES",
        provenance="DERIVED",
        description="Total Takeoff Mass synthesized from 23-component ledger",
        attribute_key="mtow_kg",
    ),
    "battery_mass_kg": ObjectiveDefinition(
        name="battery_mass_kg",
        direction=ObjectiveDirection.MINIMIZE,
        units="kg",
        source="PHASE_4_ELECTRICAL",
        provenance="DERIVED",
        description="Mass of sized lithium battery pack",
        attribute_key="battery_mass_kg",
    ),
    "total_mission_energy_wh": ObjectiveDefinition(
        name="total_mission_energy_wh",
        direction=ObjectiveDirection.MINIMIZE,
        units="Wh",
        source="PHASE_4_ENERGY",
        provenance="DERIVED",
        description="Total electrical mission energy across hover, transition, and cruise",
        attribute_key="total_mission_energy_wh",
    ),
    "hover_power_w": ObjectiveDefinition(
        name="hover_power_w",
        direction=ObjectiveDirection.MINIMIZE,
        units="W",
        source="PHASE_2_HOVER",
        provenance="DERIVED",
        description="Total hover power draw for vertical flight",
        attribute_key="hover_power_w",
    ),
    "cruise_power_w": ObjectiveDefinition(
        name="cruise_power_w",
        direction=ObjectiveDirection.MINIMIZE,
        units="W",
        source="PHASE_3_CRUISE",
        provenance="DERIVED",
        description="Cruise pusher motor mechanical power demand",
        attribute_key="cruise_power_w",
    ),
    "endurance_min": ObjectiveDefinition(
        name="endurance_min",
        direction=ObjectiveDirection.MAXIMIZE,
        units="min",
        source="MISSION_PERFORMANCE",
        provenance="DERIVED",
        description="Estimated operational flight endurance",
        attribute_key="endurance_min",
    ),
    "range_km": ObjectiveDefinition(
        name="range_km",
        direction=ObjectiveDirection.MAXIMIZE,
        units="km",
        source="MISSION_PERFORMANCE",
        provenance="DERIVED",
        description="Estimated total cruise flight range",
        attribute_key="range_km",
    ),
    "payload_mass_kg": ObjectiveDefinition(
        name="payload_mass_kg",
        direction=ObjectiveDirection.MAXIMIZE,
        units="kg",
        source="PAYLOAD_ENGINE",
        provenance="PROJECT_REQUIREMENT",
        description="Payload capacity carried by the vehicle",
        attribute_key="payload_mass_kg",
    ),
}
