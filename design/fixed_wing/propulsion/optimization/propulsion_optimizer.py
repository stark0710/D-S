"""
Fixed-Wing Propulsion Optimization Engine

Subclasses OptimizerBase to orchestrate motor, propeller, ESC, and battery searches.
"""

from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.propulsion.optimization.models import PropulsionSpecification
from backend.design.fixed_wing.propulsion.optimization.result import PropulsionOptimizationResult
from backend.design.fixed_wing.propulsion.optimization.candidate_generator import GridSearchPropulsionCandidateGenerator
from backend.design.fixed_wing.propulsion.optimization.constraints import build_propulsion_constraints
from backend.design.fixed_wing.propulsion.optimization.objective_function import PropulsionObjectiveFunction


class PropulsionOptimizer(OptimizerBase):
    """
    Subsystem optimizer resolving the optimal electric motor, propeller, ESC,
    and battery pack using a deterministic grid search evaluated against
    the PropulsionEngine backend.
    """

    def __init__(self) -> None:
        super().__init__("PropulsionOptimizer")
        # Define objective scoring backend
        self.propulsion_objective = PropulsionObjectiveFunction()

        # Register physical and safety constraints
        for check in build_propulsion_constraints():
            self.constraints.add_constraint(check.__name__, check)

        # Register objectives in self.objective
        self.objective.add_objective(
            name="propulsion_score",
            score_fn=lambda cand, ctx: self.propulsion_objective.evaluate(cand, ctx),
            weight=1.0,
            minimize=False  # We want to maximize the fitness score
        )

    def optimize(self, context: OptimizationContext) -> PropulsionOptimizationResult:
        """Runs the optimization search and returns a typed result."""
        res = super().optimize(context)
        return PropulsionOptimizationResult(
            winning_candidate=res.winning_candidate,
            generated_specification=res.generated_specification,
            success=res.success,
            message=res.message,
            evaluated_count=res.evaluated_count,
            feasible_count=res.feasible_count,
            history=res.history,
            rejected_summary=res.rejected_summary,
            execution_time_seconds=res.execution_time_seconds,
            iteration_count=res.iteration_count,
            diagnostics=res.diagnostics,
        )

    # ------------------------------------------------------------------
    #  OptimizerBase lifecycle hooks
    # ------------------------------------------------------------------

    def initialize(self, context: OptimizationContext) -> None:
        priority = getattr(context, "optimization_priority", None)
        if priority is not None:
            cat_name = None
            if hasattr(context.requirements, "mission_result") and hasattr(context.requirements.mission_result, "mission_category"):
                cat = context.requirements.mission_result.mission_category
                cat_name = cat.value if hasattr(cat, "value") else str(cat)
            from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
            self.propulsion_objective.weights = OptimizationPriorityPolicy.get_propulsion_weights(priority, cat_name)

    def generate_candidates(
        self, context: OptimizationContext
    ) -> List[OptimizationCandidate]:
        generator = GridSearchPropulsionCandidateGenerator()
        cands = generator.generate_candidates(context)
        context._active_propulsion_candidates = cands
        return cands


    def evaluate_candidate(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> None:
        # Evaluation is handled dynamically on-demand during constraint checks
        pass

    def build_specification(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> PropulsionSpecification:
        dv = candidate.design_variables
        derived = candidate.derived_variables

        # Extract values
        motor = dv["motor"]
        prop = dv["propeller"]
        esc = dv["esc"]
        batt = dv["battery"]

        # Re-extract positive score from objective scores dictionary
        pos_score = candidate.objective_scores.get("propulsion_score", 0.0)

        battery_chemistry = batt.get("chemistry", "LiPo")
        battery_energy_wh = round(derived.get("battery_nominal_energy_wh", (batt["nominal_voltage_v"] * batt["capacity_mah"]) / 1000.0), 2)
        required_energy_wh = round(derived.get("required_energy_wh", 0.0), 2)
        battery_c_rating = float(batt.get("discharge_rating_c", batt.get("discharge_c", 0.0)))
        required_c_rating = round(derived.get("required_c_rating", 0.0), 2)
        target_endurance_min = round(derived.get("controlling_target_min", 45.0), 1)


        m_prof = getattr(getattr(context.requirements, "mission_result", None), "mission_profile", None)
        target_range_km = round(getattr(m_prof, "mission_range_km", 0.0) if m_prof else 0.0, 1)
        energy_margin_pct = round(derived.get("energy_margin_pct", 0.0), 1)
        min_req_mah = round((required_energy_wh / max(1.0, batt["nominal_voltage_v"] * 0.80)) * 1000.0, 1)

        engine_count = int(derived.get("engine_count", 1))
        per_motor_static_thrust_n = round(derived.get("per_motor_static_thrust_n", derived.get("static_thrust_n", 0.0) / engine_count), 2)
        per_motor_cruise_power_w = round(derived.get("per_motor_cruise_power_w", derived.get("cruise_power_w", 0.0) / engine_count), 1)
        per_motor_max_power_w = round(motor["max_power_w"], 1)
        per_motor_climb_current_a = round(derived.get("per_motor_climb_current_a", derived.get("climb_current_a", 0.0) / engine_count), 2)

        # Retrieve layout from configuration
        cfg_res = getattr(context.requirements, "configuration_result", None)
        prop_layout_val = "Single Tractor"
        if cfg_res and hasattr(cfg_res, "selected_configuration") and isinstance(cfg_res.selected_configuration, dict):
            prop_layout_val = cfg_res.selected_configuration.get("propulsion_layout", "Single Tractor")
        elif hasattr(context.requirements, "preferred_layout") and context.requirements.preferred_layout:
            pref = context.requirements.preferred_layout
            prop_layout_val = pref.value if hasattr(pref, "value") else str(pref)

        battery_technical_spec = {
            "chemistry": {
                "preferred": battery_chemistry,
                "acceptable_alternatives": ["Li-Ion", "LiHV"] if battery_chemistry == "LiPo" else ["LiPo"],
            },
            "cells": {
                "series": batt["cell_count_s"],
                "nominal_voltage_v": round(batt["nominal_voltage_v"], 2),
            },
            "capacity": {
                "selected_mah": batt["capacity_mah"],
                "minimum_required_mah": min_req_mah,
            },
            "energy": {
                "nominal_wh": battery_energy_wh,
                "usable_wh": round(battery_energy_wh * 0.80, 2),
                "required_wh": required_energy_wh,
                "margin_pct": energy_margin_pct,
            },
            "discharge": {
                "continuous_current_a": round(derived.get("climb_current_a", 0.0), 2),
                "cruise_current_a": round(derived.get("cruise_current_a", 0.0), 2),
                "selected_c_rating": battery_c_rating,
                "required_c_rating": required_c_rating,
            },
            "mass": {
                "maximum_kg": round(batt["weight_g"] / 1000.0, 3),
            },
            "compatibility": {
                "motor_voltage_compatible": batt["cell_count_s"] == motor["cell_count_s"],
                "esc_voltage_compatible": True,
                "esc_current_sufficient": esc["continuous_current_a"] >= per_motor_climb_current_a,
            },
        }

        unit_prefix = f"{engine_count}x " if engine_count > 1 else ""
        reasoning = (
            f"Selected optimal propulsion configuration: {unit_prefix}Motor={motor['name']} (KV={motor['kv']:.0f}), "
            f"{unit_prefix}Propeller={prop['name']}, {unit_prefix}ESC={esc['name']}, Battery={batt['name']}. "
            f"Cruise current draw: {derived.get('cruise_current_a', 0.0):.2f} A, "
            f"estimated flight time: {derived.get('estimated_flight_time_min', 0.0):.1f} min, "
            f"total static thrust: {derived.get('static_thrust_n', 0.0):.1f} N. "
            f"Optimization Score: {pos_score:.4f}."
        )

        return PropulsionSpecification(
            motor_name=motor["name"],
            propeller_name=prop["name"],
            esc_name=esc["name"],
            battery_name=batt["name"],
            operating_voltage_v=round(batt["nominal_voltage_v"], 2),
            cruise_current_a=round(derived.get("cruise_current_a", 0.0), 2),
            max_climb_current_a=round(derived.get("climb_current_a", 0.0), 2),
            cell_count_s=batt["cell_count_s"],
            battery_capacity_mah=batt["capacity_mah"],
            battery_weight_g=round(batt["weight_g"], 1),
            total_propulsion_weight_g=round(derived.get("total_propulsion_weight_g", 0.0), 1),
            static_thrust_n=round(derived.get("static_thrust_n", 0.0), 2),
            cruise_thrust_n=round(derived.get("cruise_thrust_n", 0.0), 2),
            cruise_power_w=round(derived.get("cruise_power_w", 0.0), 1),
            takeoff_power_w=round(derived.get("takeoff_power_w", 0.0), 1),
            motor_efficiency=round(derived.get("motor_efficiency", 0.0), 3),
            propeller_efficiency=round(derived.get("propeller_efficiency", 0.0), 3),
            total_efficiency=round(derived.get("total_efficiency", 0.0), 3),
            estimated_flight_time_min=round(derived.get("estimated_flight_time_min", 0.0), 1),
            optimization_score=round(pos_score, 4),
            reasoning=reasoning,
            battery_chemistry=battery_chemistry,
            battery_energy_wh=battery_energy_wh,
            required_energy_wh=required_energy_wh,
            battery_c_rating=battery_c_rating,
            required_c_rating=required_c_rating,
            target_endurance_min=target_endurance_min,
            target_range_km=target_range_km,
            energy_margin_pct=energy_margin_pct,
            battery_technical_spec=battery_technical_spec,
            engine_count=engine_count,
            per_motor_static_thrust_n=per_motor_static_thrust_n,
            per_motor_max_power_w=per_motor_max_power_w,
            per_motor_cruise_power_w=per_motor_cruise_power_w,
            propulsion_layout=prop_layout_val,
            motor_weight_g=310.0,
            esc_weight_g=80.0,
        )
