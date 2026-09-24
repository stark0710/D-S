"""
VTOL Configuration Analysis Subsystem

Purpose:
    Defines the `ConfigurationAnalysis` dataclass storing trade-offs and scores.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ConfigurationAnalysis:
    """
    Volumetric trade-off evaluation scores (0.0 to 100.0) of a selected VTOL architecture.

    Attributes:
        mission_suitability (float): Rating of chosen configuration for target mission.
        hover_efficiency (float): Sized hover power loading capability.
        cruise_efficiency (float): Aerodynamic lift/drag profile efficiency.
        transition_complexity (float): Complexity rating of physical transition methods.
        structural_simplicity (float): Weight penalty rating based on structural complexity.
        manufacturability (float): Ease of composite layup and motor integration.
        redundancy_score (float): Motor out fail-safe rating.
        maintenance_accessibility (float): Maintenance packaging density index.
        scalability (float): Potential for larger sizing variants.
        metadata (Dict[str, Any]): Detailed performance indicators.
    """

    mission_suitability: float
    hover_efficiency: float
    cruise_efficiency: float
    transition_complexity: float
    structural_simplicity: float
    manufacturability: float
    redundancy_score: float
    maintenance_accessibility: float
    scalability: float
    metadata: Dict[str, Any] = field(default_factory=dict)
