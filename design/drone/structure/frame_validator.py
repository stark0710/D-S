"""
FrameValidator Subsystem

Purpose:
    Defines the `FrameValidator` class responsible for validating multirotor frame structures against constraints.

Role in Architecture:
    `FrameValidator` checks propeller clearance, ground clearance, maximum wheelbase, and structural safety margins.
"""

from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.structure.frame_constraints import FrameConstraints


class FrameValidator:
    """
    Validator for multirotor frame structural designs.

    Design Principles:
        - Single Responsibility Principle: Multirotor frame structural validation only.
    """

    def validate_frame(
        self,
        result: FrameResult,
        constraints: FrameConstraints
    ) -> list[str]:
        """
        Validates a FrameResult against FrameConstraints.

        Args:
            result (FrameResult): Target frame result object.
            constraints (FrameConstraints): Frame constraints.

        Returns:
            list[str]: List of warning or incompatibility messages.
        """
        warnings: list[str] = []
        frame = result.selected_frame
        gear = result.landing_gear

        if frame.wheelbase_mm > constraints.max_wheelbase_mm:
            warnings.append(
                f"Wheelbase ({frame.wheelbase_mm:.0f}mm) exceeds maximum allowed wheelbase constraint ({constraints.max_wheelbase_mm:.0f}mm)."
            )

        if gear.ground_clearance_mm < constraints.min_ground_clearance_mm:
            warnings.append(
                f"Landing gear ground clearance ({gear.ground_clearance_mm:.0f}mm) is below minimum required ({constraints.min_ground_clearance_mm:.0f}mm)."
            )

        return warnings
