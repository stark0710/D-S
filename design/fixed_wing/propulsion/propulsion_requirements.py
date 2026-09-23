"""
Fixed-Wing Propulsion Requirements Subsystem

Purpose:
    Defines the `PropulsionRequirements` class representing input preferences and operational contexts
    for sizing motors/engines, propellers, and thrust envelopes.

Role in Architecture:
    `PropulsionRequirements` accepts preceding engineering results (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`, `TailResult`, `FuselageResult`)
    and allows user selection or override of propulsion preferences.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult


class PropulsionType(str, Enum):
    """Supported propulsion system classifications."""
    ELECTRIC = "Electric"
    ICE = "Internal Combustion Engine (ICE)"
    HYBRID = "Hybrid Electric"
    FUEL_CELL = "Fuel Cell"
    CUSTOM = "Custom"


class PropulsionLayout(str, Enum):
    """Supported propulsion layout configurations."""
    SINGLE_TRACTOR = "Single Tractor"
    SINGLE_PUSHER = "Single Pusher"
    TWIN_TRACTOR = "Twin Tractor"
    TWIN_PUSHER = "Twin Pusher"
    TWIN_BOOM_PUSHER = "Twin Boom Pusher"
    DISTRIBUTED = "Distributed Propulsion"
    CUSTOM = "Custom"


@dataclass(slots=True)
class PropulsionRequirements:
    """
    Input model encapsulating preceding engineering results and propulsion layout overrides.

    Attributes:
        mission_result (MissionResult): Output from mission analysis.
        configuration_result (ConfigurationResult): Output from layout selection.
        wing_result (WingResult): Output from wing geometry sizing.
        airfoil_result (AirfoilResult): Output from airfoil selection.
        tail_result (TailResult): Output from tail sizing.
        fuselage_result (FuselageResult): Output from fuselage envelope sizing.
        preferred_propulsion_type (PropulsionType | None): Optional user override for motor system style.
        preferred_layout (PropulsionLayout | None): Optional user override for motor placement layout.
        metadata (dict[str, Any]): Additional operational overrides.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    fuselage_result: FuselageResult
    preferred_propulsion_type: PropulsionType | None = None
    preferred_layout: PropulsionLayout | None = None
    flight_performance_result: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
