"""
VTOL Optimization Requirements

Purpose:
    Defines the `OptimizationRequirements` class capturing layout design overrides
    and preceding stage outputs for the complete optimization stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.wing.wing_result import WingResult
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult
from backend.design.vtol.tail.tail_result import TailResult
from backend.design.vtol.fuselage.fuselage_result import FuselageResult
from backend.design.vtol.lift_system.lift_system_result import LiftSystemResult
from backend.design.vtol.forward_propulsion.forward_propulsion_result import ForwardPropulsionResult
from backend.design.vtol.electrical.electrical_result import ElectricalResult
from backend.design.vtol.avionics.avionics_result import AvionicsResult
from backend.design.vtol.payload.payload_result import PayloadResult
from backend.design.vtol.mass_properties.mass_result import MassResult
from backend.design.vtol.hover_performance.hover_result import HoverResult
from backend.design.vtol.transition.transition_result import TransitionResult
from backend.design.vtol.cruise_performance.cruise_result import CruiseResult
from backend.design.vtol.verification.verification_result import VerificationResult

@dataclass(slots=True)
class OptimizationRequirements:
    """
    Inputs for VTOL design optimization.
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
    avionics_result: AvionicsResult
    payload_result: PayloadResult
    mass_properties_result: MassResult
    hover_performance_result: HoverResult
    transition_result: TransitionResult
    cruise_performance_result: CruiseResult
    verification_result: VerificationResult

    preferred_optimizer_type: str | None = None
    target_objectives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
