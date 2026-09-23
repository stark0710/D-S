from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class HealthMonitor:
    """
    Diagnostics, sensor validation, and fail-over checks.
    """
    pre_flight_checks_active: bool
    in_flight_sensor_voting: bool
    battery_health_monitoring: bool
    vibration_monitoring_active: bool
    actuator_feedback_active: bool
    telemetry_link_watchdog: bool
    esc_telemetry_active: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
