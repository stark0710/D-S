"""
VTOL Tail Validator Subsystem

Purpose:
    Defines the `TailValidator` class verifying tail volume coefficients,
    stabilizer spans, and configuration match.
"""

from typing import List
from backend.design.vtol.tail.tail_requirements import TailRequirements
from backend.design.vtol.tail.tail_result import TailResult
from backend.design.vtol.mission.mission_requirements import VTOLType


class TailValidationError(ValueError):
    """
    Exception raised when VTOL tail sizing violates aerodynamic or G loading safety.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class TailValidator:
    """
    Validates selected tail shapes, stabilizers, and boom limits.
    """

    def validate(self, requirements: TailRequirements, result: TailResult) -> None:
        """
        Validates the tail sizing results.

        Args:
            requirements (TailRequirements): Inputs.
            result (TailResult): Sized tail package.

        Raises:
            TailValidationError: If rules are violated.
        """
        errors: List[str] = []

        if requirements is None:
            raise TailValidationError(["Requirements object is null."])

        geom = result.tail_geometry
        vtol_type = requirements.configuration_result.selected_configuration

        # If tailless or tail-sitter, we bypass standard volume checks
        is_tailless = geom.tail_configuration in ("Tailless", "Tail Sitter")

        if not is_tailless:
            # Sized volume checks
            wing_area = requirements.wing_result.wing_geometry.area_m2
            wing_span = requirements.wing_result.wing_geometry.span_m
            root_chord = requirements.wing_result.wing_geometry.root_chord_m
            taper = requirements.wing_result.wing_geometry.taper_ratio
            mac = root_chord * (2.0 / 3.0) * ((1.0 + taper + taper**2) / (1.0 + taper))

            # Horizontal volume check: Vh = Sh * L / (S * MAC)
            if geom.horizontal_area_m2 > 0:
                vh = (geom.horizontal_area_m2 * geom.tail_arm_m) / (wing_area * mac)
                if not (0.25 <= vh <= 1.0):
                    errors.append(f"Horizontal tail volume coefficient Vh ({vh:.3f}) is outside safety range of [0.25, 1.0]")

            # Vertical volume check: Vv = Sv * L / (S * b)
            if geom.vertical_area_m2 > 0:
                vv = (geom.vertical_area_m2 * geom.tail_arm_m) / (wing_area * wing_span)
                if not (0.015 <= vv <= 0.10):
                    errors.append(f"Vertical tail volume coefficient Vv ({vv:.3f}) is outside safety range of [0.015, 0.10]")

            # Width span checks
            if geom.horizontal_span_m > 1.8:
                errors.append(f"Horizontal tail span ({geom.horizontal_span_m:.2f} m) exceeds shipping limit of 1.8m.")

        # Configuration match checks
        if vtol_type == VTOLType.TAIL_SITTER and geom.tail_configuration not in ("Tail Sitter", "Tailless", "Custom"):
            errors.append("Tail Sitter configuration requires a 'Tail Sitter' or 'Tailless' empennage type.")

        if errors:
            raise TailValidationError(errors)
