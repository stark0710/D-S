"""
Fixed-Wing CAD Sizing Requirements Subsystem

Purpose:
    Defines the `CADRequirements` class representing input sizing contexts for generating CAD geometries.

Role in Architecture:
    `CADRequirements` wraps preceding sizing results and overrides.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult
from backend.design.fixed_wing.avionics.avionics_result import AvionicsResult
from backend.design.fixed_wing.payload.payload_result import PayloadResult
from backend.design.fixed_wing.mass_properties.mass_result import MassResult
from backend.design.fixed_wing.flight_performance.flight_result import FlightResult
from backend.design.fixed_wing.verification.verification_result import VerificationResult


@dataclass(slots=True)
class CADRequirements:
    """
    Input model encapsulating preceding engineering sizing nodes.

    Attributes:
        mission_result (MissionResult): Output from mission analysis.
        configuration_result (ConfigurationResult): Output from layout selection.
        wing_result (WingResult): Output from wing geometry sizing.
        airfoil_result (AirfoilResult): Output from airfoil selection.
        tail_result (TailResult): Output from tail sizing.
        fuselage_result (FuselageResult): Output from fuselage envelope sizing.
        propulsion_result (PropulsionResult): Output from propulsion sizing.
        avionics_result (AvionicsResult): Output from avionics systems selection.
        payload_result (PayloadResult): Output from payload integration.
        mass_result (MassResult): Output from mass properties analysis.
        flight_result (FlightResult): Output from flight performance analysis.
        verification_result (VerificationResult): Output from verification checks.
        electrical_result (Any): Output from electrical/battery sizing (optional).
        optimization_result (Any): Output from optimization loop (optional, default None).
        metadata (dict[str, Any]): Additional overrides.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    fuselage_result: FuselageResult
    propulsion_result: PropulsionResult
    avionics_result: AvionicsResult
    payload_result: PayloadResult
    mass_result: MassResult
    flight_result: FlightResult
    verification_result: VerificationResult
    electrical_result: Any = None
    optimization_result: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
