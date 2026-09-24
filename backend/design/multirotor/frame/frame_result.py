from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

@dataclass(slots=True)
class FrameSpecification:
    """
    Sized and optimized structural frame specification.
    """
    configuration: str
    wheelbase_m: float
    arm_length_m: float
    arm_diameter_m: float
    arm_count: int
    motor_coordinates: List[Tuple[float, float, float]]
    payload_bay_dimensions_m: Tuple[float, float, float]
    landing_gear_height_m: float
    ground_clearance_m: float
    frame_mass_kg: float
    envelope_dimensions_m: Tuple[float, float, float]
    structural_safety_margin: float
    approach_type: str  # "Catalog Selection" or "Parametric Generation"
    selected_name: str
    optimization_score: float
    engineering_reasoning: str
