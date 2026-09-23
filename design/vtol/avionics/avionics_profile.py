"""
VTOL Avionics Profile Reference Data

Purpose:
    Defines baseline resource footprints and data bus parameters.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class AvionicsProfile:
    """
    Reference resource utilization and constraints.
    """
    baseline_cpu_stabilization_pct: float = 15.0
    serial_telemetry_cpu_load_pct: float = 5.0
    rtk_gps_cpu_load_pct: float = 6.0
    visual_nav_cpu_load_pct: float = 12.0
    obstacle_avoidance_cpu_load_pct: float = 15.0

    memory_baseline_mb: float = 64.0
    memory_rtk_mb: float = 32.0
    memory_vision_mb: float = 512.0
    memory_obstacle_avoidance_mb: float = 256.0

    can_bandwidth_kbps: float = 1000.0
    i2c_bandwidth_kbps: float = 400.0
    uart_bandwidth_kbps: float = 115.2
    spi_bandwidth_kbps: float = 10000.0
    ethernet_bandwidth_mbps: float = 100.0

    metadata: Dict[str, Any] = field(default_factory=dict)
