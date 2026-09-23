"""
Fixed-Wing Airfoil Validator Subsystem

Purpose:
    Defines the `AirfoilValidator` class to validate selected root and tip airfoils.

Role in Architecture:
    `AirfoilValidator` enforces flow bounds, structural thickness checks,
    and mission suitability limits on root and tip profiles.
"""

from typing import List, Dict, Any
from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements, AirfoilType
from backend.design.fixed_wing.airfoil.airfoil_database import AirfoilRecord
from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysis
from backend.design.fixed_wing.airfoil.airfoil_constraints import AirfoilConstraints


class AirfoilValidationError(ValueError):
    """Exception raised when airfoil selection violates structural or aerodynamic limits."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class AirfoilValidator:
    """
    Validator enforcing aerodynamic and structural compatibility.
    """

    def validate(
        self,
        requirements: AirfoilRequirements,
        constraints: AirfoilConstraints,
        root_airfoil: AirfoilRecord,
        tip_airfoil: AirfoilRecord,
        reynolds: ReynoldsAnalysis,
    ) -> List[str]:
        """
        Validates the chosen root and tip airfoils.

        Args:
            requirements (AirfoilRequirements): Operational requirements context.
            constraints (AirfoilConstraints): Sizing boundaries.
            root_airfoil (AirfoilRecord): Chosen root airfoil.
            tip_airfoil (AirfoilRecord): Chosen tip airfoil.
            reynolds (ReynoldsAnalysis): Sized flow envelope.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            AirfoilValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        mission_profile = requirements.mission_result.mission_profile
        wing_geom = requirements.wing_result.wing_geometry
        category = mission_profile.mission_category.value if hasattr(mission_profile.mission_category, 'value') else str(mission_profile.mission_category)

        # 1. Mission compatibility
        if "Long Endurance" in category:
            if root_airfoil.airfoil_type == AirfoilType.HIGH_LIFT:
                errors.append(
                    f"High-Lift airfoil '{root_airfoil.name}' is incompatible with Long Endurance missions. "
                    "Select a low-drag Laminar Flow or Cambered airfoil."
                )

        # 2. Symmetrical root for Cargo
        if "Cargo" in category:
            if root_airfoil.airfoil_type == AirfoilType.SYMMETRICAL:
                errors.append(
                    f"Symmetrical airfoil '{root_airfoil.name}' cannot be used at root for Cargo missions. "
                    "Select a High-Lift or highly Cambered airfoil."
                )

        # 3. Reynolds number suitability
        # MH 32 (laminar flow) at low Re has separation bubble issues
        if reynolds.re_mean_cruise < 120000.0:
            if root_airfoil.airfoil_type == AirfoilType.LAMINAR_FLOW:
                warnings.append(
                    f"Laminar flow airfoil '{root_airfoil.name}' is operating at a low cruise Reynolds number "
                    f"({reynolds.re_mean_cruise:,.0f}). Risk of high drag from laminar separation bubbles. "
                    "Recommend adding turbulator strips or choosing a standard Clark Y profile."
                )

        # 4. Structural compatibility
        # If wing aspect ratio is high (>= 12.0), the root thickness ratio must be sufficient to support spars
        if wing_geom.aspect_ratio >= 12.0:
            if root_airfoil.thickness_ratio < 0.09:
                errors.append(
                    f"Root airfoil thickness ({root_airfoil.thickness_ratio * 100:.1f}%) is too thin for "
                    f"a high aspect ratio wing (AR = {wing_geom.aspect_ratio:.2f}). "
                    "Select an airfoil with thickness ratio >= 9% to accommodate wing spars."
                )

        # 5. Pitching moment limits
        if abs(root_airfoil.c_m0) > constraints.max_pitching_moment_magnitude:
            errors.append(
                f"Root airfoil zero-lift moment (C_m0 = {root_airfoil.c_m0:.3f}) exceeds the absolute maximum "
                f"constraint limit ({constraints.max_pitching_moment_magnitude})."
            )

        if errors:
            raise AirfoilValidationError(errors)

        return warnings
