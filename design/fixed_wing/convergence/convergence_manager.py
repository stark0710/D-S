"""
Fixed-Wing Aircraft Convergence Manager
"""

import time
from typing import Dict, Any, List

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.fixed_wing.convergence.models import ConvergenceTolerances, FinalAircraftSpecification
from backend.design.fixed_wing.convergence.result import AircraftConvergenceResult
from backend.design.fixed_wing.convergence.design_snapshot import create_snapshot, DesignSnapshot
from backend.design.fixed_wing.convergence.convergence_checker import ConvergenceChecker
from backend.design.fixed_wing.convergence.iteration_controller import IterationController


class ConvergenceManager:
    """
    Main manager orchestrating fixed-wing convergence cycles.
    Iteratively executes wing, fuselage, payload, tail, propulsion, electrical,
    mass, CG, and performance design steps until physical convergence occurs.
    """
    def __init__(self, max_iterations: int = 15, tolerances: ConvergenceTolerances | None = None) -> None:
        self.max_iterations = max_iterations
        self.tolerances = tolerances or ConvergenceTolerances()
        self.controller = IterationController()
        self.checker = ConvergenceChecker(self.tolerances)

    def run_convergence(self, context: OptimizationContext) -> AircraftConvergenceResult:
        """Runs the design iteration loop to resolve a self-consistent aircraft design."""
        t0 = time.time()
        history: List[DesignSnapshot] = []
        history_dicts: List[Dict[str, Any]] = []

        # Get MTOW constraint limit from profile
        user_mtow = None
        if context.requirements and context.requirements.mission_result:
            constraints = context.requirements.mission_result.constraints
            user_mtow = getattr(constraints, "maximum_takeoff_weight_kg", None)
            if user_mtow is not None and user_mtow <= 0.0:
                user_mtow = None

        divergence_limit_mtow = user_mtow if user_mtow is not None else 35.0

        # Build initial previous_specifications dict if empty
        if context.previous_specifications is None:
            context.previous_specifications = {}

        status = "Pending"
        reason = "Loop not executed"
        success = False
        final_specs = None
        iterations = 0

        try:
            for iteration in range(1, self.max_iterations + 1):
                iterations = iteration
                
                # Determine current loop MTOW and update profile iteration state
                if iteration == 1:
                    if context.requirements and getattr(context.requirements, "mass_result", None):
                        wb = context.requirements.mass_result.weight_breakdown
                        current_mtow = (
                            wb.structural_weight_kg +
                            wb.propulsion_weight_kg +
                            wb.avionics_weight_kg +
                            wb.payload_weight_kg +
                            wb.battery_fuel_weight_kg
                        )
                    elif context.requirements and context.requirements.mission_result:
                        mp = context.requirements.mission_result.mission_profile
                        current_mtow = getattr(mp, "initial_mtow_seed_kg", 3.10) or 3.10
                    else:
                        current_mtow = 3.10
                else:
                    current_mtow = history[-1].mtow
                
                if context.requirements and context.requirements.mission_result:
                    context.requirements.mission_result.mission_profile.current_iteration_mtow_kg = current_mtow

                # 1. Run full iteration step through all subsystems
                specs = self.controller.run_iteration(context)
                context.previous_specifications.update(specs)

                # 2. Record design snapshot
                snapshot = create_snapshot(iteration, specs)
                history.append(snapshot)
                history_dicts.append(snapshot.to_dict())

                # 3. Check for divergence
                diverged, div_reason = self.checker.check_divergence(history, divergence_limit_mtow)
                if diverged:
                    status = "Diverged"
                    reason = div_reason
                    break

                # 4. Check convergence (comparing with previous iteration snapshot)
                if iteration > 1:
                    if self.checker.check_convergence(history[-2], history[-1]):
                        status = "Converged"
                        reason = f"All variables stabilized below convergence tolerances at iteration {iteration}."
                        success = True
                        break

                # 5. Check for oscillation (non-consecutive repeating state)
                oscillated, osc_reason = self.checker.check_oscillation(history)
                if oscillated:
                    status = "Oscillated"
                    reason = osc_reason
                    break
            else:
                status = "Max Iterations Exceeded"
                reason = f"Failed to converge within {self.max_iterations} iterations."

        except Exception as e:
            status = "Fatal Failure"
            reason = f"Subsystem execution failed with exception: {str(e)}"
            import traceback
            traceback.print_exc()

        # Build FinalAircraftSpecification if successful
        if success and history:
            wing = context.previous_specifications.get("WingPlanformSpecification")
            fuse = context.previous_specifications.get("FuselageSpecification")
            payload = context.previous_specifications.get("PayloadPackagingSpecification")
            tail = context.previous_specifications.get("TailSpecification")
            prop = context.previous_specifications.get("PropulsionSpecification")
            elec = context.previous_specifications.get("ElectricalSystemSpecification")
            mass = context.previous_specifications.get("MassPropertiesSpecification")
            cg = context.previous_specifications.get("CGSpecification")
            perf = context.previous_specifications.get("FlightPerformanceSpecification")

            m_summary = {}
            if context.requirements and context.requirements.mission_result:
                profile = context.requirements.mission_result.mission_profile
                m_summary = {
                    "category": profile.mission_category.value if hasattr(profile.mission_category, 'value') else str(profile.mission_category),
                    "payload_kg": profile.payload_kg,
                    "flight_time_min": profile.flight_time_min,
                    "cruise_speed_kmh": profile.cruise_speed_kmh,
                    "mission_range_km": profile.mission_range_km,
                }

            score = getattr(perf, "performance_score", 0.0) if perf else 0.0

            final_specs = FinalAircraftSpecification(
                mission_summary=m_summary,
                wing_specification=wing,
                fuselage_specification=fuse,
                payload_specification=payload,
                tail_specification=tail,
                propulsion_specification=prop,
                electrical_specification=elec,
                mass_properties_specification=mass,
                cg_specification=cg,
                performance_specification=perf,
                iteration_history=history_dicts,
                convergence_status=status,
                final_design_score=score,
            )

        elapsed = time.time() - t0

        priority = getattr(context, "optimization_priority", None)
        priority_str = priority.value if hasattr(priority, "value") else str(priority) if priority else "BALANCED"

        diagnostics = {
            "iterations_performed": iterations,
            "optimization_priority": priority_str,
            "convergence_variables": [
                "mtow", "wing_area", "wing_loading", "battery_mass",
                "empty_weight", "cg_x", "static_margin", "cruise_power",
                "endurance", "range"
            ],
            "iteration_history": history_dicts,
            "subsystem_updates": {
                "wing": "WingPlanformSpecification",
                "fuselage": "FuselageSpecification",
                "payload": "PayloadPackagingSpecification",
                "tail": "TailSpecification",
                "propulsion": "PropulsionSpecification",
                "electrical": "ElectricalSystemSpecification",
                "mass": "MassPropertiesSpecification",
                "cg": "CGSpecification",
                "performance": "FlightPerformanceSpecification",
            },
            "execution_time_seconds": round(elapsed, 4),
            "convergence_reason": reason,
        }

        return AircraftConvergenceResult(
            success=success,
            message=reason,
            final_specification=final_specs,
            diagnostics=diagnostics,
        )
