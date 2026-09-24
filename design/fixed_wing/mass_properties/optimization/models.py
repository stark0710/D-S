"""
Fixed-Wing Mass Properties Optimization Specification Model
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Any


class CompatibleWeightBreakdown(dict):
    def __getattr__(self, name):
        # Allow accessing dict keys as properties
        if name in self:
            return self[name]
        # Map specific names expected by old tests to keys
        mapping = {
            "useful_load_kg": self.get("payload", 0.0) + self.get("battery", 0.0),
            "structural_weight_kg": self.get("wing", 0.0) + self.get("fuselage", 0.0) + self.get("horizontal_tail", 0.0) + self.get("vertical_tail", 0.0) + self.get("landing_gear", 0.0),
            "propulsion_weight_kg": self.get("motor", 0.0) + self.get("propeller", 0.0) + self.get("esc", 0.0),
            "avionics_weight_kg": self.get("flight_controller", 0.0) + self.get("gps", 0.0) + self.get("receiver", 0.0) + self.get("telemetry", 0.0) + self.get("power_module", 0.0) + self.get("bec", 0.0) + self.get("servos", 0.0),
            "battery_fuel_weight_kg": self.get("battery", 0.0),
            "payload_weight_kg": self.get("payload", 0.0),
        }
        if name in mapping:
            return mapping[name]
        raise AttributeError(f"'CompatibleWeightBreakdown' object has no attribute '{name}'")


@dataclass
class MassPropertiesSpecification:
    """
    Standardized specification containing the final aircraft weight build-up,
    fractions, subsystem breakdown, and 3D moments of inertia.
    """
    # Complete Weight Breakdown
    weight_breakdown: Any  # all mass items in kg

    # Sized weights
    empty_weight_kg: float
    operating_weight_kg: float
    maximum_takeoff_weight_kg: float

    # Ratios
    payload_fraction: float
    battery_fraction: float

    # Subsystem summary (in kg)
    subsystem_masses: Dict[str, float]

    # Inertia tensor diagonal (kg*m^2)
    moments_of_inertia: Tuple[float, float, float]  # (Ixx, Iyy, Izz)

    # Optimization tracking
    optimization_score: float
    reasoning: str

    # Extra fields for backwards compatibility with MassResult/old tests
    component_masses: List[Any] = field(default_factory=list)
    center_of_gravity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    static_margin: float = 0.15
    loading_conditions: List[Any] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.weight_breakdown, dict) and not isinstance(self.weight_breakdown, CompatibleWeightBreakdown):
            self.weight_breakdown = CompatibleWeightBreakdown(self.weight_breakdown)
