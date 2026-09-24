"""
Fixed-Wing Center of Gravity (CG) Optimization Constraints
"""

from typing import Tuple, List, Any
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


def ensure_evaluated(candidate: OptimizationCandidate, context: OptimizationContext) -> None:
    """Helper to ensure evaluator runs before checks."""
    if "cg_position" not in candidate.derived_variables:
        from backend.design.fixed_wing.cg.optimization.candidate_evaluator import CGCandidateEvaluator
        evaluator = CGCandidateEvaluator()
        evaluator.evaluate(candidate, context)


def check_fuselage_boundaries(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    f_geom = context.requirements.fuselage_result.fuselage_geometry
    total_len = getattr(f_geom, "length_m", 1.4)
    nose_len = getattr(f_geom, "nose_length_m", 0.25)
    tail_cone_len = getattr(f_geom, "tail_cone_length_m", 0.70)

    # Scale parameters consistently with evaluator
    nose_len = min(nose_len, total_len * 0.25)
    tail_cone_len = min(tail_cone_len, total_len * 0.50)
    cabin_len = total_len - nose_len - tail_cone_len

    pos = candidate.derived_variables["component_positions"]
    battery_x = pos["battery"][0]
    payload_x = pos["payload"][0]
    avionics_x = pos["avionics_tray"][0]

    # Battery limits (battery physical length scales with cabin size)
    batt_half_len = max(0.02, min(0.06, cabin_len * 0.10))
    if (battery_x - batt_half_len) < nose_len or (battery_x + batt_half_len) > (total_len - tail_cone_len):
        return False, f"Battery at {battery_x:.3f}m exits the fuselage battery bay limits."

    # Payload limits (cabin limits)
    if payload_x < nose_len or payload_x > (nose_len + cabin_len):
        return False, f"Payload at {payload_x:.3f}m is inaccessible / exits cabin bounds."

    # Avionics limits (cabin limits)
    if avionics_x < nose_len or avionics_x > (nose_len + cabin_len):
        return False, f"Avionics tray at {avionics_x:.3f}m exits cabin bounds."

    return True, ""


def check_component_overlap(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    f_geom = context.requirements.fuselage_result.fuselage_geometry
    total_len = getattr(f_geom, "length_m", 1.4)
    nose_len = getattr(f_geom, "nose_length_m", 0.25)
    tail_cone_len = getattr(f_geom, "tail_cone_length_m", 0.70)

    nose_len = min(nose_len, total_len * 0.25)
    tail_cone_len = min(tail_cone_len, total_len * 0.50)
    cabin_len = total_len - nose_len - tail_cone_len

    pos = candidate.derived_variables["component_positions"]
    battery_x = pos["battery"][0]
    payload_x = pos["payload"][0]
    avionics_x = pos["avionics_tray"][0]

    # Clearance target to prevent physical collision inside fuselage (scales down for compact platforms)
    clearance = max(0.025, min(0.05, cabin_len * 0.08))
    if abs(battery_x - payload_x) < clearance:
        return False, f"Overlap detected between Battery ({battery_x:.3f}m) and Payload ({payload_x:.3f}m)."
    if abs(battery_x - avionics_x) < clearance:
        return False, f"Overlap detected between Battery ({battery_x:.3f}m) and Avionics ({avionics_x:.3f}m)."
    if abs(payload_x - avionics_x) < clearance:
        return False, f"Overlap detected between Payload ({payload_x:.3f}m) and Avionics ({avionics_x:.3f}m)."

    return True, ""


def check_static_margin(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    sm = candidate.derived_variables["static_margin"]
    
    # Normal target range: [10%, 20%] of MAC
    min_sm = 0.10
    max_sm = 0.20
    
    if sm < min_sm:
        return False, f"Static margin ({sm*100.0:.1f}%) is below stability limits (Aft CG limit exceeded)."
    if sm > max_sm:
        return False, f"Static margin ({sm*100.0:.1f}%) is above stability limits (Forward CG limit exceeded)."

    return True, ""


def build_cg_constraints() -> List[Any]:
    return [
        check_fuselage_boundaries,
        check_component_overlap,
        check_static_margin,
    ]
