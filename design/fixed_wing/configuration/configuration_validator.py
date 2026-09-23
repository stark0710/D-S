"""
Fixed-Wing Aircraft Configuration Validator Subsystem

Purpose:
    Defines the `ConfigurationValidator` class, which validates chosen layouts for physical compatibility.

Role in Architecture:
    Enforces rules relating wing position, tail design, propulsion layout, landing gear, and launch/recovery methods
    to prevent physically impossible or highly unsafe configurations.
"""

from typing import List, Dict
from backend.design.fixed_wing.configuration.configuration_requirements import (
    ConfigurationRequirements,
    WingPosition,
    PropulsionLayout,
    TailConfiguration,
    LandingGearConfiguration,
)
from backend.design.fixed_wing.mission.mission_requirements import LaunchMethod, LandingMethod


class ConfigurationValidationError(ValueError):
    """Exception raised when an aircraft configuration fails validation rules."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class ConfigurationValidator:
    """
    Validator to enforce physical consistency and feasibility on selected configurations.
    """

    def validate(self, requirements: ConfigurationRequirements, config: Dict[str, str]) -> List[str]:
        """
        Validates the configuration mapping against mission parameters.

        Args:
            requirements (ConfigurationRequirements): Operational requirements context.
            config (Dict[str, str]): Selected configuration attributes.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            ConfigurationValidationError: If critical incompatibilities are found.
        """
        errors: List[str] = []
        warnings: List[str] = []

        wing = config.get("wing_position")
        prop = config.get("propulsion_layout")
        tail = config.get("tail_configuration")
        gear = config.get("landing_gear_configuration")

        mission_reqs = requirements.mission_result.mission_profile
        payload = mission_reqs.payload_kg
        launch = mission_reqs.launch_method
        landing = mission_reqs.landing_method

        # 1. Landing compatibility & Wing position
        if landing == LandingMethod.BELLY_LANDING:
            if wing == WingPosition.LOW_WING:
                errors.append(
                    "Low Wing configuration is incompatible with Belly Landing. "
                    "Wings will strike the ground, causing structural damage. Select High or Parasol Wing."
                )
            if gear not in (LandingGearConfiguration.BELLY_LANDING, LandingGearConfiguration.SKID):
                warnings.append(
                    f"Landing method is Belly Landing, but landing gear is set to {gear}. "
                    "Recommend setting landing gear to Belly Landing or Skid."
                )

        # 2. Runway landing vs Landing Gear
        if landing == LandingMethod.RUNWAY:
            if gear in (LandingGearConfiguration.BELLY_LANDING, LandingGearConfiguration.SKID):
                errors.append(
                    f"Landing gear {gear} is incompatible with Runway landing. "
                    "Select Tricycle or Taildragger landing gear."
                )

        # 3. Launch compatibility
        if launch == LaunchMethod.HAND_LAUNCH:
            if payload > 5.0:
                errors.append(
                    f"Hand launch is physically unfeasible for aircraft with payload of {payload} kg. "
                    "Select Catapult or Runway launch."
                )
            if prop == PropulsionLayout.TRACTOR:
                warnings.append(
                    "Tractor propulsion with Hand Launch carries risk of propeller strike. "
                    "Ensure adequate grip area and throttle delay are configured."
                )

        # 4. Tail & Propulsion consistency
        if tail in (TailConfiguration.TAILLESS, TailConfiguration.FLYING_WING):
            if tail != TailConfiguration.FLYING_WING and wing == WingPosition.PARASOL_WING:
                errors.append("Parasol wings are structurally incompatible with Tailless designs.")
            
            # Flying wings / tailless don't have separate tail configuration, verify
            if tail == TailConfiguration.FLYING_WING and wing != WingPosition.MID_WING and wing != WingPosition.HIGH_WING:
                warnings.append("Flying wing configuration is highly recommended to use Mid or High Wing position.")

        if tail == TailConfiguration.TWIN_BOOM:
            if prop not in (PropulsionLayout.PUSHER, PropulsionLayout.TWIN_BOOM_PUSHER, PropulsionLayout.TWIN_Pusher if hasattr(PropulsionLayout, 'TWIN_Pusher') else PropulsionLayout.TWIN_PUSHER):
                warnings.append(
                    f"Twin Boom tail usually requires Pusher, Twin Pusher, or Twin Boom Pusher propulsion layouts. "
                    f"Currently using {prop}."
                )

        # 5. Payload compatibility
        if payload > 15.0:
            if wing == WingPosition.PARASOL_WING:
                errors.append(
                    f"Parasol wing structures are structurally inefficient for heavy payloads of {payload} kg. "
                    "Select High Wing or Mid Wing."
                )
            if prop == PropulsionLayout.TRACTOR:
                warnings.append(
                    "Heavy payload designs benefit from twin-propeller layouts (Twin Tractor) "
                    "to distribute torque and thrust loads."
                )

        # 6. Landing gear consistency
        if gear == LandingGearConfiguration.RETRACTABLE:
            if landing == LandingMethod.PARACHUTE:
                warnings.append("Retractable landing gear adds unnecessary cost/weight if landing via parachute.")

        if errors:
            raise ConfigurationValidationError(errors)

        return warnings
