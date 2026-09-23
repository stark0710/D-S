"""
VTOL Report Requirements

Purpose:
    Defines the `ReportRequirements` class capturing layout design overrides
    and preceding stage outputs for the complete reporting stage.
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
from backend.design.vtol.mass_properties.mass_result import MassResult
from backend.design.vtol.hover_performance.hover_result import HoverResult
from backend.design.vtol.transition.transition_result import TransitionResult
from backend.design.vtol.cruise_performance.cruise_result import CruiseResult
from backend.design.vtol.verification.verification_result import VerificationResult
from backend.design.vtol.optimization.optimization_result import OptimizationResult
from backend.design.vtol.cad.cad_result import CADResult
from backend.design.vtol.manufacturing.manufacturing_result import ManufacturingResult

@dataclass(slots=True)
class ReportRequirements:
    """
    Inputs for VTOL complete report generation.
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
    optimization_result: OptimizationResult
    cad_result: CADResult
    manufacturing_result: ManufacturingResult

    preferred_export_format: str | None = None
    document_revision: str = "v1.0"
    author_name: str = "Torq Wings Design Studio"
    metadata: Dict[str, Any] = field(default_factory=dict)
