"""
VTOL Fuselage Validator Subsystem

Purpose:
    Defines the `FuselageValidator` checking internal volume packaging feasibility,
    thermal cooling area, and Center of Gravity balancing.
"""

from typing import List
from backend.design.vtol.fuselage.fuselage_requirements import FuselageRequirements
from backend.design.vtol.fuselage.fuselage_result import FuselageResult


class FuselageValidationError(ValueError):
    """
    Exception raised when VTOL fuselage sizing violates volumetric or CG balance safety limits.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class FuselageValidator:
    """
    Validates sized fuselage geometries, packaging efficiency, and static balance.
    """

    def validate(self, requirements: FuselageRequirements, result: FuselageResult) -> None:
        """
        Validates the fuselage results.

        Args:
            requirements (FuselageRequirements): Inputs.
            result (FuselageResult): Outputs.

        Raises:
            FuselageValidationError: If rules are violated.
        """
        errors: List[str] = []

        if requirements is None:
            raise FuselageValidationError(["Requirements object is null."])

        geom = result.fuselage_geometry
        internal = result.internal_layout
        analysis = result.engineering_analysis

        # 1. Length validation
        if not (0.3 <= geom.length_m <= 4.0):
            errors.append(f"Fuselage length must be between 0.3m and 4.0m (got {geom.length_m:.2f} m)")

        # 2. Packaging feasibility validation
        total_sub_volume = sum(p.volume_m3 for p in internal.placements)
        if total_sub_volume > geom.volume_m3 * 0.95:
            errors.append(
                f"Packaging volume failure: subsystem total volume ({total_sub_volume:.5f} m³) "
                f"exceeds maximum packaging limit of 95% of fuselage volume ({geom.volume_m3:.5f} m³)."
            )

        # 3. CG accommodation check
        cg_offset = abs(analysis.cg_offset_from_wing_mac_percent)
        max_offset = requirements.metadata.get("max_cg_offset", 10.0)
        if cg_offset > max_offset:
            errors.append(
                f"Fuselage CG offset ({cg_offset:.1f}%) exceeds maximum allowable static margin travel "
                f"limit of {max_offset:.1f}% from wing MAC aerodynamic center."
            )

        # 4. Cooling adequacy check
        total_inlet_area = sum(inlet.area_cm2 for inlet in result.cooling_layout.inlets)
        if total_inlet_area <= 0.0:
            errors.append("Cooling layout must provide a positive inlet intake area.")

        if errors:
            raise FuselageValidationError(errors)
