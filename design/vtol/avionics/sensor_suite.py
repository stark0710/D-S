from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class SensorSuite:
    """
    Sized sensory hardware integrated into the design.
    """
    has_gnss: bool
    gnss_receiver_type: str
    gnss_count: int
    
    has_imu: bool
    imu_count: int
    
    has_magnetometer: bool
    magnetometer_count: int
    
    has_barometer: bool
    barometer_count: int
    
    has_airspeed: bool
    airspeed_type: str
    
    has_rangefinder: bool
    rangefinder_type: str
    
    has_optical_flow: bool
    
    total_power_watts: float
    total_weight_kg: float
    
    metadata: Dict[str, Any] = field(default_factory=dict)
