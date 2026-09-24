from dataclasses import dataclass, field
from typing import Dict

@dataclass(slots=True)
class ElectricalSpecification:
    """
    Sized and optimized aircraft Power Distribution & Electrical Integration architecture specification.
    """
    power_distribution: str
    wire_gauge_summary: Dict[str, str]
    connector_summary: Dict[str, str]
    power_budget: Dict[str, float]
    voltage_budget: Dict[str, float]
    current_budget: Dict[str, float]
    loss_summary: Dict[str, float]
    electrical_efficiency_pct: float
    safety_margins: Dict[str, float]
    optimization_score: float
    engineering_reasoning: str
