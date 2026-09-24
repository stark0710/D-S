"""
Fixed-Wing Fuselage Validator Subsystem

Purpose:
    Defines the `FuselageValidator` class to validate fuselage and compartment packaging.

Role in Architecture:
    `FuselageValidator` checks width boundaries against wing root chord, compartment volumes,
    tail boom mounting contradictions, and packaging densities.
"""

from typing import List
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements, FuselageType
from backend.design.fixed_wing.fuselage.fuselage_constraints import FuselageConstraints
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.fuselage.mounting_interfaces import MountingInterfaces
from backend.design.fixed_wing.fuselage.internal_layout import InternalLayout
from backend.design.fixed_wing.fuselage.fuselage_analysis import FuselageAnalysis


class FuselageValidationError(ValueError):
    """Exception raised when sized fuselage geometry fails packaging constraints."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class FuselageValidator:
    """
    Validator enforcing packaging clearances and layout compatibility boundaries.
    """

    def validate(
        self,
        requirements: FuselageRequirements,
        constraints: FuselageConstraints,
        geometry: FuselageGeometry,
        interfaces: MountingInterfaces,
        layout: InternalLayout,
        analysis: FuselageAnalysis,
    ) -> List[str]:
        """
        Validates the sized fuselage and component placement.

        Args:
            requirements (FuselageRequirements): Sizing requirements context.
            constraints (FuselageConstraints): Geometry bounds.
            geometry (FuselageGeometry): Sized outer geometry.
            interfaces (MountingInterfaces): Sized mounting plates.
            layout (InternalLayout): Sized internal positions.
            analysis (FuselageAnalysis): Packaging evaluations.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            FuselageValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        wing_geom = requirements.wing_result.wing_geometry
        tail_style = requirements.tail_result.tail_configuration

        # 1. Outer bounds checks
        if geometry.length_m <= 0.0:
            errors.append("Sized fuselage length must be positive.")

        # 2. Wing compatibility: Fuselage width vs Wing Root Chord
        if geometry.width_m > wing_geom.root_chord_m:
            errors.append(
                f"Sized fuselage width ({geometry.width_m:.2f} m) exceeds wing root chord ({wing_geom.root_chord_m:.2f} m), "
                "which causes extreme aerodynamic blockage and drag. Select a more slender fuselage profile."
            )

        # 3. Tail compatibility vs Mounting Layout
        if requirements.preferred_fuselage_type == FuselageType.TWIN_BOOM:
            if tail_style != "Twin Boom" and tail_style != "Conventional":
                errors.append(
                    f"Twin Boom fuselage requires Twin Boom or Conventional tail boom structures. "
                    f"Layout contradiction with tail style: {tail_style}."
                )

        # 4. Payload accommodation
        if geometry.payload_bay_volume_m3 < constraints.min_payload_volume_m3:
            errors.append(
                f"Sized payload bay volume ({geometry.payload_bay_volume_m3:.6f} m3) is insufficient to hold the "
                f"minimum required payload compartment volume ({constraints.min_payload_volume_m3:.6f} m3)."
            )

        # 5. Accessibility warning
        if analysis.volume_utilization_ratio > 0.50:
            warnings.append(
                f"High internal volume utilization ({analysis.volume_utilization_ratio * 100:.1f}%). "
                "Component accessibility is restricted, risking heat buildup. Ensure adequate venting duct areas."
            )

        # 6. Cooling path validation
        if "duct" not in layout.cooling_airflow_channel.lower():
            warnings.append("No active air ventilation duct path configured for battery heat dissipations.")

        if errors:
            raise FuselageValidationError(errors)

        return warnings
