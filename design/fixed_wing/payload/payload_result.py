"""
Fixed-Wing Payload Result Subsystem

Purpose:
    Defines the `PayloadResult` class representing the output of the payload design process.

Role in Architecture:
    `PayloadResult` carries selected cameras/cargo, physical layouts, mounts, power/data ports,
    cooling vents, and CG analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.payload.payload_layout import PayloadLayout
from backend.design.fixed_wing.payload.payload_mount import PayloadMount
from backend.design.fixed_wing.payload.payload_power import PayloadPowerInterface
from backend.design.fixed_wing.payload.payload_data import PayloadDataInterface
from backend.design.fixed_wing.payload.payload_cooling import PayloadCooling
from backend.design.fixed_wing.payload.payload_analysis import PayloadAnalysis


@dataclass(slots=True)
class PayloadResult:
    """
    Consolidated output of the mission equipment packaging and balancing workflow.

    Attributes:
        selected_payloads (List[str]): Names of selected payload components.
        payload_layout (PayloadLayout): Coordinates and orientations.
        payload_mounts (List[PayloadMount]): Gimbal structure and vibration details.
        power_interfaces (List[PayloadPowerInterface]): Sized BEC supplies.
        communication_interfaces (List[PayloadDataInterface]): Shutter trigger pins and rates.
        cooling_requirements (PayloadCooling): Thermal airflow vents dimensions.
        payload_analysis (PayloadAnalysis): CG offset and static margin calculations.
        engineering_notes (List[str]): Sizing rationale notes.
        recommendations (List[str]): Integration installation tips.
        warnings (List[str]): Non-fatal warnings about weight margins or CG offsets.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    selected_payloads: List[str]
    payload_layout: PayloadLayout
    payload_mounts: List[PayloadMount]
    power_interfaces: List[PayloadPowerInterface]
    communication_interfaces: List[PayloadDataInterface]
    cooling_requirements: PayloadCooling
    payload_analysis: PayloadAnalysis
    requested_payload_mass_kg: float = 0.0
    installed_payload_mass_kg: float = 0.0
    payload_design_margin_kg: float = 0.0
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
"""
Fixed-Wing Payload Result model.
"""
