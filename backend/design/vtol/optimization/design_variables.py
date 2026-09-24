"""
Torq Wings VTOL Phase 7 - Design Variables Model.

Purpose:
    Explicit typed optimization-variable definitions, bounds, sampling logic,
    and parameter provenance classifications for Phase 7.
"""

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional

from .optimization_models import OptimizationProvenance


@dataclass(slots=True)
class DesignVariable:
    """
    A single parameter adjusted during multidisciplinary optimization loops.
    """
    name: str
    base_value: float
    optimized_value: float = 0.0
    min_bound: float = 0.0
    max_bound: float = 0.0
    units: str = ""
    provenance: OptimizationProvenance = OptimizationProvenance.CONFIGURABLE_ASSUMPTION
    is_discrete: bool = False
    step_size: float = 0.0
    is_active: bool = True
    description: str = ""

    def __post_init__(self) -> None:
        if self.optimized_value == 0.0 and self.base_value != 0.0:
            self.optimized_value = self.base_value
        if self.min_bound > self.max_bound:
            raise ValueError(
                f"min_bound ({self.min_bound}) cannot exceed max_bound ({self.max_bound}) for variable '{self.name}'"
            )

    @property
    def value(self) -> float:
        return self.base_value

    def sample_values(self, num_points: int = 3) -> List[float]:
        """Generates deterministic sample values across the defined bounds."""
        if num_points <= 1 or abs(self.max_bound - self.min_bound) < 1e-9:
            return [round(self.base_value, 4)]

        if self.is_discrete and self.step_size > 0:
            vals = []
            curr = self.min_bound
            while curr <= self.max_bound + 1e-9:
                vals.append(round(curr, 4))
                curr += self.step_size
            return vals

        step = (self.max_bound - self.min_bound) / float(num_points - 1)
        return [round(self.min_bound + i * step, 4) for i in range(num_points)]

    def sample_discrete(self, steps: int = 3) -> List[float]:
        """Alias for sample_values to support discrete/grid enumeration."""
        return self.sample_values(num_points=steps)

    def validate_value(self, value: float) -> bool:
        """Verifies if a value satisfies the defined variable bounds."""
        return (self.min_bound - 1e-6) <= value <= (self.max_bound + 1e-6)

    def to_dict(self) -> Dict[str, Any]:
        prov_str = self.provenance.value if isinstance(self.provenance, OptimizationProvenance) else str(self.provenance)
        return {
            "name": self.name,
            "base_value": round(self.base_value, 4),
            "optimized_value": round(self.optimized_value, 4),
            "min_bound": round(self.min_bound, 4),
            "max_bound": round(self.max_bound, 4),
            "units": self.units,
            "provenance": prov_str,
            "is_discrete": self.is_discrete,
            "step_size": round(self.step_size, 4),
            "is_active": self.is_active,
            "description": self.description,
        }


# Alias for type-hint compatibility
OptimizationVariable = DesignVariable


def validate_variable_bounds(var: DesignVariable) -> None:
    """Validates that a variable has well-defined bounds."""
    if var.min_bound > var.max_bound:
        raise ValueError(
            f"Invalid bounds for variable '{var.name}': lower bound {var.min_bound} exceeds upper bound {var.max_bound}"
        )


@dataclass(slots=True)
class DesignVariables:
    """
    Set of design parameters governing a configuration optimization search space.
    """
    variables: List[DesignVariable]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_active_variables(self) -> List[DesignVariable]:
        """Returns only variables marked as actively varied."""
        return [v for v in self.variables if v.is_active]

    def get_variable(self, name: str) -> Optional[DesignVariable]:
        """Retrieves variable definition by name."""
        for v in self.variables:
            if v.name.lower() == name.lower():
                return v
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "variables": [v.to_dict() for v in self.variables],
            "metadata": self.metadata,
        }


# Authoritative catalog of standard variables evaluable via Phases 1–6
STANDARD_VTOL_VARIABLES: Dict[str, DesignVariable] = {
    "payload_mass_kg": DesignVariable(
        name="payload_mass_kg",
        base_value=2.5,
        min_bound=1.5,
        max_bound=4.0,
        units="kg",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
        is_active=True,
        description="Mission payload carrying capacity",
    ),
    "range_km": DesignVariable(
        name="range_km",
        base_value=35.0,
        min_bound=20.0,
        max_bound=60.0,
        units="km",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
        is_active=True,
        description="Target forward cruise mission range",
    ),
    "endurance_min": DesignVariable(
        name="endurance_min",
        base_value=25.0,
        min_bound=15.0,
        max_bound=45.0,
        units="min",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
        is_active=True,
        description="Target total mission flight endurance",
    ),
    "cruise_speed_kmh": DesignVariable(
        name="cruise_speed_kmh",
        base_value=85.0,
        min_bound=70.0,
        max_bound=110.0,
        units="km/h",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
        is_active=True,
        description="Forward aerodynamic cruise airspeed",
    ),
    "hover_duration_min": DesignVariable(
        name="hover_duration_min",
        base_value=5.0,
        min_bound=2.0,
        max_bound=10.0,
        units="min",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
        is_active=False,
        description="Total vertical hover mission segment duration",
    ),
    "transition_speed_kmh": DesignVariable(
        name="transition_speed_kmh",
        base_value=65.0,
        min_bound=55.0,
        max_bound=75.0,
        units="km/h",
        provenance=OptimizationProvenance.CONFIGURABLE_ASSUMPTION,
        is_active=False,
        description="Target wing-borne conversion speed during transition",
    ),
    "lift_motor_count": DesignVariable(
        name="lift_motor_count",
        base_value=4.0,
        min_bound=4.0,
        max_bound=8.0,
        units="",
        provenance=OptimizationProvenance.CONFIGURABLE_ASSUMPTION,
        is_discrete=True,
        step_size=2.0,
        is_active=False,
        description="Number of vertical lift propulsion units (QuadPlane=4, OctoPlane=8)",
    ),
    "v_tail_volume_h": DesignVariable(
        name="v_tail_volume_h",
        base_value=0.045,
        min_bound=0.035,
        max_bound=0.065,
        units="",
        provenance=OptimizationProvenance.CONFIGURABLE_ASSUMPTION,
        is_active=False,
        description="Horizontal equivalent tail volume coefficient",
    ),
    "v_tail_volume_v": DesignVariable(
        name="v_tail_volume_v",
        base_value=0.025,
        min_bound=0.018,
        max_bound=0.035,
        units="",
        provenance=OptimizationProvenance.CONFIGURABLE_ASSUMPTION,
        is_active=False,
        description="Vertical equivalent tail volume coefficient",
    ),
}
