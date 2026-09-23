"""
VTOL Airfoil Requirements Subsystem

Purpose:
    Defines the `AirfoilRequirements` class capturing layout design overrides
    and preceding stage outputs for the airfoil stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.wing.wing_result import WingResult


@dataclass(slots=True)
class AirfoilRequirements:
    """
    Inputs for VTOL airfoil selection and characterization.

    Attributes:
        mission_result (MissionResult): The result from the mission engineering stage.
        configuration_result (ConfigurationResult): The result from the configuration stage.
        wing_result (WingResult): The result from the wing geometry sizing stage.
        preferred_airfoil_name (str | None): Preferred airfoil model name override (e.g. Clark Y).
        metadata (Dict[str, Any]): Additional override flags or target settings.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    preferred_airfoil_name: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
