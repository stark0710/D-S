from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass(slots=True)
class CommunicationSystem:
    """
    Onboard telemetry, RC and networking protocols.
    """
    telemetry_frequency_mhz: float
    telemetry_redundancy: bool
    has_rc_link: bool
    rc_frequency_mhz: float
    has_video_link: bool
    video_frequency_ghz: float
    has_satellite_link: bool
    
    internal_data_buses: List[str]
    can_topology: str
    ethernet_topology: str
    
    total_power_watts: float
    total_weight_kg: float
    metadata: Dict[str, Any] = field(default_factory=dict)
