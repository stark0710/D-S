"""
Fixed-Wing Fuselage Optimization Models

Defines the FuselageSpecification class.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass(slots=True)
class FuselageSpecification:
    """
    Standardized specification containing optimal fuselage geometry output by the optimizer.
    """
    overall_length: float
    width: float
    height: float
    nose_length: float
    cabin_length: float
    tail_cone_length: float
    cross_section: str
    fineness_ratio: float
    wing_mount_position: float
    payload_bay: Dict[str, Any]
    battery_bay: Dict[str, Any]
    avionics_bay: Dict[str, Any]
    bulkhead_locations: List[float]
    optimization_score: float
    reasoning: str
