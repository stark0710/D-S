from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass(slots=True)
class PayloadInterfaces:
    """
    Networking connections and control pathways.
    """
    data_connections: List[str]
    control_protocol: str
    maintenance_accessibility: str
    data_bandwidth_mbps: float
    quick_release_compatible: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
