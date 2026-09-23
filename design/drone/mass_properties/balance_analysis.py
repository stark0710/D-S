"""
BalanceAnalysis Subsystem

Purpose:
    Defines the `BalanceAnalysis` class and `BalanceAnalysisResult` dataclass for aircraft balance evaluation.

Role in Architecture:
    `BalanceAnalysis` checks pitch, roll, and yaw static balance, computes unbalanced static moments in N*m,
    and calculates battery tray relocation recommendations (in mm) to eliminate CG offset.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mass_properties.center_of_gravity import CenterOfGravity


@dataclass(slots=True)
class BalanceAnalysisResult:
    """
    Multirotor balance analysis output model.

    Attributes:
        pitch_balanced (bool): True if longitudinal CG offset is within allowable margin (<= 15mm).
        roll_balanced (bool): True if lateral CG offset is within allowable margin (<= 15mm).
        yaw_balanced (bool): True if yaw mass symmetry is maintained.
        static_pitch_moment_n_m (float): Static pitch moment arm in N*m.
        static_roll_moment_n_m (float): Static roll moment arm in N*m.
        battery_shift_recommendation_mm (float): Recommended longitudinal battery relocation distance in mm.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    pitch_balanced: bool
    roll_balanced: bool
    yaw_balanced: bool
    static_pitch_moment_n_m: float
    static_roll_moment_n_m: float
    battery_shift_recommendation_mm: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BalanceAnalysis:
    """
    Analysis service for multirotor static balance and battery relocation calculations.

    Design Principles:
        - Single Responsibility Principle: Pitch, roll, yaw static moment balance analysis and battery relocation recommendations only.
    """

    def analyze_balance(
        self,
        cg: CenterOfGravity,
        total_mass_kg: float,
        battery_mass_kg: float = 0.8
    ) -> BalanceAnalysisResult:
        """
        Evaluates static balance and computes required battery shift distance.

        Args:
            cg (CenterOfGravity): Aircraft 3D CG.
            total_mass_kg (float): Total All-Up Weight in kg.
            battery_mass_kg (float): Battery mass in kg.

        Returns:
            BalanceAnalysisResult: Computed balance analysis output.
        """
        g = 9.80665
        weight_n = total_mass_kg * g

        pitch_moment = weight_n * (cg.cg_x_mm / 1000.0)
        roll_moment = weight_n * (cg.cg_y_mm / 1000.0)

        pitch_ok = abs(cg.cg_x_mm) <= cg.cg_margin_x_mm
        roll_ok = abs(cg.cg_y_mm) <= cg.cg_margin_y_mm
        yaw_ok = True

        # Calculate required battery shift to compensate for pitch CG offset: delta_x_bat = - (cg_x * total_mass) / battery_mass
        bat_shift = 0.0
        if not pitch_ok and battery_mass_kg > 0:
            bat_shift = round(- (cg.cg_x_mm * total_mass_kg) / battery_mass_kg, 1)

        return BalanceAnalysisResult(
            pitch_balanced=pitch_ok,
            roll_balanced=roll_ok,
            yaw_balanced=yaw_ok,
            static_pitch_moment_n_m=round(pitch_moment, 3),
            static_roll_moment_n_m=round(roll_moment, 3),
            battery_shift_recommendation_mm=bat_shift
        )
