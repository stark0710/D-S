"""
VTOL Configuration Validator Subsystem

Purpose:
    Defines the `ConfigurationValidator` class, verifying architectural layout
    decisions and flight mode completeness.
"""

from typing import List
from backend.design.vtol.configuration.configuration_requirements import ConfigurationRequirements
from backend.design.vtol.mission.mission_requirements import TakeoffMethod, LandingMethod, VTOLType


class ConfigurationValidationError(ValueError):
    """
    Exception raised when VTOL configuration decisions fail validations.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class ConfigurationValidator:
    """
    Validator conducting feasibility audits on the chosen mechanical layout
    and flight configuration settings.
    """

    def validate(self, requirements: ConfigurationRequirements) -> None:
        """
        Validates the configuration requirements.

        Args:
            requirements (ConfigurationRequirements): Sizing inputs.

        Raises:
            ConfigurationValidationError: If any rules are violated.
        """
        errors: List[str] = []

        if requirements is None:
            raise ConfigurationValidationError(["Requirements object is null."])

        mission_res = requirements.mission_result
        if mission_res is None:
            raise ConfigurationValidationError(["MissionResult is missing in configuration requirements."])

        # Get values from requirements or mission result
        vtol_type = requirements.preferred_vtol_type or mission_res.mission_profile.vtol_type
        takeoff = mission_res.hover_requirements.metadata.get("takeoff_method") or TakeoffMethod.VERTICAL
        landing = mission_res.hover_requirements.metadata.get("landing_method") or LandingMethod.VERTICAL

        # Takeoff/Landing VS Layout consistency
        if takeoff == TakeoffMethod.VERTICAL:
            # Sensed as vertical lift layout
            if vtol_type not in (
                VTOLType.QUADPLANE,
                VTOLType.TILT_ROTOR,
                VTOLType.TILT_WING,
                VTOLType.LIFT_CRUISE,
                VTOLType.TAIL_SITTER,
                VTOLType.VECTORED_THRUST,
                VTOLType.TWIN_BOOM_VTOL,
                VTOLType.BOX_WING_VTOL,
                VTOLType.HYBRID_VTOL,
                VTOLType.CUSTOM,
            ):
                errors.append(f"Vertical takeoff is incompatible with layout type: {vtol_type.value}")

        if takeoff in (TakeoffMethod.CATAPULT, TakeoffMethod.HAND_LAUNCH):
            # Requires wings to generate lift
            if vtol_type == VTOLType.CUSTOM:
                # Custom could have wings, but check defaults
                pass

        # Desired motor count validation
        if requirements.desired_motor_count is not None:
            if requirements.desired_motor_count <= 0:
                errors.append(f"Desired motor count must be positive (got {requirements.desired_motor_count})")
            elif requirements.desired_motor_count > 32:
                errors.append(f"Desired motor count exceeds mechanical complexity limit of 32 (got {requirements.desired_motor_count})")

        # Redundancy requirements vs motor counts
        if requirements.redundancy_requirement == "Single Motor Out":
            if requirements.desired_motor_count is not None and requirements.desired_motor_count < 6:
                errors.append(
                    f"Propulsion redundancy 'Single Motor Out' requires at least 6 motors (got {requirements.desired_motor_count})."
                )

        if errors:
            raise ConfigurationValidationError(errors)
