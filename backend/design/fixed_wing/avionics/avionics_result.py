"""
Fixed-Wing Avionics Result Subsystem

Purpose:
    Defines the `AvionicsResult` class representing the output of the avionics design process.

Role in Architecture:
    `AvionicsResult` carries selected hardware components, autopilot firmware, GNSS redundancies,
    datalogging sensors, and detailed navigation, communication range, and power analyses.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.avionics.navigation_analysis import NavigationAnalysis
from backend.design.fixed_wing.avionics.communication_analysis import CommunicationAnalysis
from backend.design.fixed_wing.avionics.power_analysis import PowerAnalysis


@dataclass(slots=True)
class AvionicsResult:
    """
    Consolidated output of the flight controllers, receivers, and navigation analysis workflow.

    Attributes:
        selected_flight_controller (str): Sized flight controller name.
        selected_firmware (str): Selected autopilot firmware (ArduPilot, PX4).
        selected_navigation_system (str): Selected GNSS accuracy type (RTK GNSS, Standard).
        selected_receiver (str): Selected RC controller receiver.
        selected_telemetry (str): Selected telemetry data link modem.
        selected_companion_computer (str): Selected companion processor.
        selected_sensors (List[str]): Names of selected airspeed sensors, compasses, or lidars.
        navigation_analysis (NavigationAnalysis): Autopilot redundancy and CPU load estimations.
        communication_analysis (CommunicationAnalysis): Maximum telemetry range and bandwidth budgets.
        power_analysis (PowerAnalysis): Continuous avionics current draw and BEC backups.
        engineering_notes (List[str]): Sizing rationale and component notes.
        recommendations (List[str]): Design integration tips.
        warnings (List[str]): Non-fatal warnings about radio interference or link margins.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    selected_flight_controller: str
    selected_firmware: str
    selected_navigation_system: str
    selected_receiver: str
    selected_telemetry: str
    selected_companion_computer: str
    selected_sensors: List[str] = field(default_factory=list)
    navigation_analysis: NavigationAnalysis = field(default=None)
    communication_analysis: CommunicationAnalysis = field(default=None)
    power_analysis: PowerAnalysis = field(default=None)
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
