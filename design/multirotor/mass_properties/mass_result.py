from dataclasses import dataclass
from typing import Dict, Any

@dataclass(slots=True)
class MassPropertiesSpecification:
    """
    Sized and verified multirotor Mass Properties, Center of Gravity, and Moments of Inertia specification.
    """
    total_mass_kg: float
    empty_mass_kg: float
    payload_mass_kg: float
    battery_mass_kg: float
    weight_breakdown: Dict[str, float]
    component_fractions: Dict[str, float]
    center_of_gravity: tuple[float, float, float]
    moments_of_inertia: Dict[str, float]
    symmetry_report: Dict[str, Any]
    optimization_score: float
    engineering_reasoning: str
    principal_axes: Dict[str, tuple[float, float, float]]

    @property
    def empty_weight_kg(self) -> float:
        return self.empty_mass_kg

    @property
    def maximum_takeoff_weight_kg(self) -> float:
        return self.total_mass_kg

    @property
    def mtow_kg(self) -> float:
        return self.total_mass_kg

    @property
    def structural_margin(self) -> float:
        return 1.5

    @property
    def subsystem_masses(self) -> Dict[str, float]:
        return {
            "structure": self.weight_breakdown.get("Frame Structure Weight (kg)", 0.0),
            "propulsion": self.weight_breakdown.get("Propulsion Weight (kg)", 0.0),
            "electrical": self.weight_breakdown.get("Electrical Wire/PDB Weight (kg)", 0.0),
            "avionics": self.weight_breakdown.get("Avionics Weight (kg)", 0.0),
            "payload": self.payload_mass_kg,
            "battery": self.battery_mass_kg
        }

