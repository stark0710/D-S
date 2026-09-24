"""
VTOL Lift System Sizing Analysis Subsystem

Purpose:
    Defines the `LiftSystemAnalysis` class evaluating disk loading and efficiency.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class LiftSystemAnalysis:
    """
    Rotor loading efficiency indices of the vertical lift system.

    Attributes:
        disk_loading_n_m2 (float): Thrust per unit rotor swept area in N/m².
        power_loading_n_w (float): Sized thrust generated per unit electric watt in N/W.
        hover_efficiency_g_w (float): Hover efficiency in grams of thrust per watt (g/W).
        rotor_interference_loss_factor (float): Lift degradation penalty due to overlapping/coaxial rotors.
        noise_level_db (float): Estimated acoustic noise level.
        manufacturability_score (float): Sized layout complexity.
        fault_tolerance_score (float): Reliability/failure resilience index.
        metadata (Dict[str, Any]): Additional aerodynamic coefficients.
    """

    disk_loading_n_m2: float
    power_loading_n_w: float
    hover_efficiency_g_w: float
    rotor_interference_loss_factor: float
    noise_level_db: float
    manufacturability_score: float
    fault_tolerance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
