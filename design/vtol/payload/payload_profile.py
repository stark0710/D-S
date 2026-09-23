"""
VTOL Payload Profile reference parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class PayloadProfile:
    """
    Reference values and constants for payload integration calculations.
    """
    base_data_overhead_mbps: float = 0.5
    quick_release_weight_penalty_kg: float = 0.15
    isolation_mount_weight_penalty_kg: float = 0.10
    vibration_isolation_damping_factor: float = 0.70
    aerodynamic_drag_coefficient_gimbal: float = 0.35
    aerodynamic_drag_coefficient_cargo_pod: float = 0.15
    metadata: Dict[str, Any] = field(default_factory=dict)
