"""
VTOL Lift System Constraints Subsystem

Purpose:
    Defines the `LiftSystemConstraints` class storing geometric boundaries.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class LiftSystemConstraints:
    """
    Limits on rotor sizing, thrust margins, and disk loadings.

    Attributes:
        min_rotor_diameter_m (float): Lower bound of propeller size.
        max_rotor_diameter_m (float): Upper bound of propeller size.
        min_thrust_to_weight_ratio (float): Lower safety limit for T/W.
        max_disk_loading_n_m2 (float): Upper limit for rotor disk loading (N/m²).
        metadata (Dict[str, Any]): Additional regulatory limits.
    """

    min_rotor_diameter_m: float = 0.12  # ~5 inches
    max_rotor_diameter_m: float = 1.20  # ~47 inches
    min_thrust_to_weight_ratio: float = 1.30
    max_disk_loading_n_m2: float = 150.0
    metadata: Dict[str, Any] = field(default_factory=dict)
