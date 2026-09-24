from dataclasses import dataclass, field
from typing import Any, Dict, List

from .payload_selector import Payload
from .payload_mount import PayloadMount
from .payload_bay import PayloadBay
from .payload_interfaces import PayloadInterfaces
from .payload_power import PayloadPower
from .payload_thermal import PayloadThermal
from .payload_cg import PayloadCG
from .payload_analysis import PayloadAnalysis

@dataclass(slots=True)
class PayloadResult:
    """
    Consolidated output of the VTOL Payload Engineering pipeline.
    """
    payload_selection: Payload
    payload_mount: PayloadMount
    payload_bay: PayloadBay
    payload_interfaces: PayloadInterfaces
    payload_power: PayloadPower
    payload_thermal: PayloadThermal
    payload_cg: PayloadCG
    payload_analysis: PayloadAnalysis

    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
