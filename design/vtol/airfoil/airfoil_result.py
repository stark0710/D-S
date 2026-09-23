"""
VTOL Airfoil Sizing Result Subsystem

Purpose:
    Defines the consolidated `AirfoilResult` dataclass outputted by this stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.design.vtol.airfoil.polar_analysis import PolarAnalysis
from backend.design.vtol.airfoil.transition_analysis import TransitionAnalysis
from backend.design.vtol.airfoil.stall_analysis import StallAnalysis
from backend.design.vtol.airfoil.manufacturing_analysis import ManufacturingAnalysis


@dataclass(slots=True)
class AirfoilResult:
    """
    Consolidated airfoil design result containing polar, transition, stall, and mfg assessments.

    Attributes:
        selected_airfoil (str): Sized airfoil name.
        airfoil_geometry (Dict[str, Any]): Geometric parameters (thickness, camber, leading-edge radius).
        polar_analysis (PolarAnalysis): Sectional drag polars and cruise efficiencies.
        transition_analysis (TransitionAnalysis): Transition flow behaviors.
        stall_analysis (StallAnalysis): Max lift and downwash velocity.
        manufacturing_analysis (ManufacturingAnalysis): Curvature tolerances and spar clearances.
        engineering_notes (List[str]): Sizing observations.
        recommendations (List[str]): Downstream recommendations.
        warnings (List[str]): Aerodynamic or structural safety warnings.
        metadata (Dict[str, Any]): Sizing versions and execution details.
    """

    selected_airfoil: str
    airfoil_geometry: Dict[str, Any]
    polar_analysis: PolarAnalysis
    transition_analysis: TransitionAnalysis
    stall_analysis: StallAnalysis
    manufacturing_analysis: ManufacturingAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
