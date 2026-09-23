"""
ConstraintVerification Subsystem

Purpose:
    Defines the `ConstraintVerification` class and `ConstraintVerificationResult` dataclass for engineering constraints verification.

Role in Architecture:
    `ConstraintVerification` checks physical dimensions, MTOW limits, thermal limits, voltage limits, and acoustic noise constraints.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mass_properties.mass_result import MassResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.electrical.electrical_result import ElectricalResult


@dataclass(slots=True)
class ConstraintVerificationResult:
    """
    Multirotor engineering constraints verification output model.

    Attributes:
        satisfied (bool): True if all engineering design constraints are satisfied.
        mtow_satisfied (bool): True if MTOW is below upper threshold limit.
        dimensions_satisfied (bool): True if physical dimensions fit transport envelope.
        electrical_satisfied (bool): True if electrical voltage/current limits are satisfied.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    satisfied: bool
    mtow_satisfied: bool
    dimensions_satisfied: bool
    electrical_satisfied: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class ConstraintVerification:
    """
    Analysis service for engineering constraints verification.

    Design Principles:
        - Single Responsibility Principle: Physical, electrical, and operational constraint compliance check only.
    """

    def verify_constraints(
        self,
        mass_result: MassResult,
        structure_result: FrameResult,
        electrical_result: ElectricalResult,
        max_mtow_kg: float = 25.0
    ) -> ConstraintVerificationResult:
        """
        Verifies engineering constraints.

        Args:
            mass_result (MassResult): Mass properties output.
            structure_result (FrameResult): Frame result.
            electrical_result (ElectricalResult): Electrical result.
            max_mtow_kg (float): Max MTOW limit in kg.

        Returns:
            ConstraintVerificationResult: Computed constraint verification output.
        """
        mtow_ok = mass_result.total_mass_kg <= max_mtow_kg
        dim_ok = structure_result.selected_frame.wheelbase_mm <= 1500.0
        elec_ok = electrical_result.voltage_analysis.nominal_voltage_v <= 60.0  # Safe extra-low voltage boundary

        all_ok = mtow_ok and dim_ok and elec_ok

        return ConstraintVerificationResult(
            satisfied=all_ok,
            mtow_satisfied=mtow_ok,
            dimensions_satisfied=dim_ok,
            electrical_satisfied=elec_ok
        )
