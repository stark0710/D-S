"""
Fixed-Wing Aircraft Configuration Profile Subsystem

Purpose:
    Defines the `ConfigurationProfile` class, which holds profile settings and weighting coefficients.

Role in Architecture:
    The profile allows users or system-level policies to tune the weighting factors
    for configuration scoring, trade-off analysis, and recommendation ranking.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ConfigurationProfile:
    """
    Configuration profiles holding scoring parameters and relative weights for selection metrics.

    Attributes:
        structural_simplicity_weight (float): Importance weight for structural simplicity (0.0 to 1.0).
        manufacturability_weight (float): Importance weight for ease of production (0.0 to 1.0).
        aerodynamic_efficiency_weight (float): Importance weight for drag and glide efficiency (0.0 to 1.0).
        cost_impact_weight (float): Importance weight for minimizing financial impact (0.0 to 1.0).
        stability_weight (float): Importance weight for passive aerodynamic stability (0.0 to 1.0).
        maintenance_weight (float): Importance weight for accessibility and ease of maintenance (0.0 to 1.0).
    """

    structural_simplicity_weight: float = 1.0
    manufacturability_weight: float = 1.0
    aerodynamic_efficiency_weight: float = 1.0
    cost_impact_weight: float = 1.0
    stability_weight: float = 1.0
    maintenance_weight: float = 1.0
