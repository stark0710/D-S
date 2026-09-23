from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class TimeSynchronization:
    """
    Clock alignment routines across sensors and computers.
    """
    synchronization_protocol: str
    time_offset_limit_ms: float
    clock_source: str
    camera_trigger_sync_active: bool
    imu_gps_pps_aligned: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
