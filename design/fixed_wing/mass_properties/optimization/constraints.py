"""
Fixed-Wing Mass Properties Optimization Constraints
"""

from typing import Tuple, List, Any
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


def ensure_evaluated(candidate: OptimizationCandidate, context: OptimizationContext) -> None:
    """Helper to ensure evaluator runs before checks."""
    if "mtow_kg" not in candidate.derived_variables:
        from backend.design.fixed_wing.mass_properties.optimization.candidate_evaluator import MassCandidateEvaluator
        evaluator = MassCandidateEvaluator()
        evaluator.evaluate(candidate, context)


def check_mtow_limit(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    mtow = candidate.derived_variables["mtow_kg"]
    constraints = getattr(getattr(context.requirements, "mission_result", None), "constraints", None)
    mtow_limit = getattr(constraints, "maximum_takeoff_weight_kg", None) if constraints else None

    if mtow_limit is not None and mtow_limit > 0.0:
        if mtow > mtow_limit:
            return False, f"Takeoff weight ({mtow:.2f} kg) exceeds maximum MTOW limit ({mtow_limit:.2f} kg)."
    return True, ""


def check_payload_fraction(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    frac = candidate.derived_variables["payload_fraction"]
    if frac < 0.05 or frac > 0.60:
        return False, f"Payload fraction ({frac:.3f}) is outside realistic bounds [0.05, 0.60]."
    return True, ""


def check_battery_fraction(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    frac = candidate.derived_variables["battery_fraction"]
    if frac < 0.05 or frac > 0.55:
        return False, f"Battery fraction ({frac:.3f}) is outside realistic bounds [0.05, 0.55]."
    return True, ""


def check_structural_fraction(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    frac = candidate.derived_variables["structural_fraction"]
    if frac < 0.10 or frac > 0.65:
        return False, f"Structural fraction ({frac:.3f}) is outside realistic bounds [0.10, 0.65]."
    return True, ""


def check_non_negativity(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    breakdown = candidate.derived_variables["weight_breakdown"]
    for key, mass in breakdown.items():
        if mass < 0.0:
            return False, f"Component {key} has negative mass: {mass} kg."
    return True, ""


def check_subsystem_completeness(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    breakdown = candidate.derived_variables["weight_breakdown"]
    required_items = [
        "wing", "fuselage", "horizontal_tail", "vertical_tail", "landing_gear",
        "motor", "propeller", "esc", "battery", "flight_controller", "gps",
        "receiver", "telemetry", "power_module", "bec", "servos",
        "mission_equipment", "payload", "fasteners", "wiring", "paint_finish",
        "safety_margin"
    ]
    for item in required_items:
        if item not in breakdown:
            return False, f"Mandatory weight breakdown item '{item}' is missing."
    return True, ""


def check_mandatory_equipment(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    breakdown = candidate.derived_variables["weight_breakdown"]
    if breakdown.get("flight_controller", 0.0) <= 0.0:
        return False, "Flight controller weight must be positive."
    if breakdown.get("gps", 0.0) <= 0.0:
        return False, "GPS weight must be positive."
    if breakdown.get("battery", 0.0) <= 0.0:
        return False, "Battery weight must be positive."
    if breakdown.get("telemetry", 0.0) <= 0.0:
        return False, "Telemetry link weight must be positive."
    return True, ""


def build_mass_constraints() -> List[Any]:
    return [
        check_mtow_limit,
        check_payload_fraction,
        check_battery_fraction,
        check_structural_fraction,
        check_non_negativity,
        check_subsystem_completeness,
        check_mandatory_equipment,
    ]
