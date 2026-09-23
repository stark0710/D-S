"""
Fixed-Wing Wing Planform Optimization Models

Defines the WingPlanformSpecification class.
"""

from dataclasses import dataclass

@dataclass(slots=True)
class WingPlanformSpecification:
    """
    Standardized specification containing optimal wing geometry output by the optimizer.
    """
    wing_area: float
    aspect_ratio: float
    wing_span: float
    root_chord: float
    tip_chord: float
    mac: float
    taper_ratio: float
    sweep: float
    dihedral: float
    wing_loading: float
    optimization_score: float
    reasoning: str
    estimated_mtow_kg: float | None = None
    estimated_wing_weight_kg: float | None = None
