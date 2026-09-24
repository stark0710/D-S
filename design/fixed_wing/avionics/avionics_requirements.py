"""
Fixed-Wing Avionics Requirements Subsystem

Purpose:
    Defines the `AvionicsRequirements` class representing input preferences and operational contexts
    for sizing flight controllers, telemetry links, and navigation equipment.

Role in Architecture:
    `AvionicsRequirements` accepts preceding engineering results and allows user selection
    or override of flight controller, firmware, and telemetry options.
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
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult


class AutopilotFirmware(str, Enum):
    """Supported flight controller firmware suites."""
    ARDUPILOT = "ArduPilot"
    PX4 = "PX4"
    CUSTOM = "Custom"


class GNSSConfiguration(str, Enum):
    """Supported GNSS/Navigation layout styles."""
    SINGLE_GNSS = "Single GNSS"
    DUAL_GNSS = "Dual GNSS"
    RTK_GNSS = "RTK GNSS"
    VISUAL_NAV = "Visual Navigation"


@dataclass(slots=True)
class AvionicsRequirements:
    """
    Input model encapsulating preceding engineering results and avionics overrides.

    Attributes:
        mission_result (MissionResult): Output from mission analysis.
        configuration_result (ConfigurationResult): Output from layout selection.
        wing_result (WingResult): Output from wing geometry sizing.
        airfoil_result (AirfoilResult): Output from airfoil selection.
        tail_result (TailResult): Output from tail sizing.
        fuselage_result (FuselageResult): Output from fuselage envelope sizing.
        propulsion_result (PropulsionResult): Output from propulsion sizing.
        electrical_result (Any): Output from electrical/battery sizing (optional).
        preferred_flight_controller (str | None): Optional name of preferred flight controller.
        preferred_firmware (AutopilotFirmware | None): Optional user override for firmware suite.
        metadata (dict[str, Any]): Additional operational overrides.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    fuselage_result: FuselageResult
    propulsion_result: PropulsionResult
    electrical_result: Any = None
    preferred_flight_controller: str | None = None
    preferred_firmware: AutopilotFirmware | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
