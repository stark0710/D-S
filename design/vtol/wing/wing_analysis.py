"""
VTOL Wing Analysis Subsystem

Purpose:
    Defines the `WingAnalysis` dataclass storing loading values,
    dynamic bending moments, and ease-of-mfg ratings.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class WingAnalysis:
    """
    Volumetric trade-off check values of the sized wing system.

    Attributes:
        wing_loading_kg_m2 (float): Wing loading parameter.
        cruise_lift_coefficient (float): Required cruise lift coefficient (Cl).
        stall_speed_cruise_configuration_kmh (float): Calculated cruise-configuration stall speed.
        cruise_efficiency (float): Rating of wing planform for forward flight.
        hover_structural_loading (float): Bending score index under vertical motor weights.
        transition_bending_moment_nm (float): Estimated peak bending moment at wing root during transition.
        structural_efficiency (float): Sized lift-to-weight ratio capability.
        manufacturability_score (float): Ease of laying composite skins or printing wing ribs (0.0 to 100.0).
        motor_integration_score (float): Rating of motor cabling and boom packaging.
        maintenance_accessibility_score (float): Ease of access to wing tip servo links.
        metadata (Dict[str, Any]): Detailed performance indicators.
    """

    wing_loading_kg_m2: float
    cruise_lift_coefficient: float
    stall_speed_cruise_configuration_kmh: float
    cruise_efficiency: float
    hover_structural_loading: float
    transition_bending_moment_nm: float
    structural_efficiency: float
    manufacturability_score: float
    motor_integration_score: float
    maintenance_accessibility_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
