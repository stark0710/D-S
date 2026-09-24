"""
VTOL Fuselage Requirements Subsystem

Purpose:
    Defines the `FuselageRequirements` class capturing layout design overrides
    and preceding stage outputs for the fuselage sizing stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.wing.wing_result import WingResult
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult
from backend.design.vtol.tail.tail_result import TailResult


@dataclass(slots=True)
class FuselageRequirements:
    """
    Inputs for VTOL fuselage sizing and packaging.

    Attributes:
        mission_result (MissionResult): The result from the mission engineering stage.
        configuration_result (ConfigurationResult): The result from the configuration stage.
        wing_result (WingResult): The result from the wing sizing stage.
        airfoil_result (AirfoilResult): The result from the airfoil sizing stage.
        tail_result (TailResult): The result from the tail sizing stage.
        preferred_fuselage_type (str | None): Preferred fuselage configuration override (e.g. Pod-and-Boom, Monocoque).
        preferred_length_m (float | None): Preferred fuselage length override in meters.
        preferred_width_m (float | None): Preferred fuselage width override in meters.
        preferred_height_m (float | None): Preferred fuselage height override in meters.
        metadata (Dict[str, Any]): Additional override flags or target settings.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    preferred_fuselage_type: str | None = None
    preferred_length_m: float | None = None
    preferred_width_m: float | None = None
    preferred_height_m: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
