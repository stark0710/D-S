"""
VTOL Wing Sizing Profile Subsystem

Purpose:
    Defines the `WingProfile` class storing safety factors, limits,
    and material constants used in wing engineering.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class WingProfile:
    """
    Standard references for structural calculations.

    Attributes:
        default_safety_factor (float): Safety margin multiplier.
        structure_load_factor_limit_g (float): Sized G limit of wing load.
        material_density_balsa_kg_m3 (float): Reference balsa density.
        material_density_carbon_kg_m3 (float): Reference carbon fiber density.
        metadata (Dict[str, Any]): General design references.
    """

    default_safety_factor: float = 1.5
    structure_load_factor_limit_g: float = 4.0
    material_density_balsa_kg_m3: float = 130.0
    material_density_carbon_kg_m3: float = 1600.0
    metadata: Dict[str, Any] = field(default_factory=dict)
