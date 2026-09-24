from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .hover_thrust import HoverThrust
from .hover_power import HoverPower
from .hover_efficiency import HoverEfficiency
from .hover_stability import HoverStability
from .hover_control import HoverControl
from .wind_hover_analysis import WindHoverAnalysis
from .altitude_hover_analysis import AltitudeHoverAnalysis
from .failure_hover_analysis import FailureHoverAnalysis
from .hover_analysis import HoverAnalysis
from .authoritative_hover import AuthoritativeHoverResult

@dataclass(slots=True)
class HoverResult:
    """
    Consolidated outputs of the VTOL Hover Performance Engineering pipeline.
    """
    hover_thrust: HoverThrust
    hover_power: HoverPower
    hover_efficiency: HoverEfficiency
    hover_stability: HoverStability
    hover_control: HoverControl
    wind_analysis: WindHoverAnalysis
    altitude_analysis: AltitudeHoverAnalysis
    failure_analysis: FailureHoverAnalysis
    hover_analysis: HoverAnalysis

    authoritative_result: Optional[AuthoritativeHoverResult] = None
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
