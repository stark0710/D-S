"""
Fixed-Wing Payload Packaging Optimization Models

Defines the PayloadPackagingSpecification class.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass(slots=True)
class PayloadPackagingSpecification:
    """
    Standardized specification containing optimal positions, layouts, and orientations
    for components inside the fuselage.
    """
    payload_position: float
    battery_position: float
    battery_orientation: str
    avionics_layout: Dict[str, Any]
    electronics_layout: Dict[str, Any]
    gps_position: float
    receiver_position: float
    telemetry_position: float
    power_distribution: Dict[str, Any]
    access_panels: List[Dict[str, Any]]
    reserved_expansion_space: float
    packaging_efficiency_score: float
    optimization_score: float
    reasoning: str
