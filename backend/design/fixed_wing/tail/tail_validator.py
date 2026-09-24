"""
Fixed-Wing Tail Validator Subsystem

Purpose:
    Defines the `TailValidator` class to validate empennage layouts and control limits.

Role in Architecture:
    `TailValidator` enforces rules checking stabilizer volumes, structural span limits,
    control chord ratios, and configuration compatibility.
"""

from typing import List, Dict, Any
from backend.design.fixed_wing.tail.tail_requirements import TailRequirements, TailConfigType
from backend.design.fixed_wing.tail.tail_constraints import TailConstraints
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail
from backend.design.fixed_wing.tail.control_surface import ControlSurfaces
from backend.design.fixed_wing.tail.tail_analysis import TailAnalysis


class TailValidationError(ValueError):
    """Exception raised when sized tail geometry or stability coefficients violate limits."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class TailValidator:
    """
    Validator to enforce stability, volume coefficient, and layout limits on empennage geometries.
    """

    def validate(
        self,
        requirements: TailRequirements,
        constraints: TailConstraints,
        tail_style: TailConfigType,
        h_tail: HorizontalTail,
        v_tail: VerticalTail,
        control_surfaces: ControlSurfaces,
        analysis: TailAnalysis,
    ) -> List[str]:
        """
        Validates the sized tail configuration.

        Args:
            requirements (TailRequirements): Sizing requirements context.
            constraints (TailConstraints): Sizing bounds.
            tail_style (TailConfigType): Chosen tail style.
            h_tail (HorizontalTail): Sized horizontal tail.
            v_tail (VerticalTail): Sized vertical tail.
            control_surfaces (ControlSurfaces): Sized control surfaces.
            analysis (TailAnalysis): Tail stability volume coefficients.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            TailValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        mission_profile = requirements.mission_result.mission_profile
        wing_geom = requirements.wing_result.wing_geometry
        airfoil_data = requirements.airfoil_result.polar_data
        category = mission_profile.mission_category.value if hasattr(mission_profile.mission_category, 'value') else str(mission_profile.mission_category)

        # 1. Config compatibility
        if tail_style in (TailConfigType.TAILLESS, TailConfigType.FLYING_WING):
            if h_tail.area_m2 > 0.0 or v_tail.area_m2 > 0.0:
                errors.append(
                    f"Tail style is '{tail_style.value}', but horizontal/vertical tail areas are positive. "
                    "Flying wings must have horizontal and vertical areas set to 0.0."
                )
            return warnings  # Tailless has no tail surfaces to validate further

        # 2. Tail Volume coefficients checks
        # Pitch Volume coefficient
        if analysis.horizontal_volume_coefficient < constraints.min_v_h:
            errors.append(
                f"Horizontal tail volume coefficient ({analysis.horizontal_volume_coefficient:.3f}) is below "
                f"minimum constraint limit ({constraints.min_v_h}). Increase tail area or tail arm."
            )
        elif analysis.horizontal_volume_coefficient > constraints.max_v_h:
            errors.append(
                f"Horizontal tail volume coefficient ({analysis.horizontal_volume_coefficient:.3f}) exceeds "
                f"maximum constraint limit ({constraints.max_v_h})."
            )

        # Yaw Volume coefficient
        if analysis.vertical_volume_coefficient < constraints.min_v_v:
            errors.append(
                f"Vertical tail volume coefficient ({analysis.vertical_volume_coefficient:.3f}) is below "
                f"minimum constraint limit ({constraints.min_v_v}). Increase vertical area or tail arm."
            )
        elif analysis.vertical_volume_coefficient > constraints.max_v_v:
            errors.append(
                f"Vertical tail volume coefficient ({analysis.vertical_volume_coefficient:.3f}) exceeds "
                f"maximum constraint limit ({constraints.max_v_v})."
            )

        # 3. Airfoil trim matching control authority
        # High negative pitching moment profile with small horizontal tail
        c_m0 = airfoil_data.pitching_moment_c_m0
        if c_m0 < -0.10 and analysis.horizontal_volume_coefficient < 0.45:
            errors.append(
                f"High-camber root airfoil has pitching moment C_m0 = {c_m0:.3f}, but horizontal tail volume "
                f"coefficient is too low (V_h = {analysis.horizontal_volume_coefficient:.3f}). "
                "Requires V_h >= 0.45 to ensure safe elevator trim authority without stalling the tail."
            )

        # 4. Structural span checks
        # Tail span should not be wider than 60% of wing span
        max_h_span = 0.60 * wing_geom.span_m
        if h_tail.span_m > max_h_span:
            warnings.append(
                f"Horizontal tail span ({h_tail.span_m:.2f} m) is wide relative to wing span ({wing_geom.span_m:.2f} m). "
                f"Tail span exceeds 60% limit ({max_h_span:.2f} m), which may introduce structural bending issues."
            )

        # 5. Mission compatibility
        if "Cargo" in category:
            if analysis.horizontal_volume_coefficient < 0.55:
                warnings.append(
                    f"Low horizontal volume coefficient ({analysis.horizontal_volume_coefficient:.3f}) for Cargo. "
                    "Recommend V_h >= 0.55 to manage large CG offsets from heavy cargo loading."
                )

        if errors:
            raise TailValidationError(errors)

        return warnings
