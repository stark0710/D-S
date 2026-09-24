"""
VTOL Wing Sizing Result Subsystem

Purpose:
    Defines the consolidated `WingResult` dataclass outputted by the wing stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.design.vtol.wing.wing_geometry import WingGeometry
from backend.design.vtol.wing.wing_structure import WingStructure
from backend.design.vtol.wing.wing_mounts import MotorMounts
from backend.design.vtol.wing.wing_analysis import WingAnalysis


@dataclass(slots=True)
class WingResult:
    """
    Consolidated wing design result containing geometry, structure, pylon mounts, and analysis.

    Attributes:
        wing_geometry (WingGeometry): Planform shapes and chords.
        wing_structure (WingStructure): Load factors and structural weights.
        motor_mounts (MotorMounts): Placement of motor attachments.
        wing_analysis (WingAnalysis): Lift and transition structural checks.
        engineering_notes (List[str]): Sizing layout observations.
        recommendations (List[str]): Structural suggestions.
        warnings (List[str]): Wing loading or structural margin warnings.
        metadata (Dict[str, Any]): Sizing versions and execution details.
    """

    wing_geometry: WingGeometry
    wing_structure: WingStructure
    motor_mounts: MotorMounts
    wing_analysis: WingAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
