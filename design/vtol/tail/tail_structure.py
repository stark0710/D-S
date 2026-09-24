"""
VTOL Tail Structure Subsystem

Purpose:
    Defines the `TailStructure` class capturing structural concepts, materials,
    and boom configurations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class TailStructure:
    """
    Empennage construction details.

    Attributes:
        structural_concept (str): Internal concept layout (e.g. Twin Carbon Boom, Fuselage mount).
        estimated_tail_weight_kg (float): Total mass of tail assembly in kg.
        boom_diameter_mm (float): Outer diameter of main tail boom tube.
        boom_material (str): Main load-bearing boom material.
        metadata (Dict[str, Any]): Section thicknesses or joint interfaces.
    """

    structural_concept: str
    estimated_tail_weight_kg: float
    boom_diameter_mm: float
    boom_material: str
    metadata: Dict[str, Any] = field(default_factory=dict)
