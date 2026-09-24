"""
Electrical System Optimization Constraints

Defines the 10 electrical, RF, mechanical, and safety constraints.
"""

from typing import Tuple, List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.components.component_category import ComponentCategory


class ConstraintCheckException(Exception):
    """Exception raised inside constraint checkers due to evaluation failures."""
    pass


def ensure_evaluated(candidate: OptimizationCandidate, context: OptimizationContext) -> None:
    """Helper to ensure the candidate is evaluated before constraint checks."""
    if "total_continuous_current_a" not in candidate.derived_variables:
        from backend.design.fixed_wing.electrical.candidate_evaluator import CandidateEvaluator
        evaluator = CandidateEvaluator()
        try:
            evaluator.evaluate(candidate, context)
        except Exception as e:
            candidate.status = "FAILED"
            candidate.derived_variables["evaluation_error"] = str(e)
            raise ConstraintCheckException(str(e)) from e


def check_voltage_compatibility(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """1. Voltage incompatible check: PM max voltage support vs battery cells count."""
    try:
        ensure_evaluated(candidate, context)
    except ConstraintCheckException as e:
        return False, f"Electrical calculation backend failed: {e}"

    dv = candidate.design_variables
    pm = dv["power_module"]
    
    # propulsion battery cell count S
    prop_spec = context.previous_specifications.get("PropulsionOptimizer")
    prop_cells = getattr(prop_spec, "battery_cell_count", 6)
    if not prop_spec:
        # Check from evaluation or context
        prop_cells = 6

    if pm["max_voltage_cells_s"] < prop_cells:
        return False, f"Power module max voltage cell count ({pm['max_voltage_cells_s']}S) is below battery count ({prop_cells}S)."
    return True, ""


def check_current_limits(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """2. Current exceeded check: continuous current vs PM continuous limit."""
    ensure_evaluated(candidate, context)
    dv = candidate.design_variables
    derived = candidate.derived_variables
    pm = dv["power_module"]
    total_cont = derived["total_continuous_current_a"]

    if total_cont > pm["max_continuous_current_a"]:
        return False, f"Peak continuous current ({total_cont:.1f} A) exceeds PM max continuous current rating ({pm['max_continuous_current_a']:.1f} A)."
    return True, ""


def check_servo_torque(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """3. Servo torque insufficient check: servo torque vs required aero torque."""
    ensure_evaluated(candidate, context)
    dv = candidate.design_variables
    derived = candidate.derived_variables
    servo = dv["servo"]
    req_torque = derived["required_servo_torque_kgcm"]

    if servo["torque_kgcm"] < req_torque:
        return False, f"Selected servo torque ({servo['torque_kgcm']:.1f} kg-cm) is below aerodynamic torque requirements ({req_torque:.1f} kg-cm)."
    return True, ""


def check_bec_capacity(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """4. BEC overloaded check: continuous/peak servo load vs BEC limits."""
    ensure_evaluated(candidate, context)
    dv = candidate.design_variables
    derived = candidate.derived_variables
    bec = dv["bec"]
    servo_cont = derived["servo_cont_current_a"]
    servo_peak = derived["servo_peak_current_a"]

    if servo_cont > bec["max_continuous_current_a"]:
        return False, f"Servos continuous current draw ({servo_cont:.1f} A) exceeds BEC continuous rating ({bec['max_continuous_current_a']:.1f} A)."
    if servo_peak > bec["max_peak_current_a"]:
        return False, f"Servos peak current draw ({servo_peak:.1f} A) exceeds BEC peak rating ({bec['max_peak_current_a']:.1f} A)."
    return True, ""


def check_gps_interference(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """5. GPS interference check: high power telemetry modems vs standard GPS shielding."""
    ensure_evaluated(candidate, context)
    dv = candidate.design_variables
    telemetry = dv["telemetry"]
    gps = dv["gps"]

    # Reject if telemetry power is high (>= 2.5W) and GPS is not high-end dual/shielded (doesn't support dual frequency)
    if telemetry["power_w"] >= 2.5 and not gps["supports_dual"]:
        return False, f"High-power telemetry transmitter '{telemetry['name']}' causes critical RF interference on standard M8N GNSS receiver '{gps['name']}'; shielded dual-frequency RTK GNSS required."
    return True, ""


def check_telemetry_compatibility(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """6. Telemetry incompatible check: telemetry range capability vs mission range target."""
    ensure_evaluated(candidate, context)
    dv = candidate.design_variables
    telemetry = dv["telemetry"]
    
    profile = context.requirements.mission_result.mission_profile
    range_target_km = profile.mission_range_km

    if telemetry["max_range_km"] < range_target_km:
        return False, f"Telemetry radio max range ({telemetry['max_range_km']:.1f} km) is below required target range ({range_target_km:.1f} km)."
    return True, ""


def check_connector_rating(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """7. Connector mismatch check: connector rating vs peak current."""
    ensure_evaluated(candidate, context)
    dv = candidate.design_variables
    derived = candidate.derived_variables
    
    # We retrieve the selected connector
    connector_name = derived["connector_name"]
    # We find the connector record
    from backend.design.fixed_wing.electrical.candidate_generator import build_electrical_repository
    repo = build_electrical_repository()
    connector = next(c for c in repo.get_components_by_category(ComponentCategory.CUSTOM) if c["name"] == connector_name)

    total_peak = derived["total_peak_current_a"]
    if connector["max_continuous_current_a"] < total_peak:
        return False, f"Selected connector '{connector_name}' (max {connector['max_continuous_current_a']} A) is overloaded under peak load ({total_peak:.1f} A)."
    return True, ""


def check_wire_sizing(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """8. Wire gauge insufficient check: wire ampacity and voltage drop checks."""
    ensure_evaluated(candidate, context)
    derived = candidate.derived_variables
    total_cont = derived["total_continuous_current_a"]
    voltage_drop = derived["voltage_drop_percent"]

    # We retrieve the selected wire record
    wire_name = derived["wire_name"]
    from backend.design.fixed_wing.electrical.candidate_generator import build_electrical_repository
    repo = build_electrical_repository()
    wire = next(w for w in repo.get_components_by_category(ComponentCategory.CUSTOM) if w["name"] == wire_name)

    if wire["max_continuous_current_a"] < total_cont:
        return False, f"Selected wiring '{wire_name}' (max {wire['max_continuous_current_a']} A) is overloaded under continuous draw ({total_cont:.1f} A)."
    if voltage_drop > 2.0:
        return False, f"Line voltage drop ({voltage_drop:.2f}%) exceeds the maximum allowable drop (2.0%)."
    return True, ""


def check_mission_equipment_interface(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """9. Mission equipment unsupported check: flight controller compatible interfaces check."""
    ensure_evaluated(candidate, context)
    dv = candidate.design_variables
    fc = dv["flight_controller"]
    payload = dv["mission_equipment"]

    # Check that flight controller provides required interfaces for the mission payload
    fc_interfaces = fc["interfaces"]
    payload_interfaces = payload.get("interfaces", [])
    for p_inf in payload_interfaces:
        if p_inf not in fc_interfaces:
            return False, f"Flight controller '{fc['name']}' lacks the high-speed interface '{p_inf}' required by mission payload '{payload['name']}'."
    return True, ""


def check_cooling_feasibility(candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
    """10. Cooling impossible check: Cabin thermal loading verification."""
    ensure_evaluated(candidate, context)
    dv = candidate.design_variables
    derived = candidate.derived_variables
    telemetry = dv["telemetry"]
    
    # Estimate heat dissipation inside electronics cabin
    # Line loss heating: P_heat_wire = total_cont_current^2 * wire_resistance
    wire_name = derived["wire_name"]
    from backend.design.fixed_wing.electrical.candidate_generator import build_electrical_repository
    repo = build_electrical_repository()
    wire = next(w for w in repo.get_components_by_category(ComponentCategory.CUSTOM) if w["name"] == wire_name)

    total_cont = derived["total_continuous_current_a"]
    p_heat_wire = (total_cont ** 2) * (wire["resistance_mohm_per_m"] / 1000.0) * 0.5
    # Telemetry radio self-heating
    p_heat_radio = telemetry["power_w"] * 0.6  # assume 60% power dissipated as heat in cabin

    total_dissipated_heat_w = p_heat_wire + p_heat_radio

    # Structural limit: in typical carbon fiber cabins, heat dissipation above 15.0W triggers throttling
    if total_dissipated_heat_w > 15.0:
        return False, f"Cabin thermal heat load ({total_dissipated_heat_w:.1f} W) exceeds static dissipation limit (15.0 W); risk of component thermal runaway."
    return True, ""


def build_electrical_constraints() -> List[callable]:
    """Returns all 10 constraint validation check functions."""
    return [
        check_voltage_compatibility,
        check_current_limits,
        check_servo_torque,
        check_bec_capacity,
        check_gps_interference,
        check_telemetry_compatibility,
        check_connector_rating,
        check_wire_sizing,
        check_mission_equipment_interface,
        check_cooling_feasibility,
    ]
