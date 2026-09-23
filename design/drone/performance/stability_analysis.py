"""
StabilityAnalysis Subsystem

Purpose:
    Defines the `StabilityAnalysis` class and `StabilityAnalysisResult` dataclass for control authority and stability evaluation.

Role in Architecture:
    `StabilityAnalysis` evaluates control authority margins across pitch, roll, and yaw control axes.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class StabilityAnalysisResult:
    """
    Multirotor flight control stability analysis output model.

    Attributes:
        pitch_control_authority (float): Pitch axis control authority rating (0.0 to 1.0).
        roll_control_authority (float): Roll axis control authority rating (0.0 to 1.0).
        yaw_control_authority (float): Yaw axis control authority rating (0.0 to 1.0).
        control_margin_percent (float): Control power margin percentage (ideal >= 30%).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    pitch_control_authority: float
    roll_control_authority: float
    yaw_control_authority: float
    control_margin_percent: float
    metadata: dict[str, Any] = field(default_factory=dict)


class StabilityAnalysis:
    """
    Analysis service for multirotor flight control authority and stability margins.

    Design Principles:
        - Single Responsibility Principle: Pitch, roll, and yaw control power margin evaluation only.
    """

    def analyze_stability(
        self,
        actual_tw_ratio: float,
        cg_offset_x_mm: float,
        cg_offset_y_mm: float
    ) -> StabilityAnalysisResult:
        """
        Calculates control authority ratings and control margin percentage.

        Args:
            actual_tw_ratio (float): T/W ratio.
            cg_offset_x_mm (float): Longitudinal CG offset in mm.
            cg_offset_y_mm (float): Lateral CG offset in mm.

        Returns:
            StabilityAnalysisResult: Computed stability analysis output.
        """
        # Base control authority from T/W ratio
        base_auth = min(1.0, actual_tw_ratio / 2.0)

        # CG offsets degrade control authority in affected direction
        pitch_auth = round(max(0.2, base_auth - (abs(cg_offset_x_mm) / 100.0)), 2)
        roll_auth = round(max(0.2, base_auth - (abs(cg_offset_y_mm) / 100.0)), 2)
        yaw_auth = round(base_auth * 0.85, 2)

        control_margin = round(max(0.0, (actual_tw_ratio - 1.0) / actual_tw_ratio * 100.0), 1)

        return StabilityAnalysisResult(
            pitch_control_authority=pitch_auth,
            roll_control_authority=roll_auth,
            yaw_control_authority=yaw_auth,
            control_margin_percent=control_margin
        )
