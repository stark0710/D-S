from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
import backend.design.fixed_wing.propulsion.optimization.objective_function as p_obj_mod

orig_evaluate = p_obj_mod.PropulsionObjectiveFunction.evaluate

def target_aware_evaluate(self, candidate, context):
    if candidate.status == "FAILED" or not candidate.constraints_passed:
        candidate.overall_score = -999.0
        return -999.0

    dv = candidate.design_variables
    derived = candidate.derived_variables
    motor = dv["motor"]
    esc = dv["esc"]

    m_prof = getattr(getattr(context.requirements, "mission_result", None), "mission_profile", None)
    t_target = getattr(m_prof, "flight_time_min", 45.0) if m_prof else 45.0
    r_target = getattr(m_prof, "mission_range_km", 30.0) if m_prof else 30.0
    v_cruise = getattr(m_prof, "cruise_speed_kmh", 70.0) if m_prof else 70.0
    if v_cruise > 0 and r_target > 0:
        t_range = (r_target / v_cruise) * 60.0
        t_target = max(t_target, t_range)

    flight_time = derived.get("estimated_flight_time_min", 30.0)

    # 1. Electrical Efficiency
    total_eff = derived.get("total_efficiency", 0.50)
    score_eff = max(0.0, min(1.0, (total_eff - 0.35) / 0.35))

    # 2. Weight
    total_w = derived.get("total_propulsion_weight_g", 500.0)
    score_weight = max(0.0, min(1.0, 1.0 - (total_w / 4000.0)))

    # 3. Cruise Efficiency
    cruise_pwr = derived.get("cruise_power_w", 200.0)
    score_cruise_pwr = max(0.0, min(1.0, 1.0 - (cruise_pwr / 2000.0)))

    # 4. Takeoff Margin
    static_thrust = derived.get("static_thrust_n", 10.0)
    req_thrust = derived.get("takeoff_thrust_n", 5.0)
    t_w_margin = static_thrust / max(1.0, req_thrust)
    score_takeoff = max(0.0, min(1.0, (t_w_margin - 1.0) / 1.5)) if t_w_margin >= 1.0 else 0.0

    # 5. Target-Aware Endurance
    if flight_time < t_target:
        score_endur = max(0.0, (flight_time / t_target) * 0.4)
    else:
        excess_ratio = (flight_time - t_target) / t_target
        if excess_ratio <= 0.30:
            score_endur = 0.85 + (excess_ratio / 0.30) * 0.15
        else:
            score_endur = 1.0

    # 6. Reliability
    climb_curr = derived.get("climb_current_a", 10.0)
    motor_max_curr = motor["max_current_a"]
    climb_current_ratio = climb_curr / max(1.0, motor_max_curr)
    score_rel = max(0.0, min(1.0, 1.0 - climb_current_ratio))

    # 7. Future Upgrade Margin
    esc_max_curr = esc["continuous_current_a"]
    esc_margin_ratio = climb_curr / max(1.0, esc_max_curr)
    score_esc_margin = max(0.0, min(1.0, 1.0 - esc_margin_ratio))

    category = getattr(context.requirements.mission_result, "mission_category", "Survey")
    cat_name = category.value if hasattr(category, 'value') else str(category)
    priority = getattr(context, "optimization_priority", OptimizationPriority.BALANCED)
    from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
    weights = OptimizationPriorityPolicy.get_propulsion_weights(priority, cat_name)

    score = (
        weights["electrical_efficiency"] * score_eff +
        weights["weight"] * score_weight +
        weights["cruise_efficiency"] * score_cruise_pwr +
        weights["takeoff_margin"] * score_takeoff +
        weights["endurance"] * score_endur +
        weights["reliability"] * score_rel +
        weights["future_upgrade_margin"] * score_esc_margin
    )
    candidate.objective_scores = {
        "electrical_efficiency": score_eff,
        "weight": score_weight,
        "cruise_efficiency": score_cruise_pwr,
        "takeoff_margin": score_takeoff,
        "endurance": score_endur,
        "reliability": score_rel,
        "future_upgrade_margin": score_esc_margin,
    }
    candidate.overall_score = score
    return score

p_obj_mod.PropulsionObjectiveFunction.evaluate = target_aware_evaluate

pipeline = FixedWingDesignPipeline()
for p in [OptimizationPriority.BALANCED, OptimizationPriority.LOWEST_WEIGHT, OptimizationPriority.LOWEST_COST, OptimizationPriority.MAXIMUM_ENDURANCE, OptimizationPriority.MAXIMUM_RANGE, OptimizationPriority.HIGHEST_EFFICIENCY]:
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=p
    )
    res = pipeline.execute(req)
    spec = res.final_specification
    batt_name = getattr(spec.propulsion, "battery_name", None)
    batt_cap = getattr(spec.propulsion, "battery_capacity_mah", None)
    batt_w = getattr(spec.propulsion, "battery_weight_g", None)
    endurance = getattr(spec.performance, "endurance_min", None)
    mtow = getattr(spec.mass_properties, "maximum_takeoff_weight_kg", None)
    ar = getattr(spec.wing, "aspect_ratio", None)
    print(f"Priority: {p.value:18} | MTOW: {mtow:5.3f} kg | AR: {ar:4.1f} | Batt: {batt_name} ({batt_cap} mAh, {batt_w} g) | Endur: {endurance:5.1f} min")
