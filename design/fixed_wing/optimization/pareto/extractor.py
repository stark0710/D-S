"""
Pareto Front Extraction Engine for Fixed-Wing Aircraft Design.
"""

from typing import List, Dict, Tuple, Optional, Any
from backend.design.fixed_wing.optimization.pareto.models import (
    ObjectiveDirection,
    ParetoObjectiveDefinition,
    ParetoObjectiveValue,
    ParetoTolerance,
    ParetoCandidate,
    ParetoFrontResult,
)
from backend.design.fixed_wing.optimization.pareto.dominance import (
    check_dominance,
    is_duplicate,
)


DEFAULT_OBJECTIVE_DEFINITIONS: List[ParetoObjectiveDefinition] = [
    ParetoObjectiveDefinition(
        name="mtow",
        direction=ObjectiveDirection.MINIMIZE,
        unit="kg",
        description="Maximum Takeoff Weight",
    ),
    ParetoObjectiveDefinition(
        name="endurance",
        direction=ObjectiveDirection.MAXIMIZE,
        unit="min",
        description="Mission Flight Endurance",
    ),
    ParetoObjectiveDefinition(
        name="range",
        direction=ObjectiveDirection.MAXIMIZE,
        unit="km",
        description="Mission Flight Range",
    ),
    ParetoObjectiveDefinition(
        name="payload_capability",
        direction=ObjectiveDirection.MAXIMIZE,
        unit="kg",
        description="Installed Payload Capability",
    ),
    ParetoObjectiveDefinition(
        name="efficiency",
        direction=ObjectiveDirection.MAXIMIZE,
        unit="dimensionless",
        description="Aerodynamic Lift-to-Drag Ratio (L/D)",
    ),
]


def build_candidate_from_result(
    result: Any,
    candidate_id: str,
    provenance: str = "Aircraft Sizing Engine",
    is_selected: bool = False,
) -> ParetoCandidate:
    """
    Constructs a typed ParetoCandidate from a FixedWingDesignResult or specification.
    Extracts authoritative typed values for all 5 Pareto objectives, engineering summary,
    and manufacturer-independent technical specifications.
    """
    spec = getattr(result, "final_specification", None)
    
    # 1. Feasibility validation
    is_feasible = bool(getattr(result, "success", False) and getattr(result, "converged", False))
    
    # Verification check
    verif = getattr(result, "verification_result", None)
    if verif is not None:
        if hasattr(verif, "passed") and not verif.passed:
            is_feasible = False
        elif hasattr(verif, "is_verified") and not verif.is_verified:
            is_feasible = False

    # 2. Authoritative Objective Extraction
    # MTOW (kg)
    mtow_val = 0.0
    if spec and hasattr(spec, "mass_properties") and hasattr(spec.mass_properties, "maximum_takeoff_weight_kg"):
        mtow_val = float(spec.mass_properties.maximum_takeoff_weight_kg)
    elif getattr(result, "mass_properties_result", None) and hasattr(result.mass_properties_result, "maximum_takeoff_weight_kg"):
        mtow_val = float(result.mass_properties_result.maximum_takeoff_weight_kg)
    elif getattr(result, "mass_properties_result", None) and hasattr(result.mass_properties_result, "total_mass_kg"):
        mtow_val = float(result.mass_properties_result.total_mass_kg)

    # Endurance (min)
    endurance_val = 0.0
    if spec and hasattr(spec, "performance") and hasattr(spec.performance, "endurance_min"):
        endurance_val = float(spec.performance.endurance_min)
    elif getattr(result, "performance_result", None) and hasattr(result.performance_result, "endurance_analysis"):
        endurance_val = float(getattr(result.performance_result.endurance_analysis, "operational_flight_time_min", 0.0))
        if endurance_val <= 0.0:
            endurance_val = float(getattr(result.performance_result.endurance_analysis, "maximum_flight_time_min", 0.0))

    # Range (km)
    range_val = 0.0
    if spec and hasattr(spec, "performance") and hasattr(spec.performance, "range_km"):
        range_val = float(spec.performance.range_km)
    elif getattr(result, "performance_result", None) and hasattr(result.performance_result, "range_analysis"):
        range_val = float(getattr(result.performance_result.range_analysis, "operational_range_km", 0.0))
        if range_val <= 0.0:
            range_val = float(getattr(result.performance_result.range_analysis, "maximum_range_km", 0.0))

    # Payload Capability (kg)
    payload_val = 0.0
    payload_res = getattr(result, "payload_result", None)
    if payload_res and hasattr(payload_res, "installed_payload_mass_kg") and payload_res.installed_payload_mass_kg > 0.0:
        payload_val = float(payload_res.installed_payload_mass_kg)
    elif payload_res and hasattr(payload_res, "requested_payload_mass_kg") and payload_res.requested_payload_mass_kg > 0.0:
        payload_val = float(payload_res.requested_payload_mass_kg)
    elif spec and hasattr(spec, "payload") and hasattr(spec.payload, "installed_payload_mass_kg"):
        payload_val = float(spec.payload.installed_payload_mass_kg)
    elif spec and hasattr(spec, "mission") and isinstance(spec.mission, dict) and "payload_kg" in spec.mission:
        payload_val = float(spec.mission["payload_kg"])
    elif getattr(result, "mission_result", None) and hasattr(result.mission_result, "mission_profile"):
        payload_val = float(getattr(result.mission_result.mission_profile, "payload_kg", 0.0))

    # Efficiency (Aerodynamic L/D)
    efficiency_val = 0.0
    perf_res = getattr(result, "performance_result", None)
    if perf_res and hasattr(perf_res, "aerodynamic_analysis") and hasattr(perf_res.aerodynamic_analysis, "lift_to_drag_ratio"):
        efficiency_val = float(perf_res.aerodynamic_analysis.lift_to_drag_ratio)
    elif spec and hasattr(spec, "performance") and hasattr(spec.performance, "aerodynamic_analysis"):
        aero = getattr(spec.performance, "aerodynamic_analysis", None)
        if aero and hasattr(aero, "lift_to_drag_ratio"):
            efficiency_val = float(aero.lift_to_drag_ratio)
    elif perf_res and hasattr(perf_res, "glide_analysis") and hasattr(perf_res.glide_analysis, "glide_ratio"):
        efficiency_val = float(perf_res.glide_analysis.glide_ratio)

    objectives = {
        "mtow": ParetoObjectiveValue("mtow", ObjectiveDirection.MINIMIZE, mtow_val, "kg"),
        "endurance": ParetoObjectiveValue("endurance", ObjectiveDirection.MAXIMIZE, endurance_val, "min"),
        "range": ParetoObjectiveValue("range", ObjectiveDirection.MAXIMIZE, range_val, "km"),
        "payload_capability": ParetoObjectiveValue("payload_capability", ObjectiveDirection.MAXIMIZE, payload_val, "kg"),
        "efficiency": ParetoObjectiveValue("efficiency", ObjectiveDirection.MAXIMIZE, efficiency_val, "dimensionless"),
    }

    # 3. Subsystem Resolution (prefer converged spec, fallback to initial result)
    wing_res = getattr(spec, "wing", None) or getattr(result, "wing_result", None)
    prop_res = getattr(spec, "propulsion", None) or getattr(result, "propulsion_result", None)
    tail_res = getattr(spec, "tail", None) or getattr(result, "tail_result", None)
    cg_res = getattr(spec, "cg", None) or getattr(result, "cg_result", None)
    mass_res = getattr(spec, "mass_properties", None) or getattr(result, "mass_properties_result", None)
    perf_res = getattr(spec, "performance", None) or getattr(result, "performance_result", None)

    # CG Position resolution
    cg_pos = getattr(cg_res, "cg_position", None)
    if isinstance(cg_pos, (list, tuple)) and len(cg_pos) > 0:
        cg_x_val = float(cg_pos[0])
    else:
        cg_x_val = float(getattr(cg_res, "x_cg_m", 0.0))

    # Wingspan resolution
    span_val = float(getattr(wing_res, "wingspan", getattr(wing_res, "wing_span", 0.0)))

    # Tail configuration resolution
    tail_cfg = getattr(tail_res, "tail_configuration", getattr(tail_res, "configuration", "Conventional"))

    summary: Dict[str, Any] = {
        "mtow_kg": round(mtow_val, 4),
        "empty_weight_kg": round(float(getattr(mass_res, "empty_weight_kg", 0.0)), 4) if mass_res else 0.0,
        "wingspan_m": round(span_val, 4),
        "wing_area_m2": round(float(getattr(wing_res, "wing_area", 0.0)), 4) if wing_res else 0.0,
        "aspect_ratio": round(float(getattr(wing_res, "aspect_ratio", 0.0)), 2) if wing_res else 0.0,
        "root_chord_m": round(float(getattr(wing_res, "root_chord", 0.0)), 4) if wing_res else 0.0,
        "cg_x": round(cg_x_val, 4),
        "static_margin": round(float(getattr(cg_res, "static_margin", 0.0)), 4) if cg_res else 0.0,
        "stall_speed_kmh": round(float(getattr(perf_res, "stall_speed_kmh", 0.0)), 2) if perf_res else 0.0,
        "cruise_speed_kmh": round(float(getattr(perf_res, "cruise_speed_kmh", 0.0)), 2) if perf_res else 0.0,
        "cruise_power_w": round(float(getattr(prop_res, "cruise_power_w", 0.0)), 2) if prop_res else 0.0,
        "endurance_min": round(endurance_val, 2),
        "range_km": round(range_val, 2),
        "motor_name": getattr(prop_res, "motor_name", "Unknown"),
        "propeller_name": getattr(prop_res, "propeller_name", "Unknown"),
        "esc_name": getattr(prop_res, "esc_name", "Unknown"),
        "battery_name": getattr(prop_res, "battery_name", "Unknown"),
        "tail_config": tail_cfg,
    }

    # 4. Manufacturer-Independent Component Engineering Requirements
    op_voltage = float(getattr(prop_res, "operating_voltage_v", 0.0)) if prop_res else 0.0
    cell_count = int(getattr(prop_res, "cell_count_s", 0)) if prop_res else 0
    cr_current = float(getattr(prop_res, "cruise_current_a", 0.0)) if prop_res else 0.0
    climb_current = float(getattr(prop_res, "max_climb_current_a", 0.0)) if prop_res else 0.0
    bat_cap = float(getattr(prop_res, "battery_capacity_mah", 0.0)) if prop_res else 0.0
    bat_wt = float(getattr(prop_res, "battery_weight_g", 0.0)) if prop_res else 0.0
    bat_wh = float(getattr(prop_res, "battery_energy_wh", 0.0)) if prop_res else 0.0
    req_wh = float(getattr(prop_res, "required_energy_wh", 0.0)) if prop_res else 0.0
    bat_chem = str(getattr(prop_res, "battery_chemistry", "LiPo")) if prop_res else "LiPo"
    bat_c = float(getattr(prop_res, "battery_c_rating", 0.0)) if prop_res else 0.0
    cr_power = float(getattr(prop_res, "cruise_power_w", 0.0)) if prop_res else 0.0
    to_power = float(getattr(prop_res, "takeoff_power_w", 0.0)) if prop_res else 0.0
    stat_thrust = float(getattr(prop_res, "static_thrust_n", 0.0)) if prop_res else 0.0
    mot_eff = float(getattr(prop_res, "motor_efficiency", 0.85)) if prop_res else 0.85
    prop_eff = float(getattr(prop_res, "propeller_efficiency", 0.70)) if prop_res else 0.70

    technical_specs: Dict[str, Any] = {
        "motor": {
            "type": "Brushless DC Outrunner",
            "required_nominal_voltage_v": op_voltage,
            "cell_count_s": cell_count,
            "required_static_thrust_n": stat_thrust,
            "continuous_power_w": cr_power,
            "peak_power_w": to_power,
            "propeller_compatibility": getattr(prop_res, "propeller_name", "Unknown"),
            "efficiency_target": mot_eff,
        },
        "battery": {
            "chemistry": bat_chem,
            "cell_count_s": cell_count,
            "nominal_voltage_v": op_voltage,
            "required_capacity_mah": bat_cap,
            "required_energy_wh": req_wh if req_wh > 0.0 else bat_wh,
            "installed_energy_wh": bat_wh,
            "continuous_current_a": cr_current,
            "peak_current_a": climb_current,
            "minimum_c_rating": bat_c,
            "maximum_pack_mass_g": bat_wt,
        },
        "esc": {
            "supported_voltage_v": op_voltage,
            "continuous_current_rating_a": round(cr_current * 1.25, 1),
            "peak_current_rating_a": round(climb_current * 1.2, 1),
            "telemetry_protocol": "PWM / DShot",
        },
        "propeller": {
            "designation": getattr(prop_res, "propeller_name", "Unknown"),
            "configuration": "Fixed Pitch Tractor/Pusher",
            "efficiency_target": prop_eff,
            "motor_compatibility": getattr(prop_res, "motor_name", "Unknown"),
        },
    }

    return ParetoCandidate(
        candidate_id=candidate_id,
        is_feasible=is_feasible,
        pareto_rank=1,
        is_selected_design=is_selected,
        objectives=objectives,
        engineering_summary=summary,
        technical_specifications=technical_specs,
        provenance=provenance,
        specification=spec,
    )


class ParetoFrontExtractor:
    """
    Deterministic Pareto front extractor implementing non-dominated sorting
    and engineering-tolerance deduplication.
    """

    def __init__(
        self,
        tolerances: Optional[ParetoTolerance] = None,
        objective_definitions: Optional[List[ParetoObjectiveDefinition]] = None,
    ):
        self.tolerances = tolerances if tolerances is not None else ParetoTolerance()
        self.objective_definitions = (
            objective_definitions
            if objective_definitions is not None
            else list(DEFAULT_OBJECTIVE_DEFINITIONS)
        )

    def extract(self, candidates: List[ParetoCandidate]) -> ParetoFrontResult:
        """
        Extracts the non-dominated Pareto front from a candidate archive.
        """
        total_count = len(candidates)
        if total_count == 0:
            return ParetoFrontResult(
                enabled=True,
                objective_definitions=self.objective_definitions,
                candidate_count=0,
                feasible_candidate_count=0,
                dominated_candidate_count=0,
                deduplicated_count=0,
                front_size=0,
                front=[],
                methodology="Bounded Feasible Candidate Nondominated Sorting",
                warnings=["Candidate pool is empty"],
            )

        # 1. Feasibility Filter
        feasible_candidates: List[ParetoCandidate] = [c for c in candidates if c.is_feasible]
        feasible_count = len(feasible_candidates)

        if feasible_count == 0:
            return ParetoFrontResult(
                enabled=True,
                objective_definitions=self.objective_definitions,
                candidate_count=total_count,
                feasible_candidate_count=0,
                dominated_candidate_count=0,
                deduplicated_count=0,
                front_size=0,
                front=[],
                methodology="Bounded Feasible Candidate Nondominated Sorting",
                warnings=["NO_FEASIBLE_CANDIDATES: All provided candidates failed feasibility constraints"],
            )

        # 2. Non-dominated Sorting (Rank 1 identification)
        # A candidate is dominated if there exists any other feasible candidate that dominates it.
        nondominated: List[ParetoCandidate] = []
        dominated: List[ParetoCandidate] = []

        for i, cand_a in enumerate(feasible_candidates):
            is_dom = False
            for j, cand_b in enumerate(feasible_candidates):
                if i == j:
                    continue
                if check_dominance(cand_b, cand_a, self.tolerances):
                    is_dom = True
                    break
            if is_dom:
                cand_a.pareto_rank = 2
                dominated.append(cand_a)
            else:
                cand_a.pareto_rank = 1
                nondominated.append(cand_a)

        dominated_count = len(dominated)

        # 3. Deduplication within Numerical Tolerance
        # If two nondominated candidates are within tolerance on all 5 objectives, keep one deterministic representative.
        deduplicated_front: List[ParetoCandidate] = []
        deduplicated_count = 0

        for cand in nondominated:
            matched_dup = False
            for existing in deduplicated_front:
                if is_duplicate(cand, existing, self.tolerances):
                    matched_dup = True
                    # If the duplicate candidate is the user-selected design, replace existing with selected
                    if cand.is_selected_design and not existing.is_selected_design:
                        deduplicated_front.remove(existing)
                        deduplicated_front.append(cand)
                    break
            if not matched_dup:
                deduplicated_front.append(cand)
            else:
                deduplicated_count += 1

        # 4. Deterministic Ordering
        # Order by:
        # 1. Pareto rank ascending
        # 2. MTOW ascending (minimize)
        # 3. Endurance descending (maximize)
        # 4. Range descending (maximize)
        # 5. Payload descending (maximize)
        # 6. Efficiency descending (maximize)
        # 7. Candidate ID ascending
        def sort_key(c: ParetoCandidate):
            return (
                c.pareto_rank,
                c.get_value("mtow"),
                -c.get_value("endurance"),
                -c.get_value("range"),
                -c.get_value("payload_capability"),
                -c.get_value("efficiency"),
                c.candidate_id,
            )

        sorted_front = sorted(deduplicated_front, key=sort_key)

        return ParetoFrontResult(
            enabled=True,
            objective_definitions=self.objective_definitions,
            candidate_count=total_count,
            feasible_candidate_count=feasible_count,
            dominated_candidate_count=dominated_count,
            deduplicated_count=deduplicated_count,
            front_size=len(sorted_front),
            front=sorted_front,
            methodology="Bounded Feasible Candidate Nondominated Sorting",
            warnings=[],
            diagnostics={
                "candidate_pool_size": total_count,
                "feasible_size": feasible_count,
                "dominated_size": dominated_count,
                "deduplicated_size": deduplicated_count,
                "final_front_size": len(sorted_front),
            },
        )


def self_check_pareto_front(
    front_result: ParetoFrontResult,
    tolerances: Optional[ParetoTolerance] = None,
) -> Tuple[bool, List[str]]:
    """
    Forensic mathematical self-check for a Pareto front result:
    1. Every returned point is feasible.
    2. For every pair (A, B) on the front: NOT dominates(A, B) and NOT dominates(B, A).
    3. No duplicate points remain within numerical tolerance.
    """
    if tolerances is None:
        tolerances = ParetoTolerance()

    errors: List[str] = []
    front = front_result.front

    # 1. Feasibility check
    for c in front:
        if not c.is_feasible:
            errors.append(f"Infeasible candidate '{c.candidate_id}' found on Pareto front")

    # 2. Mutual non-dominance check
    n = len(front)
    for i in range(n):
        for j in range(i + 1, n):
            a = front[i]
            b = front[j]
            if check_dominance(a, b, tolerances):
                errors.append(
                    f"Dominance violation: Candidate '{a.candidate_id}' dominates candidate '{b.candidate_id}' on the Pareto front"
                )
            if check_dominance(b, a, tolerances):
                errors.append(
                    f"Dominance violation: Candidate '{b.candidate_id}' dominates candidate '{a.candidate_id}' on the Pareto front"
                )
            if is_duplicate(a, b, tolerances):
                errors.append(
                    f"Deduplication violation: Candidates '{a.candidate_id}' and '{b.candidate_id}' are duplicates within tolerance"
                )

    return (len(errors) == 0, errors)
