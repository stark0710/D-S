"""
AvionicsResult Subsystem

Purpose:
    Defines the `AvionicsResult` domain model representing output from the Drone Avionics Engineering Framework.

Role in Architecture:
    `AvionicsResult` encapsulates selected flight controller, GNSS, receiver, telemetry, camera, companion computer,
    selected auxiliary sensors, `CommunicationAnalysisResult`, navigation analysis dictionary, `AvionicsPowerAnalysisResult`,
    engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.avionics.communication_analysis import CommunicationAnalysisResult
from backend.design.drone.avionics.power_analysis import AvionicsPowerAnalysisResult


@dataclass(slots=True)
class AvionicsResult:
    """
    Multirotor avionics subsystem engineering evaluation output summary.

    Attributes:
        selected_flight_controller (dict[str, Any]): Selected FC specifications dictionary.
        selected_gps (dict[str, Any]): Selected GNSS specifications dictionary.
        selected_receiver (dict[str, Any]): Selected RC receiver specifications dictionary.
        selected_telemetry (dict[str, Any]): Selected telemetry radio specifications dictionary.
        selected_camera (dict[str, Any] | None): Selected camera payload specifications dictionary or None.
        selected_companion_computer (dict[str, Any] | None): Selected companion computer specifications dictionary or None.
        selected_sensors (list[dict[str, Any]]): Selected auxiliary navigation/obstacle sensors list.
        communication_analysis (CommunicationAnalysisResult): Computed RF link range and bandwidth output.
        navigation_analysis (dict[str, Any]): Computed navigation redundancy and precision summary.
        power_analysis (AvionicsPowerAnalysisResult): Computed power draw and mass breakdown output.
        engineering_notes (str): Rationale and engineering notes.
        warnings (list[str]): Diagnostic warnings generated during avionics evaluation.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    selected_flight_controller: dict[str, Any]
    selected_gps: dict[str, Any]
    selected_receiver: dict[str, Any]
    selected_telemetry: dict[str, Any]
    selected_camera: dict[str, Any] | None
    selected_companion_computer: dict[str, Any] | None
    selected_sensors: list[dict[str, Any]]
    communication_analysis: CommunicationAnalysisResult
    navigation_analysis: dict[str, Any]
    power_analysis: AvionicsPowerAnalysisResult
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
