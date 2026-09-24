"""
Fixed-Wing Airfoil Result Subsystem

Purpose:
    Defines the `AirfoilResult` class representing the output of the airfoil selection process.

Role in Architecture:
    `AirfoilResult` carries selected root/tip airfoils, distribution descriptions, polar curves,
    performance maps, Reynolds analyses, design advice, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.airfoil.polar_analysis import PolarData
from backend.design.fixed_wing.airfoil.performance_map import PerformanceMap
from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysis


@dataclass(slots=True)
class AirfoilResult:
    """
    Consolidated output of the wing airfoil engineering workflow.

    Attributes:
        selected_root_airfoil (str): Selected root section airfoil name.
        selected_tip_airfoil (str): Selected tip section airfoil name.
        airfoil_distribution (str): Lofting layout description between root and tip.
        polar_data (PolarData): Sized cruise lift, drag, and moment coefficient curves.
        performance_map (PerformanceMap): 2D performance map grid across flow regimes.
        reynolds_analysis (ReynoldsAnalysis): Sized flight Reynolds numbers across span.
        engineering_notes (List[str]):Sizing rationale and performance metrics notes.
        recommendations (List[str]): Sizing layout tips.
        warnings (List[str]): Non-fatal warnings about separation bubble risks or moment balances.
        metadata (Dict[str, Any]): Timestamps, version metrics, etc.
    """

    selected_root_airfoil: str
    selected_tip_airfoil: str
    airfoil_distribution: str
    polar_data: PolarData
    performance_map: PerformanceMap
    reynolds_analysis: ReynoldsAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
