"""
PayloadResult Subsystem

Purpose:
    Defines the `PayloadResult` domain model representing output from the Drone Payload Integration Engineering Framework.

Role in Architecture:
    `PayloadResult` encapsulates `PayloadProfile`, `PayloadMount`, `PayloadInterface`, `PayloadPowerAnalysisResult`,
    `PayloadBalanceAnalysisResult`, `PayloadVibrationAnalysisResult`, engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.payload.payload_profile import PayloadProfile
from backend.design.drone.payload.payload_mount import PayloadMount
from backend.design.drone.payload.payload_interface import PayloadInterface
from backend.design.drone.payload.payload_power_analysis import PayloadPowerAnalysisResult
from backend.design.drone.payload.payload_balance_analysis import PayloadBalanceAnalysisResult
from backend.design.drone.payload.payload_vibration_analysis import PayloadVibrationAnalysisResult


@dataclass(slots=True)
class PayloadResult:
    """
    Multirotor payload integration engineering output summary.

    Attributes:
        selected_payload (PayloadProfile): Selected payload specification profile.
        mounting_solution (PayloadMount): Mechanical payload mounting solution.
        interface_definition (PayloadInterface): Electrical and data link interface specification.
        power_analysis (PayloadPowerAnalysisResult): Electrical power consumption output.
        balance_analysis (PayloadBalanceAnalysisResult): Center of Gravity offset and moment output.
        vibration_analysis (PayloadVibrationAnalysisResult): Vibration isolation analysis output.
        engineering_notes (str): Rationale and engineering notes.
        warnings (list[str]): Diagnostic warnings generated during payload evaluation.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    selected_payload: PayloadProfile
    mounting_solution: PayloadMount
    interface_definition: PayloadInterface
    power_analysis: PayloadPowerAnalysisResult
    balance_analysis: PayloadBalanceAnalysisResult
    vibration_analysis: PayloadVibrationAnalysisResult
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
