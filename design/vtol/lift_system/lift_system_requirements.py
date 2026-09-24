"""
VTOL Lift System Requirements Subsystem

Purpose:
    Defines the `LiftSystemRequirements` class capturing layout design overrides
    and preceding stage outputs for the lift system stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.wing.wing_result import WingResult
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult
from backend.design.vtol.tail.tail_result import TailResult
from backend.design.vtol.fuselage.fuselage_result import FuselageResult


@dataclass(slots=True)
class LiftSystemRequirements:
    """
    Inputs for VTOL vertical lift system sizing.

    Attributes:
        mission_result (MissionResult): The result from the mission stage.
        configuration_result (ConfigurationResult): The result from the configuration stage.
        wing_result (WingResult): The result from the wing sizing stage.
        airfoil_result (AirfoilResult): The result from the airfoil sizing stage.
        tail_result (TailResult): The result from the tail sizing stage.
        fuselage_result (FuselageResult): The result from the fuselage sizing stage.
        preferred_motor_model (str | None): Preferred motor model override (e.g. MN6007).
        preferred_propeller_model (str | None): Preferred propeller model override (e.g. 22x7.2).
        metadata (Dict[str, Any]): Additional override flags or target settings.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    fuselage_result: FuselageResult
    preferred_motor_model: str | None = None
    preferred_propeller_model: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
