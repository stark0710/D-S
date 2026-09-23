"""
Fixed-Wing Wing Planform Optimization Models

Defines the PlanformCandidate and OptimizationBounds data models.
"""

from dataclasses import dataclass, field

@dataclass(slots=True)
class PlanformCandidate:
    """
    Represents a specific wing planform design candidate in the optimization space.
    """
    aspect_ratio: float
    taper_ratio: float
    sweep_angle_deg: float
    wing_loading_kg_m2: float

@dataclass(slots=True)
class OptimizationBounds:
    """
    Defines the search boundaries and discretization steps for the optimizer.
    """
    min_aspect_ratio: float = 4.0
    max_aspect_ratio: float = 20.0
    aspect_ratio_steps: int = 5

    min_taper_ratio: float = 0.1
    max_taper_ratio: float = 1.0
    taper_ratio_steps: int = 5

    min_sweep_deg: float = 0.0
    max_sweep_deg: float = 45.0
    sweep_steps: int = 5

    min_wing_loading_kg_m2: float = 5.0
    max_wing_loading_kg_m2: float = 80.0
    wing_loading_steps: int = 5

@dataclass(slots=True)
class WingPlanformSpecification:
    """
    Represents the optimized wing geometry configuration handed off to downstream subsystems.
    """
    span_m: float
    area_m2: float
    aspect_ratio: float
    mean_aerodynamic_chord_m: float
    taper_ratio: float
    sweep_angle_deg: float

