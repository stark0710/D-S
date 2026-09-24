"""
Fixed-Wing Payload Requirements Subsystem

Purpose:
    Defines the `PayloadRequirements` class representing input preferences and operational contexts
    for sizing and integrating mission payloads.

Role in Architecture:
    `PayloadRequirements` wraps preceding results and allows user preferences
    for mapping, cargo, or custom sensor payloads.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult
from backend.design.fixed_wing.avionics.avionics_result import AvionicsResult


class PayloadType(str, Enum):
    """Supported mission payload classifications."""
    RGB_CAMERA = "RGB Camera"
    MULTISPECTRAL = "Multispectral Camera"
    HYPERSPECTRAL = "Hyperspectral Camera"
    THERMAL = "Thermal Camera"
    LIDAR = "LiDAR"
    RADAR = "Radar"
    SCIENTIFIC = "Scientific Instruments"
    CARGO = "Cargo"
    RELAY = "Communication Relay"
    ENV_SENSORS = "Environmental Sensors"
    CUSTOM = "Custom Payload"


@dataclass(slots=True)
class PayloadRequirements:
    """
    Input model encapsulating preceding engineering results and payload preferences.

    Attributes:
        mission_result (MissionResult): Output from mission analysis.
        configuration_result (ConfigurationResult): Output from layout selection.
        wing_result (WingResult): Output from wing geometry sizing.
        airfoil_result (AirfoilResult): Output from airfoil selection.
        tail_result (TailResult): Output from tail sizing.
        fuselage_result (FuselageResult): Output from fuselage envelope sizing.
        propulsion_result (PropulsionResult): Output from propulsion sizing.
        avionics_result (AvionicsResult): Output from avionics systems selection.
        electrical_result (Any): Output from electrical/battery sizing (optional).
        preferred_payloads (List[PayloadType] | None): Optional list of preferred payload types.
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
    electrical_result: Any = None
    preferred_payloads: List[PayloadType] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
