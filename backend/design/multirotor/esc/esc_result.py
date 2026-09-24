from dataclasses import dataclass

@dataclass(slots=True)
class ESCSpecification:
    """
    Sized and optimized Electronic Speed Controller (ESC) specification.
    """
    manufacturer: str
    model: str
    continuous_current_a: float
    burst_current_a: float
    voltage_range_v: tuple[float, float]
    bec: str  # e.g., "5V/2A" or "None"
    protocol: str
    weight_kg: float
    current_margin_a: float
    thermal_margin_pct: float
    efficiency_pct: float
    optimization_score: float
    engineering_reasoning: str
