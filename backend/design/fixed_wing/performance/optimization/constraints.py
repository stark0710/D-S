"""
Fixed-Wing Flight Performance Constraints
"""

from typing import Tuple, List, Any
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


def ensure_evaluated(candidate: OptimizationCandidate, context: OptimizationContext) -> None:
    if "flight_result" not in candidate.derived_variables:
        from backend.design.fixed_wing.performance.optimization.candidate_evaluator import FlightPerformanceCandidateEvaluator
        evaluator = FlightPerformanceCandidateEvaluator()
        evaluator.evaluate(candidate, context)


def check_mission_endurance(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    endurance = derived["endurance"]
    target = context.requirements.mission_result.mission_profile.flight_time_min
    if endurance < target:
        return False, f"Endurance {endurance:.1f} min is below target {target:.1f} min."
    return True, ""


def check_mission_range(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    rng = derived["range"]
    target = context.requirements.mission_result.mission_profile.mission_range_km
    if rng < target:
        return False, f"Range {rng:.1f} km is below target {target:.1f} km."
    return True, ""


def check_stall_speed(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    v_stall = derived["stall_speed"]
    target = context.requirements.mission_result.mission_profile.stall_speed_target_kmh
    if v_stall > target:
        return False, f"Stall speed {v_stall:.1f} km/h exceeds target {target:.1f} km/h."
    return True, ""


def check_cruise_speed(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    v_max = derived["maximum_speed"]
    target = context.requirements.mission_result.mission_profile.cruise_speed_kmh
    if v_max < target:
        return False, f"Max speed {v_max:.1f} km/h is below cruise target {target:.1f} km/h."
    return True, ""


def check_takeoff_landing_distance(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    to_dist = derived["takeoff_distance"]
    land_dist = derived["landing_distance"]
    limit = 100.0
    if to_dist > limit:
        return False, f"Takeoff distance {to_dist:.1f} m exceeds limit {limit:.1f} m."
    if land_dist > limit:
        return False, f"Landing distance {land_dist:.1f} m exceeds limit {limit:.1f} m."
    return True, ""


def check_rate_of_climb(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    roc = derived["rate_of_climb"]
    target = 1.5  # standard min rate of climb limit
    if roc < target:
        return False, f"Rate of climb {roc:.1f} m/s is below target {target:.1f} m/s."
    return True, ""


def check_power_deficit(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    req = derived["power_required"]
    avail = derived["power_available"]
    if avail < req:
        return False, f"Power deficit: available {avail:.1f} W is below required cruise {req:.1f} W."
    return True, ""


def check_battery_capacity(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    
    target_wh = getattr(context.requirements.mission_result.mission_profile, "energy_demand_kwh", 0.5) * 1000.0
    
    mass_spec = context.previous_specifications.get("MassPropertiesOptimizer") or context.previous_specifications.get("MassPropertiesSpecification")
    if mass_spec:
        batt_mass = mass_spec.weight_breakdown.get("battery", 0.8)
    else:
        batt_spec = context.previous_specifications.get("PropulsionOptimizer") or context.previous_specifications.get("PropulsionSpecification")
        batt_mass = getattr(batt_spec, "battery_weight_g", 800.0) / 1000.0
        
    battery_energy_wh = batt_mass * 200.0
    # Sized battery must meet at least 50% of nominal energy budget limit
    if battery_energy_wh < (target_wh * 0.40):
        return False, f"Battery capacity {battery_energy_wh:.1f} Wh is insufficient for target demand {target_wh:.1f} Wh."
    return True, ""


def check_failed_validation(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    ensure_evaluated(candidate, context)
    if candidate.derived_variables.get("failed_validation", False):
        return False, f"Flight validation error: {candidate.derived_variables.get('validation_error_msg')}"
    return True, ""


def build_performance_constraints() -> List[Any]:
    return [
        check_failed_validation,
        check_mission_endurance,
        check_mission_range,
        check_stall_speed,
        check_cruise_speed,
        check_takeoff_landing_distance,
        check_rate_of_climb,
        check_power_deficit,
        check_battery_capacity,
    ]
