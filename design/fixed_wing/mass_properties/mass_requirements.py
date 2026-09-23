"""
Fixed-Wing Mass Properties Requirements Subsystem

Purpose:
    Defines the `MassRequirements` class representing input preferences and operational contexts
    for sizing mass budgets, CG targets, and moments of inertia.

Role in Architecture:
    `MassRequirements` wraps preceding results and allows optional structural mass overrides.
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


@dataclass(slots=True)
class MassRequirements:
    """
    Input model encapsulating preceding engineering results and mass property overrides.

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
        electrical_result (Any): Output from electrical/battery sizing (optional).
        structural_mass_override_kg (float | None): Optional user override for empty structural weight.
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
    electrical_result: Any = None
    structural_mass_override_kg: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
