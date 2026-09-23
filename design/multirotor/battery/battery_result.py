from dataclasses import dataclass, field
from typing import Dict, Any
from backend.design.multirotor.motor.motor_result import MotorSpecification
from backend.design.multirotor.propeller.propeller_result import PropellerSpecification
from backend.design.multirotor.esc.esc_result import ESCSpecification

@dataclass(slots=True)
class BatterySpecification:
    """
    Sized and optimized Battery specification.
    """
    manufacturer: str
    model: str
    chemistry: str
    voltage: float
    cell_count: int
    capacity_mah: float
    weight_kg: float
    energy_wh: float
    continuous_current_a: float
    burst_current_a: float
    estimated_hover_time_min: float
    estimated_flight_time_min: float
    remaining_energy_margin_pct: float
    optimization_score: float
    engineering_reasoning: str


@dataclass
class PropulsionAssembly:
    """
    Unified propulsion system compilation mapping Motor, Propeller, ESC, and Battery specifications.
    """
    motor: MotorSpecification
    propeller: PropellerSpecification
    esc: ESCSpecification
    battery: BatterySpecification
    
    # Sized system totals
    estimated_auw_kg: float
    total_hover_thrust_n: float
    max_thrust_capability_n: float
    hover_throttle_pct: float
    
    # Sized electrical totals
    hover_current_total_a: float
    hover_power_total_w: float
    peak_current_total_a: float
    peak_power_total_w: float
    
    # Validation results
    safety_margins: Dict[str, Any] = field(default_factory=dict)
    compatibility_matrix: Dict[str, Any] = field(default_factory=dict)
