"""
VTOL Airfoil Manufacturing Analysis Subsystem

Purpose:
    Defines the `ManufacturingAnalysis` class evaluating trailing edge limits,
    mold releases, and spar packing dimensions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ManufacturingAnalysis:
    """
    Sized manufacturing trade-off checks for the selected airfoil.

    Attributes:
        foam_cut_feasibility_score (float): Rating of suitability for hot-wire foam cutting (0.0 to 100.0).
        mold_release_feasibility_score (float): Ease of composite shell mold extraction (0.0 to 100.0).
        min_trailing_edge_thickness_mm (float): Minimum trailing edge thickness to avoid print split or delamination.
        carbon_spar_diameter_max_mm (float): Maximum diameter of carbon tube spar that physically fits in the airfoil thickness.
        suitability_rating (str): Qualitative evaluation (e.g. Excellent, Good, Marginal).
        metadata (Dict[str, Any]): Detailed geometry calculations.
    """

    foam_cut_feasibility_score: float
    mold_release_feasibility_score: float
    min_trailing_edge_thickness_mm: float
    carbon_spar_diameter_max_mm: float
    suitability_rating: str
    metadata: Dict[str, Any] = field(default_factory=dict)
