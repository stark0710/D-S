"""
ElectricalResult Subsystem

Purpose:
    Defines the `ElectricalResult` domain model representing output from the Drone Electrical Power Engineering Framework.

Role in Architecture:
    `ElectricalResult` encapsulates selected battery, ESCs, PDB, BEC, connectors, wiring, `PowerBudget`,
    `CurrentAnalysisResult`, `VoltageAnalysisResult`, efficiency analysis dictionary, estimated endurance in minutes,
    engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.electrical.power_budget import PowerBudget
from backend.design.drone.electrical.current_analysis import CurrentAnalysisResult
from backend.design.drone.electrical.voltage_analysis import VoltageAnalysisResult


@dataclass(slots=True)
class ElectricalResult:
    """
    Multirotor electrical subsystem engineering evaluation output summary.

    Attributes:
        selected_battery (dict[str, Any]): Battery pack specifications dictionary.
        selected_escs (dict[str, Any]): ESC specifications dictionary.
        selected_pdb (dict[str, Any]): PDB specifications dictionary.
        selected_bec (dict[str, Any]): BEC voltage regulator specifications dictionary.
        selected_connectors (dict[str, Any]): Power connector specifications dictionary.
        selected_wiring (dict[str, Any]): Wiring gauge specifications dictionary.
        power_budget (PowerBudget): Detailed system power budget breakdown.
        current_analysis (CurrentAnalysisResult): Electrical current draw analysis output.
        voltage_analysis (VoltageAnalysisResult): Voltage thresholds and voltage drop output.
        efficiency_analysis (dict[str, float]): Electrical losses dictionary.
        estimated_endurance_min (float): Estimated hover flight endurance in minutes.
        engineering_notes (str): Rationale and engineering notes.
        warnings (list[str]): Diagnostic warnings generated during electrical evaluation.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    selected_battery: dict[str, Any]
    selected_escs: dict[str, Any]
    selected_pdb: dict[str, Any]
    selected_bec: dict[str, Any]
    selected_connectors: dict[str, Any]
    selected_wiring: dict[str, Any]
    power_budget: PowerBudget
    current_analysis: CurrentAnalysisResult
    voltage_analysis: VoltageAnalysisResult
    efficiency_analysis: dict[str, float]
    estimated_endurance_min: float
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
