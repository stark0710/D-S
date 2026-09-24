"""
Fixed-Wing Propulsion Constraints Evaluator

Enforces physical, mechanical, and electrical constraints on the propulsion system.
"""

from typing import List, Tuple, Dict, Any, Callable
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

ConstraintFunc = Callable[[OptimizationCandidate, OptimizationContext], Tuple[bool, str]]


def ensure_evaluated(candidate: OptimizationCandidate, context: OptimizationContext) -> None:
    """Ensures the candidate has been evaluated by the engine before checking constraints."""
    if candidate.status == "PENDING":
        from backend.design.fixed_wing.propulsion.optimization.candidate_evaluator import CandidateEvaluator
        evaluator = CandidateEvaluator()
        evaluator.evaluate(candidate, context)


def check_motor_current_vs_esc(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures that the motor current draw does not exceed ESC continuous current rating."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    dv = candidate.design_variables
    derived = candidate.derived_variables
    esc = dv["esc"]
    climb_current = derived.get("per_motor_climb_current_a", derived.get("climb_current_a", 0.0))

    if climb_current > esc["continuous_current_a"]:
        return False, f"Climb current ({climb_current:.1f} A) exceeds ESC continuous rating ({esc['continuous_current_a']:.1f} A)."
    return True, ""


def check_esc_vs_battery(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures the battery can support the maximum ESC continuous current rating."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    dv = candidate.design_variables
    esc = dv["esc"]
    battery = dv["battery"]

    if esc["continuous_current_a"] > battery["max_discharge_current_a"]:
        return False, f"ESC continuous rating ({esc['continuous_current_a']:.1f} A) exceeds battery max discharge rate ({battery['max_discharge_current_a']:.1f} A)."
    return True, ""


def check_battery_voltage_vs_motor(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures battery voltage is within the motor's operating limit (cell counts match)."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    dv = candidate.design_variables
    motor = dv["motor"]
    battery = dv["battery"]

    if battery["cell_count_s"] != motor["cell_count_s"]:
        return False, f"Battery cell count ({battery['cell_count_s']}S) is incompatible with motor designed cell count ({motor['cell_count_s']}S)."
    return True, ""


def check_propeller_diameter(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures propeller diameter is within maximum limits from fuselage envelope."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    dv = candidate.design_variables
    propeller = dv["propeller"]

    fuse_spec = context.previous_specifications.get("FuselageOptimizer")
    height_m = getattr(fuse_spec, "height", 0.20)
    max_prop_diameter_m = max(0.28, height_m * 2.0)

    if propeller["diameter_m"] > max_prop_diameter_m:
        return False, f"Propeller diameter ({propeller['diameter_m']:.3f} m) exceeds maximum allowable limit ({max_prop_diameter_m:.3f} m)."
    return True, ""


def check_ground_clearance(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures ground clearance is maintained based on the landing gear and propeller radius."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    dv = candidate.design_variables
    propeller = dv["propeller"]
    prop_radius = propeller["diameter_m"] / 2.0

    # Retrieve ground clearance limit (typically from landing gear / fuselage height clearance)
    fuse_spec = context.previous_specifications.get("FuselageOptimizer")
    height_m = getattr(fuse_spec, "height", 0.20)
    clearance_limit = max(0.14, height_m)  # Ground clearance limit is at least height of fuselage

    if prop_radius > clearance_limit:
        return False, f"Propeller radius ({prop_radius:.3f} m) exceeds landing gear ground clearance limit ({clearance_limit:.3f} m)."
    return True, ""


def check_static_thrust(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures static thrust of the system meets or exceeds takeoff thrust requirements."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    derived = candidate.derived_variables
    static_thrust = derived.get("static_thrust_n", 0.0)
    req_takeoff_thrust = derived.get("takeoff_thrust_n", 0.0)

    if static_thrust < req_takeoff_thrust:
        return False, f"Static thrust ({static_thrust:.1f} N) is below required takeoff thrust ({req_takeoff_thrust:.1f} N)."
    return True, ""


def check_cruise_thrust(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures that the propeller can generate positive cruise thrust matching or exceeding cruise drag."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    derived = candidate.derived_variables
    static_thrust = derived.get("static_thrust_n", 0.0)
    cruise_drag = derived.get("cruise_thrust_n", 0.0)

    # Cruise thrust should be less than static thrust capability
    if static_thrust < cruise_drag:
        return False, f"Propeller static thrust capability ({static_thrust:.1f} N) is below cruise drag ({cruise_drag:.1f} N)."
    return True, ""


def check_climb_power(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures the motor is capable of providing sized climb power."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    dv = candidate.design_variables
    derived = candidate.derived_variables
    motor = dv["motor"]
    climb_power = derived.get("per_motor_climb_power_w", derived.get("climb_power_w", 0.0))

    if motor["max_power_w"] < climb_power:
        return False, f"Motor max power ({motor['max_power_w']:.1f} W) is below required climb power ({climb_power:.1f} W)."
    return True, ""


def check_motor_thermal_limit(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures motor maximum current does not cause overheating (does not exceed max_current_a)."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    dv = candidate.design_variables
    derived = candidate.derived_variables
    motor = dv["motor"]
    climb_current = derived.get("per_motor_climb_current_a", derived.get("climb_current_a", 0.0))

    if climb_current > motor["max_current_a"]:
        return False, f"Motor climb current ({climb_current:.1f} A) exceeds motor maximum current limit ({motor['max_current_a']:.1f} A)."
    return True, ""


def check_battery_discharge_rate(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures current draw doesn't exceed battery maximum continuous discharge capability."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    dv = candidate.design_variables
    derived = candidate.derived_variables
    battery = dv["battery"]
    climb_current = derived.get("climb_current_a", 0.0)

    if climb_current > battery["max_discharge_current_a"]:
        return False, f"Climb current ({climb_current:.1f} A) exceeds battery continuous rating ({battery['max_discharge_current_a']:.1f} A)."
    return True, ""


def check_mission_energy_sufficiency(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """Ensures candidate battery can satisfy target flight time and range requirements."""
    ensure_evaluated(candidate, context)
    if candidate.status == "FAILED":
        return False, "Propulsion calculation backend failed"

    derived = candidate.derived_variables
    flight_time = derived.get("estimated_flight_time_min", 0.0)

    # Retrieve mission requirements
    m_prof = getattr(getattr(context.requirements, "mission_result", None), "mission_profile", None)
    t_target = 0.0
    r_target = 0.0
    v_cruise = 70.0
    if m_prof:
        t_target = getattr(m_prof, "flight_time_min", 0.0)
        r_target = getattr(m_prof, "mission_range_km", 0.0)
        v_cruise = getattr(m_prof, "cruise_speed_kmh", 70.0)
    elif hasattr(context.requirements, "target_flight_time_min"):
        t_target = getattr(context.requirements, "target_flight_time_min", 0.0)
        r_target = getattr(context.requirements, "target_range_km", 0.0)
        v_cruise = getattr(context.requirements, "cruise_speed_kmh", 70.0)

    controlling_target_min = t_target
    if v_cruise > 0 and r_target > 0:
        t_range = (r_target / v_cruise) * 60.0
        controlling_target_min = max(controlling_target_min, t_range)

    if controlling_target_min > 0.0 and flight_time < controlling_target_min:
        all_cands = getattr(context, "_active_propulsion_candidates", None)
        catalog_has_feasible = False
        if all_cands:
            for c in all_cands:
                ensure_evaluated(c, context)
                if c.derived_variables.get("estimated_flight_time_min", 0.0) >= controlling_target_min:
                    catalog_has_feasible = True
                    break

        if catalog_has_feasible or all_cands is None:
            return False, (
                f"Estimated flight time ({flight_time:.1f} min) is below controlling mission requirement "
                f"({controlling_target_min:.1f} min; target endurance={t_target:.1f} min, target range={r_target:.1f} km)."
            )

        # Catalog limitation for extreme mission: flag warning so mass properties physically sizes battery
        candidate.derived_variables["catalog_capacity_warning"] = (
            f"Discrete catalog maximum flight time ({flight_time:.1f} min) is below mission target "
            f"({controlling_target_min:.1f} min). Physical battery requirement will be sized by mass properties."
        )

    return True, ""



def build_propulsion_constraints() -> List[ConstraintFunc]:
    """Compiles and returns the list of active propulsion constraints."""
    return [
        check_motor_current_vs_esc,
        check_esc_vs_battery,
        check_battery_voltage_vs_motor,
        check_propeller_diameter,
        check_ground_clearance,
        check_static_thrust,
        check_cruise_thrust,
        check_climb_power,
        check_motor_thermal_limit,
        check_battery_discharge_rate,
        check_mission_energy_sufficiency,
    ]

