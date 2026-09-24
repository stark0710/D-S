"""
VTOL Wing Structure Subsystem

Purpose:
    Defines the `WingStructure` class describing wing reinforcement and material properties.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class WingStructure:
    """
    Structural parameters and weight estimates of the VTOL wing.

    Attributes:
        structural_concept (str): Internal concept layout (e.g. Rib and Spar, Carbon Shell).
        estimated_wing_weight_kg (float): Sized empty weight of wing panels in kg.
        limit_load_factor_g (float): Operational G load capacity.
        ultimate_load_factor_g (float): Ultimate structural breaking G load.
        spar_material (str): Main load-bearing spar material.
        metadata (Dict[str, Any]): Section thicknesses or layup properties.
    """

    structural_concept: str
    estimated_wing_weight_kg: float
    limit_load_factor_g: float
    ultimate_load_factor_g: float
    spar_material: str
    metadata: Dict[str, Any] = field(default_factory=dict)
