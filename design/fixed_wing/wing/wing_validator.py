"""
Fixed-Wing Wing Validator Subsystem

Purpose:
    Defines the `WingValidator` class to validate wing geometry outputs.

Role in Architecture:
    Enforces rules checking that sized dimensions comply with structural limits,
    aspect ratio boundaries, wing loading constraints, and configuration layouts.
"""

from typing import List, Dict, Any
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_constraints import WingConstraints


class WingValidationError(ValueError):
    """Exception raised when sized wing geometry fails constraints."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class WingValidator:
    """
    Validator to enforce aerodynamic and structural sanity on sized wing geometry.
    """

    def validate(
        self,
        requirements: WingRequirements,
        constraints: WingConstraints,
        geometry: WingGeometry,
        structural_results: Dict[str, Any],
    ) -> List[str]:
        """
        Validates the sized wing geometry.

        Args:
            requirements (WingRequirements): Sizing requirements context.
            constraints (WingConstraints): Geometry bounds.
            geometry (WingGeometry): Sized wing geometry.
            structural_results (Dict[str, Any]): Structural feasibility checks.

        Returns:
            List[str]: List of non-fatal engineering warnings.

        Raises:
            WingValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        mission_profile = requirements.mission_result.mission_profile
        layout = requirements.configuration_result.selected_configuration
        category = mission_profile.mission_category.value if hasattr(mission_profile.mission_category, 'value') else str(mission_profile.mission_category)

        # 1. Wing Loading limits
        if geometry.wing_loading_kg_m2 < constraints.min_wing_loading_kg_m2:
            errors.append(
                f"Sized wing loading ({geometry.wing_loading_kg_m2:.2f} kg/m2) is below "
                f"minimum constraint limit ({constraints.min_wing_loading_kg_m2} kg/m2)."
            )
        elif geometry.wing_loading_kg_m2 > constraints.max_wing_loading_kg_m2:
            errors.append(
                f"Sized wing loading ({geometry.wing_loading_kg_m2:.2f} kg/m2) exceeds "
                f"maximum constraint limit ({constraints.max_wing_loading_kg_m2} kg/m2)."
            )

        # 2. Aspect Ratio limits
        if geometry.aspect_ratio < constraints.min_aspect_ratio:
            errors.append(
                f"Sized Aspect Ratio ({geometry.aspect_ratio:.2f}) is below "
                f"minimum constraint limit ({constraints.min_aspect_ratio})."
            )
        elif geometry.aspect_ratio > constraints.max_aspect_ratio:
            errors.append(
                f"Sized Aspect Ratio ({geometry.aspect_ratio:.2f}) exceeds "
                f"maximum constraint limit ({constraints.max_aspect_ratio})."
            )

        # 3. Structural feasibility
        if not structural_results.get("is_feasible", True):
            errors.append("Sized wing weight exceeds structural feasibility bounds (limit: 25% of MTOW).")

        # 4. Mission compatibility
        if "Long Endurance" in category:
            if geometry.aspect_ratio < 11.0:
                warnings.append(
                    f"Low Aspect Ratio ({geometry.aspect_ratio:.2f}) is suboptimal for Long Endurance. "
                    "Recommend AR >= 12.0 for higher aerodynamic glide efficiency."
                )
        elif "Cargo" in category:
            if geometry.wing_loading_kg_m2 < 15.0:
                warnings.append(
                    f"Low wing loading ({geometry.wing_loading_kg_m2:.2f} kg/m2) on Cargo mission "
                    "results in excessively large wingspan and structural bending penalties."
                )

        # 5. Configuration compatibility
        tail = layout.get("tail_configuration", "")
        planform = requirements.preferred_planform or PlanformType.TAPERED

        if tail == "Twin Boom":
            if planform in (PlanformType.DELTA, PlanformType.ELLIPTICAL):
                errors.append(
                    f"Planform type '{planform}' is structurally incompatible with Twin Boom tail layouts. "
                    "Select Rectangular, Tapered, or Trapezoidal wing planform."
                )

        gear = layout.get("landing_gear_configuration", "")
        if gear == "Belly Landing":
            if geometry.dihedral_angle_deg < 1.0:
                warnings.append(
                    f"Low dihedral angle ({geometry.dihedral_angle_deg} deg) with Belly Landing "
                    "increases risk of wing tip strike. Recommend dihedral >= 2 degrees."
                )

        if errors:
            raise WingValidationError(errors)

        return warnings
