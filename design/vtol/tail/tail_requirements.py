"""
VTOL Tail Requirements Subsystem

Purpose:
    Defines the `TailRequirements` class capturing layout design overrides
    and preceding stage outputs for the tail sizing stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.wing.wing_result import WingResult
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult


@dataclass(slots=True)
class TailRequirements:
    """
    Inputs for VTOL tail sizing and stabilization.

    Attributes:
        mission_result (MissionResult): The result from the mission engineering stage.
        configuration_result (ConfigurationResult): The result from the configuration stage.
        wing_result (WingResult): The result from the wing sizing stage.
        airfoil_result (AirfoilResult): The result from the airfoil sizing stage.
        preferred_tail_configuration (str | None): Preferred tail layout override (e.g. V-Tail, Conventional).
        metadata (Dict[str, Any]): Additional override flags or target settings.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    preferred_tail_configuration: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
