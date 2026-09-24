"""
MassResult Subsystem

Purpose:
    Defines the `MassResult` domain model representing output from the Drone Mass Properties & Center of Gravity Engineering Framework.

Role in Architecture:
    `MassResult` encapsulates total mass in kg, empty mass in kg, payload mass in kg, `MassBreakdown`, `CenterOfGravity`,
    `MomentOfInertia`, `BalanceAnalysisResult`, engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mass_properties.mass_breakdown import MassBreakdown
from backend.design.drone.mass_properties.center_of_gravity import CenterOfGravity
from backend.design.drone.mass_properties.moment_of_inertia import MomentOfInertia
from backend.design.drone.mass_properties.balance_analysis import BalanceAnalysisResult


@dataclass(slots=True)
class MassResult:
    """
    Multirotor mass properties & Center of Gravity engineering output summary.

    Attributes:
        total_mass_kg (float): Total All-Up Weight (AUW) in kg.
        empty_mass_kg (float): Empty aircraft mass in kg.
        payload_mass_kg (float): Payload mass in kg.
        mass_breakdown (MassBreakdown): Detailed subsystem weight breakdown.
        center_of_gravity (CenterOfGravity): 3D Center of Gravity coordinates.
        moment_of_inertia (MomentOfInertia): 3D rotational moments of inertia tensor.
        balance_analysis (BalanceAnalysisResult): Pitch/roll/yaw static balance output.
        engineering_notes (str): Rationale and engineering notes.
        warnings (list[str]): Diagnostic warnings generated during mass analysis.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    total_mass_kg: float
    empty_mass_kg: float
    payload_mass_kg: float
    mass_breakdown: MassBreakdown
    center_of_gravity: CenterOfGravity
    moment_of_inertia: MomentOfInertia
    balance_analysis: BalanceAnalysisResult
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
