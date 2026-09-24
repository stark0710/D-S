"""
VTOL Payload Constraints definition
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass(slots=True)
class PayloadConstraints:
    """
    Structural, electrical, thermal and CG limits.
    """
    max_payload_mass_kg: float = 50.0
    max_payload_power_watts: float = 120.0
    max_cg_shift_pct_mac: float = 5.0
    max_thermal_dissipation_watts: float = 80.0
    required_interfaces: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
