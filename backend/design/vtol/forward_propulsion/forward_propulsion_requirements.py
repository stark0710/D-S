"""
VTOL Forward Propulsion Requirements Subsystem

Purpose:
    Defines the `ForwardPropulsionRequirements` class capturing layout design overrides
    and preceding stage outputs for the forward propulsion stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.wing.wing_result import WingResult
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult
from backend.design.vtol.tail.tail_result import TailResult
from backend.design.vtol.fuselage.fuselage_result import FuselageResult
from backend.design.vtol.lift_system.lift_system_result import LiftSystemResult


@dataclass(slots=True)
class ForwardPropulsionRequirements:
    """
    Inputs for VTOL forward propulsion sizing.

    Attributes:
        mission_result (MissionResult): The result from the mission stage.
        configuration_result (ConfigurationResult): The result from the configuration stage.
        wing_result (WingResult): The result from the wing stage.
        airfoil_result (AirfoilResult): The result from the airfoil stage.
        tail_result (TailResult): The result from the tail stage.
        fuselage_result (FuselageResult): The result from the fuselage stage.
        lift_system_result (LiftSystemResult): The result from the lift system stage.
        preferred_cruise_motor (str | None): Preferred motor override.
        preferred_cruise_propeller (str | None): Preferred propeller override.
        preferred_cruise_esc (str | None): Preferred ESC override.
        metadata (Dict[str, Any]): Additional override flags or target settings.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    fuselage_result: FuselageResult
    lift_system_result: LiftSystemResult
    preferred_cruise_motor: str | None = None
    preferred_cruise_propeller: str | None = None
    preferred_cruise_esc: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
