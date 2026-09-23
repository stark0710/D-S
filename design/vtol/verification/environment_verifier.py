from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class EnvironmentVerification:
    """
    Verifies hover/cruise wind margins.
    """
    wind_tolerance_limit_kts: float
    density_altitude_ceiling_m: float
    thermal_dissipation_verified: bool
    is_environment_verified: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
