from dataclasses import dataclass, field
from typing import Any, Dict, List

from .cruise_speed_analysis import CruiseSpeedAnalysis
from .cruise_power_analysis import CruisePowerAnalysis
from .range_analysis import RangeAnalysis
from .endurance_analysis import EnduranceAnalysis
from .climb_analysis import ClimbAnalysis
from .descent_analysis import DescentAnalysis
from .maneuver_analysis import ManeuverAnalysis
from .performance_envelope_analysis import PerformanceEnvelope
from .cruise_analysis import CruiseAnalysis

@dataclass(slots=True)
class CruiseResult:
    """
    Consolidated outputs of the VTOL Cruise Sizing Framework.
    """
    speed_analysis: CruiseSpeedAnalysis
    power_analysis: CruisePowerAnalysis
    range_analysis: RangeAnalysis
    endurance_analysis: EnduranceAnalysis
    climb_analysis: ClimbAnalysis
    descent_analysis: DescentAnalysis
    maneuver_analysis: ManeuverAnalysis
    performance_envelope: PerformanceEnvelope
    cruise_analysis: CruiseAnalysis

    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
