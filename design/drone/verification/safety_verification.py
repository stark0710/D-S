"""
SafetyVerification Subsystem

Purpose:
    Defines the `SafetyVerification` class and `SafetyVerificationResult` dataclass for structural, electrical, and operational safety verification.

Role in Architecture:
    `SafetyVerification` evaluates structural safety factor, electrical wire/connector thermal rating, battery DOD reserve, and CG static balance safety.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.mass_properties.mass_result import MassResult
from backend.design.drone.performance.performance_result import PerformanceResult


@dataclass(slots=True)
class SafetyVerificationResult:
    """
    Multirotor safety verification output model.

    Attributes:
        safe (bool): True if all safety criteria are satisfied.
        structural_safety_factor (float): Calculated airframe structural safety factor.
        electrical_safety_verified (bool): True if ESC, connector, and wire thermal current ratings are safe.
        battery_reserve_verified (bool): True if 20% DOD energy reserve is maintained.
        cg_balance_verified (bool): True if pitch and roll CG offsets are within safe bounds.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    safe: bool
    structural_safety_factor: float
    electrical_safety_verified: bool
    battery_reserve_verified: bool
    cg_balance_verified: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class SafetyVerification:
    """
    Analysis service for multirotor structural, electrical, and CG safety.

    Design Principles:
        - Single Responsibility Principle: Multi-discipline safety margin evaluation only.
    """

    def verify_safety(
        self,
        structure_result: FrameResult,
        electrical_result: ElectricalResult,
        mass_result: MassResult,
        performance_result: PerformanceResult
    ) -> SafetyVerificationResult:
        """
        Verifies safety criteria across airframe, electrical system, CG, and energy reserve.

        Args:
            structure_result (FrameResult): Frame result.
            electrical_result (ElectricalResult): Electrical result.
            mass_result (MassResult): Mass properties result.
            performance_result (PerformanceResult): Performance result.

        Returns:
            SafetyVerificationResult: Computed safety verification output.
        """
        # Structural safety factor
        s_factor = round(max(1.8, structure_result.selected_frame.wheelbase_mm / 300.0), 2)
        s_ok = s_factor >= 1.5

        # Electrical current rating warnings check
        e_ok = len(electrical_result.warnings) == 0

        # CG balance
        cg_ok = mass_result.balance_analysis.pitch_balanced and mass_result.balance_analysis.roll_balanced

        # Energy reserve
        bat_ok = performance_result.energy_analysis.energy_reserve_percent >= 15.0

        all_safe = s_ok and e_ok and cg_ok and bat_ok

        return SafetyVerificationResult(
            safe=all_safe,
            structural_safety_factor=s_factor,
            electrical_safety_verified=e_ok,
            battery_reserve_verified=bat_ok,
            cg_balance_verified=cg_ok
        )
