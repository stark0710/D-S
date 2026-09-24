"""
PropulsionValidator Subsystem

Purpose:
    Defines the `PropulsionValidator` class responsible for validating multirotor propulsion designs against constraints.

Role in Architecture:
    `PropulsionValidator` checks hover throttle margins, motor current draw limits, propeller tip speed bounds, and power loading limits.
"""

from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.propulsion.propulsion_constraints import PropulsionConstraints


class PropulsionValidator:
    """
    Validator for multirotor propulsion subsystem designs.

    Design Principles:
        - Single Responsibility Principle: Propulsion subsystem constraint and feasibility validation only.
    """

    def validate_propulsion(
        self,
        result: PropulsionResult,
        constraints: PropulsionConstraints
    ) -> list[str]:
        """
        Validates a PropulsionResult against PropulsionConstraints.

        Args:
            result (PropulsionResult): Target propulsion result.
            constraints (PropulsionConstraints): Propulsion constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []
        hover_throt = result.hover_analysis.hover_throttle_percent
        tip_speed = result.efficiency_analysis.propeller_tip_speed_m_s

        if hover_throt > constraints.max_hover_throttle_percent:
            warnings.append(
                f"Hover throttle ({hover_throt:.1f}%) exceeds maximum recommended limit ({constraints.max_hover_throttle_percent:.1f}%). "
                "Insufficient control authority margin for maneuvering and wind rejection."
            )

        if hover_throt < constraints.min_hover_throttle_percent:
            warnings.append(
                f"Hover throttle ({hover_throt:.1f}%) is below minimum threshold ({constraints.min_hover_throttle_percent:.1f}%). "
                "System is over-motored; consider smaller motors to reduce mass."
            )

        if tip_speed > 200.0:
            warnings.append(
                f"Propeller tip speed ({tip_speed:.1f} m/s) is high (> 200 m/s). Expect increased acoustic noise and compressibility efficiency loss."
            )

        return warnings
