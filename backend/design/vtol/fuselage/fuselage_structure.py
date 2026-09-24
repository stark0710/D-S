"""
VTOL Fuselage Structure Subsystem

Purpose:
    Defines the `FuselageStructure` class capturing structural configurations
    and composite reinforcements.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class FuselageStructure:
    """
    Structural parameters of the sized fuselage shell.

    Attributes:
        construction_type (str): Structural skin style (e.g. Monocoque, Semi-monocoque).
        estimated_fuselage_weight_kg (float): Weight of the composite shell.
        wall_thickness_mm (float): thickness of the composite sandwich skin.
        reinforcement_locations (List[str]): Locations requiring extra carbon ply sheets.
        crash_energy_absorption_level (str): Level of crashworthiness (Low, Medium, High).
        metadata (Dict[str, Any]): Layup details.
    """

    construction_type: str
    estimated_fuselage_weight_kg: float
    wall_thickness_mm: float
    reinforcement_locations: List[str]
    crash_energy_absorption_level: str
    metadata: Dict[str, Any] = field(default_factory=dict)
