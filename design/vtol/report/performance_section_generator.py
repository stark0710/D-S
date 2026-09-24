from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PerformanceSection:
    """
    Hover, transition, and cruise flight envelop summaries.
    """
    title: str
    hover_metrics: Dict[str, str]
    transition_timeline: Dict[str, str]
    cruise_margins: Dict[str, str]
