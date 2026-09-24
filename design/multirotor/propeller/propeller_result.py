from dataclasses import dataclass

@dataclass(slots=True)
class PropellerSpecification:
    """
    Sized and optimized propulsion propeller specification.
    """
    manufacturer: str
    model: str
    diameter_m: float
    pitch_m: float
    blade_count: int
    material: str
    weight_kg: float
    disc_area_m2: float
    tip_speed_m_s: float
    hover_efficiency_g_w: float
    power_absorption_w: float
    optimization_score: float
    engineering_reasoning: str
