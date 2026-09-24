"""
Fixed-Wing Convergence Checker
"""

from typing import List, Tuple
from backend.design.fixed_wing.convergence.models import ConvergenceTolerances
from backend.design.fixed_wing.convergence.design_snapshot import DesignSnapshot


class ConvergenceChecker:
    """
    Validates iteration snapshots for convergence criteria, divergence, and cycle oscillations.
    """
    def __init__(self, tolerances: ConvergenceTolerances) -> None:
        self.tolerances = tolerances

    def check_convergence(self, snapshot1: DesignSnapshot, snapshot2: DesignSnapshot) -> bool:
        """Returns True if the difference between snapshot1 and snapshot2 is within tolerances."""
        return (
            abs(snapshot1.mtow - snapshot2.mtow) <= self.tolerances.mtow and
            abs(snapshot1.wing_area - snapshot2.wing_area) <= self.tolerances.wing_area and
            abs(snapshot1.wing_loading - snapshot2.wing_loading) <= self.tolerances.wing_loading and
            abs(snapshot1.battery_mass - snapshot2.battery_mass) <= self.tolerances.battery_mass and
            abs(snapshot1.empty_weight - snapshot2.empty_weight) <= self.tolerances.empty_weight and
            abs(snapshot1.cg_x - snapshot2.cg_x) <= self.tolerances.cg_x and
            abs(snapshot1.static_margin - snapshot2.static_margin) <= self.tolerances.static_margin and
            abs(snapshot1.cruise_power - snapshot2.cruise_power) <= self.tolerances.cruise_power and
            abs(snapshot1.endurance - snapshot2.endurance) <= self.tolerances.endurance and
            abs(snapshot1.range - snapshot2.range) <= self.tolerances.range
        )

    def check_divergence(self, history: List[DesignSnapshot], limit_mtow: float) -> Tuple[bool, str]:
        """Returns True and a reason if the design variables are diverging or exceed constraints."""
        if len(history) < 2:
            return False, ""

        latest = history[-1]
        
        # 1. Check MTOW against limit
        if limit_mtow > 0.0 and latest.mtow > limit_mtow:
            return True, f"MTOW {latest.mtow:.2f} kg exceeds mission profile limit of {limit_mtow:.2f} kg."

        # 2. Check MTOW relative growth from initial
        first = history[0]
        if first.mtow > 0.0 and latest.mtow > 2.0 * first.mtow:
            return True, f"MTOW {latest.mtow:.2f} kg has diverged to more than double the initial weight ({first.mtow:.2f} kg)."

        # 3. Check monotonically increasing weight changes over last 3 steps
        if len(history) >= 4:
            errors = []
            for i in range(1, len(history)):
                errors.append(abs(history[i].mtow - history[i-1].mtow))
            if errors[-1] > errors[-2] > errors[-3]:
                return True, (
                    f"Divergence detected: consecutive weight updates are growing larger "
                    f"({errors[-3]:.4f} -> {errors[-2]:.4f} -> {errors[-1]:.4f})."
                )

        return False, ""

    def check_oscillation(self, history: List[DesignSnapshot]) -> Tuple[bool, str]:
        """Returns True and a reason if the snapshot states are repeating/cycling."""
        if len(history) < 3:
            return False, ""

        latest = history[-1]
        
        # Check matching states against any historical steps (excluding immediate predecessor)
        for i in range(len(history) - 2):
            prev = history[i]
            if (
                abs(latest.mtow - prev.mtow) <= self.tolerances.mtow * 0.5 and
                abs(latest.cg_x - prev.cg_x) <= self.tolerances.cg_x * 0.5 and
                abs(latest.wing_area - prev.wing_area) <= self.tolerances.wing_area * 0.5
            ):
                # Ensure it is an actual cycle/oscillation, not monotonic asymptotic convergence
                intermediate_diffs = [history[j].mtow - history[j-1].mtow for j in range(i + 1, len(history))]
                has_sign_change = any(d1 * d2 < -1e-9 for d1, d2 in zip(intermediate_diffs, intermediate_diffs[1:]))
                if has_sign_change:
                    return True, f"Oscillation detected: design state at iteration {latest.iteration} matches state at iteration {prev.iteration}."

        return False, ""
