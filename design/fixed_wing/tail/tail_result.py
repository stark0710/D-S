"""
Fixed-Wing Tail Result Subsystem

Purpose:
    Defines the `TailResult` class representing the output of the tail design and sizing process.

Role in Architecture:
    `TailResult` carries the selected tail style, sized geometry, control surface chords,
    stability ratings, design advice, and warnings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail
from backend.design.fixed_wing.tail.control_surface import ControlSurfaces
from backend.design.fixed_wing.tail.tail_analysis import TailAnalysis


@dataclass(slots=True)
class TailResult:
    """
    Consolidated output of the empennage sizing and control design workflow.

    Attributes:
        tail_configuration (str): Chosen style (e.g. Conventional, V-Tail, Twin Boom).
        horizontal_tail (HorizontalTail): Sized horizontal tail geometry.
        vertical_tail (VerticalTail): Sized vertical tail geometry.
        control_surfaces (ControlSurfaces): Elevator and rudder layout and deflection limits.
        tail_volume_coefficients (Dict[str, float]): Stability volume ratios V_h and V_v.
        tail_analysis (TailAnalysis): Performance, stability, and trim audits.
        engineering_notes (List[str]): Sizing rationale and coefficient metrics notes.
        recommendations (List[str]): Sizing layout tips.
        warnings (List[str]): Sizing warnings or layout mismatch notifications.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    tail_configuration: str
    horizontal_tail: HorizontalTail
    vertical_tail: VerticalTail
    control_surfaces: ControlSurfaces
    tail_volume_coefficients: Dict[str, float]
    tail_analysis: TailAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
