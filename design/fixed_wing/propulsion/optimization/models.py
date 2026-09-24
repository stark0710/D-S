"""
Fixed-Wing Propulsion Optimization Specification Model
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class PropulsionSpecification:
    """
    Sized electric propulsion system configuration and simulated performance.
    """
    # Selected Hardware Components
    motor_name: str
    propeller_name: str
    esc_name: str
    battery_name: str

    # Electrical and Operating Parameters
    operating_voltage_v: float
    cruise_current_a: float
    max_climb_current_a: float
    cell_count_s: int
    battery_capacity_mah: float
    battery_weight_g: float
    total_propulsion_weight_g: float

    # Performance Metrics
    static_thrust_n: float
    cruise_thrust_n: float
    cruise_power_w: float
    takeoff_power_w: float
    motor_efficiency: float
    propeller_efficiency: float
    total_efficiency: float
    estimated_flight_time_min: float

    # Optimization Diagnostics
    optimization_score: float
    reasoning: str

    # Battery Engineering Technical Specification & Diagnostics (Phase 6B-3)
    battery_chemistry: str = "LiPo"
    battery_energy_wh: float = 0.0
    required_energy_wh: float = 0.0
    battery_c_rating: float = 0.0
    required_c_rating: float = 0.0
    target_endurance_min: float = 0.0
    target_range_km: float = 0.0
    energy_margin_pct: float = 0.0
    battery_technical_spec: Dict[str, Any] = field(default_factory=dict)

    # Multi-Engine & Component Sizing Metrics
    engine_count: int = 1
    per_motor_static_thrust_n: float = 0.0
    per_motor_max_power_w: float = 0.0
    per_motor_cruise_power_w: float = 0.0
    propulsion_layout: str = "Single Tractor"
    motor_weight_g: float = 0.0
    esc_weight_g: float = 0.0

