"""
Fixed-Wing Tail Optimization Models

Defines the TailSpecification class.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class TailSpecification:
    """
    Standardized specification containing the optimized empennage geometry and configuration.
    """
    tail_configuration: str
    horizontal_tail_area_m2: float
    horizontal_tail_span_m: float
    horizontal_tail_root_chord_m: float
    horizontal_tail_tip_chord_m: float
    vertical_tail_area_m2: float
    vertical_tail_height_m: float
    vertical_tail_root_chord_m: float
    vertical_tail_tip_chord_m: float
    horizontal_volume_coefficient: float
    vertical_volume_coefficient: float
    tail_arm_m: float
    horizontal_aspect_ratio: float
    vertical_aspect_ratio: float
    horizontal_taper_ratio: float
    vertical_taper_ratio: float
    horizontal_sweep_deg: float
    vertical_sweep_deg: float
    tail_dihedral_deg: float
    optimization_score: float
    reasoning: str
