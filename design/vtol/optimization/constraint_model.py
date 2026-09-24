"""
VTOL Optimization Constraints Model.

Purpose:
    Typed constraint definitions, bound checking, violation magnitude calculation,
    and provenance tracking for Phase 7.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass(slots=True)
class ConstraintDefinition:
    """Explicit definition of an engineering constraint on candidate designs."""
    name: str
    min_bound: Optional[float] = None
    max_bound: Optional[float] = None
    units: str = ""
    provenance: str = "CONFIGURABLE_ASSUMPTION"
    is_hard: bool = True
    description: str = ""
    attribute_key: str = ""

    @property
    def lower_bound(self) -> Optional[float]:
        return self.min_bound

    @property
    def upper_bound(self) -> Optional[float]:
        return self.max_bound

    def evaluate(self, actual_value: float) -> "ConstraintResult":
        """Evaluates actual value against constraint bounds."""
        is_passed = True
        violation = 0.0

        if self.min_bound is not None and actual_value < (self.min_bound - 1e-6):
            is_passed = False
            violation = max(violation, self.min_bound - actual_value)

        if self.max_bound is not None and actual_value > (self.max_bound + 1e-6):
            is_passed = False
            violation = max(violation, actual_value - self.max_bound)

        notes = "PASSED" if is_passed else f"VIOLATION: magnitude={violation:.4f} {self.units}"
        return ConstraintResult(
            name=self.name,
            actual_value=round(actual_value, 4),
            min_bound=round(self.min_bound, 4) if self.min_bound is not None else None,
            max_bound=round(self.max_bound, 4) if self.max_bound is not None else None,
            is_passed=is_passed,
            violation_magnitude=round(violation, 4),
            units=self.units,
            provenance=self.provenance,
            notes=notes,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "min_bound": round(self.min_bound, 4) if self.min_bound is not None else None,
            "max_bound": round(self.max_bound, 4) if self.max_bound is not None else None,
            "units": self.units,
            "provenance": self.provenance,
            "is_hard": self.is_hard,
            "description": self.description,
            "attribute_key": self.attribute_key or self.name,
        }


@dataclass(slots=True)
class ConstraintResult:
    """Evaluation result for a single constraint."""
    name: str
    actual_value: float
    min_bound: Optional[float]
    max_bound: Optional[float]
    is_passed: bool
    violation_magnitude: float
    units: str
    provenance: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "actual_value": self.actual_value,
            "min_bound": self.min_bound,
            "max_bound": self.max_bound,
            "is_passed": self.is_passed,
            "violation_magnitude": self.violation_magnitude,
            "units": self.units,
            "provenance": self.provenance,
            "notes": self.notes,
        }


# Standard authoritative constraint definitions
STANDARD_CONSTRAINTS: Dict[str, ConstraintDefinition] = {
    "mtow_limit": ConstraintDefinition(
        name="mtow_limit",
        max_bound=10.0,
        units="kg",
        provenance="PROJECT_REQUIREMENT",
        description="Maximum takeoff weight limit",
        attribute_key="mtow_kg",
    ),
    "static_stability": ConstraintDefinition(
        name="static_stability",
        min_bound=0.001,
        units="fraction MAC",
        provenance="DERIVED",
        description="Requirement for positive longitudinal static pitch margin (SM > 0)",
        attribute_key="static_margin_fraction",
    ),
    "static_margin_bounds": ConstraintDefinition(
        name="static_margin_bounds",
        min_bound=0.05,
        max_bound=0.15,
        units="fraction MAC",
        provenance="CONFIGURABLE_ASSUMPTION",
        description="Configurable static margin bounds (+5% to +15% MAC guideline)",
        attribute_key="static_margin_fraction",
    ),
    "hover_thrust_ratio": ConstraintDefinition(
        name="hover_thrust_ratio",
        min_bound=1.30,
        units="ratio",
        provenance="CONFIGURABLE_ASSUMPTION",
        description="Minimum vertical hover thrust-to-weight ratio",
        attribute_key="hover_thrust_to_weight",
    ),
    "stall_speed_margin": ConstraintDefinition(
        name="stall_speed_margin",
        max_bound=18.06,  # 65 km/h
        units="m/s",
        provenance="DERIVED",
        description="Wing stall speed must remain below transition forward speed",
        attribute_key="stall_speed_m_s",
    ),
    "cg_aft_limit_clearance": ConstraintDefinition(
        name="cg_aft_limit_clearance",
        min_bound=0.000,
        units="m",
        provenance="ASSUMPTION_BASED / DERIVED",
        description="CG must remain forward of aft stability limit",
        attribute_key="aft_margin_m",
    ),
    "cg_forward_limit_clearance": ConstraintDefinition(
        name="cg_forward_limit_clearance",
        min_bound=0.000,
        units="m",
        provenance="DERIVED",
        description="CG must remain aft of forward elevator trim authority limit",
        attribute_key="forward_margin_m",
    ),
    "battery_energy_margin": ConstraintDefinition(
        name="battery_energy_margin",
        min_bound=1.20,
        units="ratio",
        provenance="CONFIGURABLE_ASSUMPTION",
        description="Installed battery capacity must provide at least 20% reserve SoC",
        attribute_key="battery_reserve_ratio",
    ),
    "trim_feasibility": ConstraintDefinition(
        name="trim_feasibility",
        min_bound=1.0,
        units="flag (1=FEASIBLE)",
        provenance="DERIVED",
        description="Quasi-steady pitch trim equilibrium within ruddervator deflection limits",
        attribute_key="trim_is_feasible",
    ),
}
