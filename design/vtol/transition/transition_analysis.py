"""
VTOL Transition Analysis Aggregator
"""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class TransitionAnalysis:
    conversion_speed_kmh: float
    duration_s: float
    energy_kwh: float
    min_stability_margin: float
    control_saturation_risk_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
