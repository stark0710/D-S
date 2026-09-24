from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class IterationRecord:
    """
    Metadata capturing sizing variables state at the end of a design pipeline iteration.
    """
    iteration: int
    mtow_kg: float
    battery_mass_kg: float
    required_thrust_n: float
    available_thrust_n: float
    hover_power_w: float
    hover_throttle_pct: float
    estimated_endurance_min: float
    constraint_status: str
    convergence_error_kg: float


class ConvergenceManager:
    """
    Manages convergence validation and dynamic variable feedback between iterations.
    """
    def __init__(self, tolerance: float = 0.01, max_iterations: int = 15) -> None:
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.history: List[IterationRecord] = []

    def calculate_feedback_payload(
        self,
        actual_payload: float,
        m_batt: float,
        target_hover_time: float
    ) -> float:
        """
        Computes the adjusted payload weight to pass to the motor/propeller sizers.
        This forces the internal battery mass estimator in MotorPerformance to align with
        the actual selected catalog battery mass.
        """
        # Formula derivation:
        # We want: payload_passed + est_batt_mass = actual_payload + m_batt
        # where: est_batt_mass = payload_passed * 1.5 + (target_hover_time / 30.0) * 0.4
        # So: payload_passed * 2.5 + (target_hover_time / 30.0) * 0.4 = actual_payload + m_batt
        # Therefore: payload_passed = (actual_payload + m_batt - (target_hover_time / 30.0) * 0.4) / 2.5
        payload_passed = (actual_payload + m_batt - (target_hover_time / 30.0) * 0.4) / 2.5
        return max(0.01, payload_passed)

    def is_converged(self, prev_record: IterationRecord, current_record: IterationRecord) -> bool:
        """
        Checks whether sizing variables have stabilized within tolerance bounds.
        """
        if not prev_record or not current_record:
            return False
            
        error = abs(current_record.mtow_kg - prev_record.mtow_kg)
        return error <= self.tolerance
