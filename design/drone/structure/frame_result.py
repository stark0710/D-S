"""
FrameResult Subsystem

Purpose:
    Defines the `FrameResult` domain model representing output from the Drone Structural Engineering Framework.

Role in Architecture:
    `FrameResult` encapsulates the `FrameProfile`, dimensional envelope dictionary, `ArmGeometry`,
    `MountingLayout`, `LandingGear`, total structure weight estimate in grams, engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.structure.frame_profile import FrameProfile
from backend.design.drone.structure.arm_geometry import ArmGeometry
from backend.design.drone.structure.landing_gear import LandingGear
from backend.design.drone.structure.mounting_layout import MountingLayout


@dataclass(slots=True)
class FrameResult:
    """
    Multirotor structural engineering output summary.

    Attributes:
        selected_frame (FrameProfile): Selected frame specification profile.
        frame_dimensions (dict[str, float]): Key dimensional envelope dictionary (wheelbase, height, arm_length).
        arm_geometry (ArmGeometry): Detailed arm tube and motor mounting geometry.
        mounting_layout (MountingLayout): Equipment and subsystem mounting layout.
        landing_gear (LandingGear): Selected landing gear specification.
        estimated_structure_weight_g (float): Total structural airframe weight in grams.
        engineering_notes (str): Rationale and structural engineering notes.
        warnings (list[str]): Diagnostic warnings encountered during structural analysis.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    selected_frame: FrameProfile
    frame_dimensions: dict[str, float]
    arm_geometry: ArmGeometry
    mounting_layout: MountingLayout
    landing_gear: LandingGear
    estimated_structure_weight_g: float
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
