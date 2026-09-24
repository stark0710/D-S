"""
ThrustAnalysis Subsystem

Purpose:
    Defines the `ThrustAnalysis` class and `ThrustAnalysisResult` dataclass for multirotor thrust calculations.

Role in Architecture:
    `ThrustAnalysis` calculates total hover thrust, total maximum thrust, thrust-to-weight ratio,
    and individual motor thrust requirements.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ThrustAnalysisResult:
    """
    Multirotor thrust analysis output model.

    Attributes:
        total_hover_thrust_kg (float): Required total hover thrust in kg (equals AUW mass).
        total_max_thrust_kg (float): Maximum available total thrust across all motors in kg.
        actual_thrust_to_weight_ratio (float): Calculated thrust-to-weight ratio (Total Max Thrust / AUW).
        hover_thrust_per_motor_g (float): Individual motor hover thrust requirement in grams.
        max_thrust_per_motor_g (float): Individual motor maximum thrust capability in grams.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    total_hover_thrust_kg: float
    total_max_thrust_kg: float
    actual_thrust_to_weight_ratio: float
    hover_thrust_per_motor_g: float
    max_thrust_per_motor_g: float
    metadata: dict[str, Any] = field(default_factory=dict)


class ThrustAnalysis:
    """
    Analysis service for multirotor thrust calculations.

    Design Principles:
        - Single Responsibility Principle: Thrust calculation physics only.
    """

    def analyze_thrust(
        self,
        auw_kg: float,
        rotor_count: int,
        target_tw_ratio: float = 2.0,
        coaxial: bool = False
    ) -> ThrustAnalysisResult:
        """
        Calculates hover thrust, maximum thrust requirement, and T/W ratio.

        Args:
            auw_kg (float): All-Up Weight mass in kg.
            rotor_count (int): Total rotor count.
            target_tw_ratio (float): Target thrust-to-weight ratio.
            coaxial (bool): True if coaxial rotor configuration.

        Returns:
            ThrustAnalysisResult: Computed thrust analysis results.
        """
        # Coaxial inflow loss factor ~12-15%
        coaxial_factor = 0.86 if coaxial else 1.0

        hover_thrust_total_kg = auw_kg
        hover_thrust_per_motor_g = round((auw_kg * 1000.0) / (rotor_count * coaxial_factor), 1)

        max_thrust_total_kg = auw_kg * target_tw_ratio
        max_thrust_per_motor_g = round((max_thrust_total_kg * 1000.0) / (rotor_count * coaxial_factor), 1)

        actual_tw = round((max_thrust_per_motor_g * rotor_count * coaxial_factor / 1000.0) / auw_kg, 2)

        return ThrustAnalysisResult(
            total_hover_thrust_kg=hover_thrust_total_kg,
            total_max_thrust_kg=max_thrust_total_kg,
            actual_thrust_to_weight_ratio=actual_tw,
            hover_thrust_per_motor_g=hover_thrust_per_motor_g,
            max_thrust_per_motor_g=max_thrust_per_motor_g
        )
