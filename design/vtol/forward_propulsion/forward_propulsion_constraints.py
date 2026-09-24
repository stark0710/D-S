"""
VTOL Forward Propulsion Constraints Subsystem

Purpose:
    Defines the `ForwardPropulsionConstraints` class storing geometric and safety bounds.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ForwardPropulsionConstraints:
    """
    Limits on propeller sizing, ESC currents, and climb margins.

    Attributes:
        min_propeller_diameter_m (float): Lower bound of propeller size.
        max_propeller_diameter_m (float): Upper bound of propeller size.
        max_esc_current_a (float): Maximum continuous ESC thermal capacity in amps.
        min_climb_rate_m_s (float): Lower safety limit for forward climb rates.
        metadata (Dict[str, Any]): Additional regulatory limits.
    """

    min_propeller_diameter_m: float = 0.10  # ~4 inches
    max_propeller_diameter_m: float = 0.80  # ~31 inches
    max_esc_current_a: float = 120.0
    min_climb_rate_m_s: float = 1.5
    metadata: Dict[str, Any] = field(default_factory=dict)
