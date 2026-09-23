"""
PropulsionResult Subsystem

Purpose:
    Defines the `PropulsionResult` domain model representing output from the Drone Propulsion Engineering Framework.

Role in Architecture:
    `PropulsionResult` encapsulates selected motors dictionary, selected propellers dictionary, `ThrustAnalysisResult`,
    `PowerAnalysisResult`, `EfficiencyAnalysisResult`, `HoverAnalysisResult`, engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.propulsion.thrust_analysis import ThrustAnalysisResult
from backend.design.drone.propulsion.power_analysis import PowerAnalysisResult
from backend.design.drone.propulsion.hover_analysis import HoverAnalysisResult
from backend.design.drone.propulsion.efficiency_analysis import EfficiencyAnalysisResult


@dataclass(slots=True)
class PropulsionResult:
    """
    Multirotor propulsion engineering output summary.

    Attributes:
        selected_motors (dict[str, Any]): Selected motor parameters dictionary.
        selected_propellers (dict[str, Any]): Selected propeller parameters dictionary.
        thrust_analysis (ThrustAnalysisResult): Computed thrust analysis result.
        power_analysis (PowerAnalysisResult): Computed electrical power analysis result.
        efficiency_analysis (EfficiencyAnalysisResult): Computed propulsion efficiency result.
        hover_analysis (HoverAnalysisResult): Computed hover performance result.
        engineering_notes (str): Rationale and engineering notes.
        warnings (list[str]): Diagnostic warnings encountered during propulsion evaluation.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    selected_motors: dict[str, Any]
    selected_propellers: dict[str, Any]
    thrust_analysis: ThrustAnalysisResult
    power_analysis: PowerAnalysisResult
    efficiency_analysis: EfficiencyAnalysisResult
    hover_analysis: HoverAnalysisResult
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
