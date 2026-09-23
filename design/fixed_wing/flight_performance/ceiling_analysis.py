"""
Fixed-Wing Ceiling Performance Analysis Subsystem

Purpose:
    Defines the `CeilingAnalysis` class.

Role in Architecture:
    `CeilingAnalysis` holds absolute and service altitudes limits.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class CeilingAnalysis:
    """
    Flight altitude limits.

    Attributes:
        absolute_ceiling_m (float): Sized max altitude where ROC drops to zero.
        service_ceiling_m (float): Sized max altitude where ROC is exactly 0.5 m/s (100 ft/min).
        density_altitude_limit_m (float): Density altitude limits.
        metadata (Dict[str, Any]): Power reduction indices.
    """

    absolute_ceiling_m: float
    service_ceiling_m: float
    density_altitude_limit_m: float
    metadata: Dict[str, Any] = field(default_factory=dict)
