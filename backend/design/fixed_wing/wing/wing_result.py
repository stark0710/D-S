"""
Fixed-Wing Wing Result Subsystem

Purpose:
    Defines the `WingResult` class representing the output of the wing design and sizing process.

Role in Architecture:
    `WingResult` carries the sized geometry parameters, analysis metrics, recommendations,
    and metadata for downstream sizing (e.g. airfoil selection, tail sizing, CAD generation).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_analysis import WingAnalysis


@dataclass(slots=True)
class WingResult:
    """
    Consolidated output of the wing engineering and sizing workflow.

    Attributes:
        wing_geometry (WingGeometry): Sized dimensions of the wing.
        planform (str): Sized wing planform classification (e.g., "Rectangular", "Tapered").
        reference_area (float): Reference planform area in m2.
        aspect_ratio (float): Sized wing aspect ratio.
        wing_loading (float): Sized wing loading in kg/m2.
        mean_aerodynamic_chord (float): Mean aerodynamic chord length in meters.
        quarter_chord_location (float): Distance from root leading edge to quarter-chord location of MAC.
        analysis (WingAnalysis): Detailed analysis of the wing's aerodynamics and structure.
        engineering_notes (List[str]): Operational notes compiling sizing decisions.
        recommendations (List[str]): Actionable design advice for airfoil and structural layout.
        warnings (List[str]): Warning statements or physical trade-off alerts.
        metadata (Dict[str, Any]): Run timestamps, version numbers, etc.
        estimated_mtow_kg (float | None): Sizing MTOW estimate in kg.
        estimated_wing_weight_kg (float | None): Structural wing weight estimate in kg.
    """

    wing_geometry: WingGeometry
    planform: str
    reference_area: float
    aspect_ratio: float
    wing_loading: float
    mean_aerodynamic_chord: float
    quarter_chord_location: float
    analysis: WingAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    estimated_mtow_kg: float | None = None
    estimated_wing_weight_kg: float | None = None
