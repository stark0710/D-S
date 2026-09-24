"""
VTOL Wing Validator Subsystem

Purpose:
    Defines the `WingValidator` class checking sized wing geometries
    and motor mounting clearances.
"""

from typing import List
from backend.design.vtol.wing.wing_requirements import WingRequirements
from backend.design.vtol.wing.wing_geometry import WingGeometry
from backend.design.vtol.wing.wing_mounts import MotorMounts
from backend.design.vtol.mission.mission_requirements import VTOLType


class WingValidationError(ValueError):
    """
    Exception raised when VTOL wing design violates geometric or structural rules.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class WingValidator:
    """
    Validates the sized wing geometry, loading, and structural mounts.
    """

    def validate(self, requirements: WingRequirements, geometry: WingGeometry, mounts: MotorMounts) -> None:
        """
        Validates the wing geometry and mounts.

        Args:
            requirements (WingRequirements): inputs.
            geometry (WingGeometry): Sized geometry.
            mounts (MotorMounts): Placed motor mounts.

        Raises:
            WingValidationError: If rules are violated.
        """
        errors: List[str] = []

        if requirements is None:
            raise WingValidationError(["Requirements object is null."])

        # 1. Geometry validations
        if geometry.span_m <= 0.0:
            errors.append(f"Wingspan must be positive (got {geometry.span_m} m)")
        elif geometry.span_m > 5.5:
            errors.append(f"Wingspan exceeds physical limit of 5.5m (got {geometry.span_m} m)")

        if not (5.0 <= geometry.aspect_ratio <= 18.0):
            errors.append(f"Aspect ratio must be between 5.0 and 18.0 (got {geometry.aspect_ratio})")

        if geometry.root_chord_m <= geometry.tip_chord_m:
            errors.append(
                f"Root chord ({geometry.root_chord_m} m) must be greater than tip chord ({geometry.tip_chord_m} m) to ensure structural span stiffness."
            )

        if not (0.1 <= geometry.taper_ratio <= 1.0):
            errors.append(f"Taper ratio must be between 0.1 and 1.0 (got {geometry.taper_ratio})")

        # 2. Configuration vs Wing Type compatibility
        vtol_type = requirements.configuration_result.selected_configuration
        if vtol_type == VTOLType.TILT_WING and geometry.wing_type != "Tilt Wing":
            errors.append("Tilt Wing configuration requires a 'Tilt Wing' wing architecture.")

        # 3. Mount coordinates vs Wing Span compatibility
        semi_span = geometry.span_m / 2.0
        for mount in mounts.mounts:
            if abs(mount.position_y_m) > semi_span + 0.01:
                errors.append(
                    f"Motor mount '{mount.name}' position Y ({mount.position_y_m} m) is placed beyond the wing tip ({semi_span} m)."
                )

        if errors:
            raise WingValidationError(errors)
