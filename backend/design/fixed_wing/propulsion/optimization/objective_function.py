"""
Fixed-Wing Propulsion Sizing Objective Function

Calculates the overall optimization score based on efficiency, mass,
thrust margin, reliability, and flight endurance.
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class PropulsionObjectiveFunction:
    """Computes the overall optimization score for a propulsion candidate."""

    def __init__(self) -> None:
        self.weights = {
            "electrical_efficiency": 0.15,
            "weight": 0.15,
            "cruise_efficiency": 0.15,
            "takeoff_margin": 0.15,
            "endurance": 0.20,
            "reliability": 0.10,
            "future_upgrade_margin": 0.10,
        }

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """Evaluates the multi-objective score of the candidate."""
        if candidate.status == "FAILED" or not candidate.constraints_passed:
            candidate.overall_score = -999.0
            return -999.0

        dv = candidate.design_variables
        derived = candidate.derived_variables

        motor = dv["motor"]
        esc = dv["esc"]

        # 1. Electrical Efficiency
        total_eff = derived.get("total_efficiency", 0.50)
        score_eff = max(0.0, min(1.0, (total_eff - 0.35) / 0.35))

        # 2. Weight (minimize total mass)
        total_w = derived.get("total_propulsion_weight_g", 500.0)
        score_weight = max(0.0, min(1.0, 1.0 - (total_w / 4000.0)))

        # 3. Cruise Efficiency (minimize cruise power)
        cruise_pwr = derived.get("cruise_power_w", 200.0)
        score_cruise_pwr = max(0.0, min(1.0, 1.0 - (cruise_pwr / 2000.0)))

        # 4. Takeoff Margin (maximize thrust-to-weight ratio)
        static_thrust = derived.get("static_thrust_n", 10.0)
        req_thrust = derived.get("takeoff_thrust_n", 5.0)
        t_w_margin = static_thrust / max(1.0, req_thrust)
        score_takeoff = max(0.0, min(1.0, (t_w_margin - 1.0) / 1.5)) if t_w_margin >= 1.0 else 0.0

        # 5. Target-Aware Endurance (Phase 6B-3)
        # Determine controlling mission target from endurance or range requirements
        m_prof = getattr(getattr(context.requirements, "mission_result", None), "mission_profile", None)
        t_target = 45.0
        r_target = 30.0
        v_cruise = 70.0
        if m_prof:
            t_target = getattr(m_prof, "flight_time_min", t_target)
            r_target = getattr(m_prof, "mission_range_km", r_target)
            v_cruise = getattr(m_prof, "cruise_speed_kmh", v_cruise)
        elif hasattr(context.requirements, "target_flight_time_min"):
            t_target = getattr(context.requirements, "target_flight_time_min", t_target)
            r_target = getattr(context.requirements, "target_range_km", r_target)
            v_cruise = getattr(context.requirements, "cruise_speed_kmh", v_cruise)

        controlling_target_min = t_target
        if v_cruise > 0 and r_target > 0:
            t_range = (r_target / v_cruise) * 60.0
            controlling_target_min = max(controlling_target_min, t_range)

        flight_time = derived.get("estimated_flight_time_min", 30.0)
        if controlling_target_min <= 0.0:
            score_endur = max(0.0, min(1.0, flight_time / 180.0))
        elif flight_time < controlling_target_min:
            # Under-performing battery is heavily penalized
            score_endur = max(0.0, (flight_time / controlling_target_min) * 0.40)
        else:
            # Target met: 0.85 baseline score for satisfying target
            # Moderate margin (up to 30% above target) scales to 1.0
            # Excessive capacity beyond 30% plateaus at 1.0, allowing weight and cruise
            # power objectives to naturally penalize unnecessary mass.
            excess_ratio = (flight_time - controlling_target_min) / controlling_target_min
            if excess_ratio <= 0.30:
                score_endur = 0.85 + (excess_ratio / 0.30) * 0.15
            else:
                score_endur = 1.0


        # 6. Reliability (minimize climb current vs motor limit)
        climb_curr = derived.get("climb_current_a", 10.0)
        motor_max_curr = motor["max_current_a"]
        climb_current_ratio = climb_curr / max(1.0, motor_max_curr)
        score_rel = max(0.0, min(1.0, 1.0 - climb_current_ratio))

        # 7. Future Upgrade Margin (maximize ESC current headroom)
        esc_max_curr = esc["continuous_current_a"]
        esc_margin_ratio = climb_curr / max(1.0, esc_max_curr)
        score_esc_margin = max(0.0, min(1.0, 1.0 - esc_margin_ratio))

        # Adjust weights based on mission category and optimization priority
        category = getattr(context.requirements.mission_result, "mission_category", "Survey")
        cat_name = category.value if hasattr(category, 'value') else str(category)

        priority = getattr(context, "optimization_priority", None)
        from backend.design.common.requirements.optimization_priority import OptimizationPriority
        if priority is None:
            priority = OptimizationPriority.BALANCED
        from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
        weights = OptimizationPriorityPolicy.get_propulsion_weights(priority, cat_name)

        # Calculate score
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
