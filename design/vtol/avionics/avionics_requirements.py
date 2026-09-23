"""
VTOL Avionics Requirements Subsystem

Purpose:
    Defines the `AvionicsRequirements` class capturing layout design overrides
    and preceding stage outputs for the avionics sizing stage.
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
from backend.design.vtol.forward_propulsion.forward_propulsion_result import ForwardPropulsionResult
from backend.design.vtol.electrical.electrical_result import ElectricalResult

@dataclass(slots=True)
class AvionicsRequirements:
    """
    Inputs for VTOL avionics system and autopilot selection.
    """
    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    fuselage_result: FuselageResult
    lift_system_result: LiftSystemResult
    forward_propulsion_result: ForwardPropulsionResult
    electrical_result: ElectricalResult

    preferred_flight_controller: str | None = None
    preferred_companion_computer: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
