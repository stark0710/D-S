"""
VTOL Optimization Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class OptimizationConstraints:
    """
    Penalty factors and boundary limits for design optimizer iterations.
    """
    max_takeoff_weight_limit_kg: float = 80.0
    cg_margin_mac_limit: float = 5.0
    min_climb_rate_limit_m_s: float = 2.0
    max_continuous_current_limit_amps: float = 120.0
    min_reserve_soc_limit_pct: float = 15.0
    metadata: Dict[str, Any] = field(default_factory=dict)
