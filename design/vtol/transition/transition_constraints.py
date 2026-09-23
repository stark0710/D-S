"""
VTOL Transition Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class TransitionConstraints:
    """
    Conversion boundary limits.
    """
    min_conversion_speed_kmh: float = 40.0
    max_conversion_speed_kmh: float = 90.0
    max_transition_duration_s: float = 30.0
    max_pitch_pitchrate_deg_s: float = 5.0
    min_stability_margin_transition: float = 0.05
    max_current_draw_pct_limit: float = 95.0
    metadata: Dict[str, Any] = field(default_factory=dict)
