"""
VTOL Airfoil Validator Subsystem

Purpose:
    Defines the `AirfoilValidator` class checking aerodynamic polar bounds,
    spar packaging thicknesses, and transition characteristics.
"""

from typing import List
from backend.design.vtol.airfoil.airfoil_requirements import AirfoilRequirements
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult


class AirfoilValidationError(ValueError):
    """
    Exception raised when VTOL airfoil selections violate safety or moment limits.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class AirfoilValidator:
    """
    Validates selected airfoils for structural and aerodynamic feasibility.
    """

    def validate(self, requirements: AirfoilRequirements, result: AirfoilResult) -> None:
        """
        Validates the airfoil results.

        Args:
            requirements (AirfoilRequirements): Inputs.
            result (AirfoilResult): Outputs.

        Raises:
            AirfoilValidationError: If rules are violated.
        """
        errors: List[str] = []

        if requirements is None:
            raise AirfoilValidationError(["Requirements object is null."])

        # 1. Spar clearance check
        root_chord = requirements.wing_result.wing_geometry.root_chord_m
        t_ratio = result.airfoil_geometry["thickness_ratio"]
        thickness_m = root_chord * t_ratio
        spar_diam_limit_m = 0.015  # 15mm minimum spar support diameter for medium models

        if thickness_m < spar_diam_limit_m:
            errors.append(
                f"Airfoil root thickness ({thickness_m * 1000:.1f} mm) is too thin to structural spar of "
                f"{spar_diam_limit_m * 1000:.1f} mm diameter. Choose a thicker airfoil."
            )

        # 2. Pitching moment check
        cm0 = result.airfoil_geometry["cm0"]
        if cm0 < -0.15:
            errors.append(
                f"Airfoil zero-lift pitching moment ({cm0}) is too nose-down. "
                "This requires excessive horizontal tail stabilizer load."
            )

        # 3. Lift-to-drag check
        ld_ratio = result.polar_analysis.lift_to_drag_ratio_sectional
        if ld_ratio < 10.0:
            errors.append(f"Airfoil sectional L/D ratio ({ld_ratio:.1f}) is below minimum requirement of 10.0.")

        if errors:
            raise AirfoilValidationError(errors)
