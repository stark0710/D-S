from dataclasses import dataclass

@dataclass(slots=True)
class MotorSpecification:
    """
    Sized and optimized propulsion motor specification.
    """
    manufacturer: str
    model: str
    kv: float
    voltage_range_v: tuple[float, float]
    max_thrust_n: float
    hover_thrust_n: float
    hover_current_a: float
    max_current_a: float
    efficiency_pct: float
    weight_kg: float
    power_margin_w: float
    throttle_hover_pct: float
    mount_pattern_mm: str
    optimization_score: float
    engineering_reasoning: str
