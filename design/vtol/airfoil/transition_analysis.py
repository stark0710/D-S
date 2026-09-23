"""
VTOL Airfoil Transition Aerodynamics Subsystem

Purpose:
    Defines the `TransitionAnalysis` class evaluating flow separation,
    high angles of attack, and pitch margins during the transition.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


@dataclass(slots=True)
class TransitionAnalysis:
    """
    Sized performance of the airfoil during the hover-to-cruise transition.

    Attributes:
        transition_aoa_range_deg (Tuple[float, float]): Angle of attack range traversed during transition.
        flow_detachment_angle_deg (float): Angle where boundary layer flow detaches.
        separated_flow_drag_coefficient (float): High angle of attack bluff body drag coefficient.
        pitch_stability_margin_transition (float): Stability reserve under transition pitching moments.
        suitability_rating (str): Qualitative evaluation (e.g. Excellent, Good, Marginal).
        metadata (Dict[str, Any]): Additional transition parameters.
    """

    transition_aoa_range_deg: Tuple[float, float]
    flow_detachment_angle_deg: float
    separated_flow_drag_coefficient: float
    pitch_stability_margin_transition: float
    suitability_rating: str
    metadata: Dict[str, Any] = field(default_factory=dict)
