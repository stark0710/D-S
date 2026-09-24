"""
PayloadBalanceAnalysis Subsystem

Purpose:
    Defines the `PayloadBalanceAnalysis` class and `PayloadBalanceAnalysisResult` dataclass for Center of Gravity (CG) offset calculations.

Role in Architecture:
    `PayloadBalanceAnalysis` calculates payload CG offsets (X, Y, Z in mm) relative to frame geometric center and resulting pitch/roll moment arms in N*m.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PayloadBalanceAnalysisResult:
    """
    Multirotor payload Center of Gravity (CG) balance analysis output model.

    Attributes:
        cg_offset_x_mm (float): Longitudinal (front/back) CG offset in mm.
        cg_offset_y_mm (float): Lateral (left/right) CG offset in mm.
        cg_offset_z_mm (float): Vertical (downward) CG offset in mm.
        pitch_moment_arm_n_m (float): Unbalanced static pitch moment in N*m.
        roll_moment_arm_n_m (float): Unbalanced static roll moment in N*m.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    cg_offset_x_mm: float
    cg_offset_y_mm: float
    cg_offset_z_mm: float
    pitch_moment_arm_n_m: float
    roll_moment_arm_n_m: float
    metadata: dict[str, Any] = field(default_factory=dict)


class PayloadBalanceAnalysis:
    """
    Analysis service for payload CG offset and static moment arm calculations.

    Design Principles:
        - Single Responsibility Principle: Center of Gravity offset and static balancing moments only.
    """

    def analyze_balance(
        self,
        payload_mass_kg: float,
        offset_x_mm: float = 0.0,
        offset_y_mm: float = 0.0,
        offset_z_mm: float = 120.0
    ) -> PayloadBalanceAnalysisResult:
        """
        Calculates CG offsets and static pitch/roll moments.

        Args:
            payload_mass_kg (float): Payload mass in kg.
            offset_x_mm (float): Longitudinal offset in mm.
            offset_y_mm (float): Lateral offset in mm.
            offset_z_mm (float): Vertical downward offset in mm.

        Returns:
            PayloadBalanceAnalysisResult: Computed balance analysis output.
        """
        g = 9.80665
        weight_n = payload_mass_kg * g

        pitch_moment = weight_n * (offset_x_mm / 1000.0)
        roll_moment = weight_n * (offset_y_mm / 1000.0)

        return PayloadBalanceAnalysisResult(
            cg_offset_x_mm=round(offset_x_mm, 1),
            cg_offset_y_mm=round(offset_y_mm, 1),
            cg_offset_z_mm=round(offset_z_mm, 1),
            pitch_moment_arm_n_m=round(pitch_moment, 3),
            roll_moment_arm_n_m=round(roll_moment, 3)
        )
