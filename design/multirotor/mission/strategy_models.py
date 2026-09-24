from dataclasses import dataclass

@dataclass(slots=True)
class PriorityWeights:
    """
    Design optimization priority weighting factors (each between 0.0 and 1.0).
    """
    endurance: float
    payload_capacity: float
    efficiency: float
    agility: float
    wind_resistance: float
    cost: float
    reliability: float
    safety: float
    redundancy: float
    manufacturability: float


@dataclass(slots=True)
class DesignStrategy:
    """
    Summarized design direction strategies for down-stream optimization modules.
    """
    key_objective: str
    propulsion_strategy: str
    structural_strategy: str
    electrical_strategy: str
