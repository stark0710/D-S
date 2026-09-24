"""
VTOL Fuselage Sizing Analysis Subsystem

Purpose:
    Defines the `FuselageAnalysis` class evaluating wetted drags,
    thermal distributions, and CG balancing.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class FuselageAnalysis:
    """
    Volumetric trade-off evaluation scores (0.0 to 100.0) of a sized fuselage.

    Attributes:
        structural_efficiency (float): Structural capability index.
        packaging_efficiency (float): Sized volumetric packing ratio.
        aerodynamic_drag_coefficient_cd0 (float): Baseline drag coefficient.
        cg_offset_from_wing_mac_percent (float): CG offset distance from MAC center.
        cooling_effectiveness_score (float): Thermal dissipation effectiveness.
        maintenance_accessibility_score (float): accessibility score.
        manufacturability_score (float): Sized layups feasibility.
        modularity_score (float): Sized payload modularity level.
        weight_efficiency (float): Sized structural-to-total weight balance.
        metadata (Dict[str, Any]): Intermediate calculations.
    """

    structural_efficiency: float
    packaging_efficiency: float
    aerodynamic_drag_coefficient_cd0: float
    cg_offset_from_wing_mac_percent: float
    cooling_effectiveness_score: float
    maintenance_accessibility_score: float
    manufacturability_score: float
    modularity_score: float
    weight_efficiency: float
    metadata: Dict[str, Any] = field(default_factory=dict)
