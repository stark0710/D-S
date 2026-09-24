"""
VTOL Mass Properties Requirements

Purpose:
    Defines the `MassRequirements` class capturing layout design overrides
    and preceding stage outputs for the mass properties sizing stage.
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
from backend.design.vtol.avionics.avionics_result import AvionicsResult
from backend.design.vtol.payload.payload_result import PayloadResult

@dataclass(slots=True)
class MassRequirements:
    """
    Inputs for VTOL mass properties evaluation.
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

    preferred_empty_mass_fraction: float | None = None
    preferred_weight_growth_margin: float | None = None
    fixed_wing_subsystems: Any | None = None
    convergence_tolerance_kg: float = 0.015
    max_iterations: int = 20
    relaxation_alpha: float = 0.70
    specific_energy_wh_kg: float | None = None
    initial_mass_guess_kg: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
