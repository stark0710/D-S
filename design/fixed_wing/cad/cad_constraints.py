"""
Fixed-Wing CAD Constraints Subsystem

Purpose:
    Defines the `CADConstraints` class.

Role in Architecture:
    `CADConstraints` gathers physical assembly limits and format rules.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class CADConstraints:
    """
    Sizing limits restricting CAD model generation.

    Attributes:
        allowed_export_formats (List[str]): List of active export formats allowed by user.
        min_clearance_mm (float): Minimum physical gap between component fittings.
        max_allowable_errors (int): Limit on geometry regeneration failures.
    """

    allowed_export_formats: List[str] = field(
        default_factory=lambda: ["STEP", "STL", "IGES", "GLTF", "OBJ", "PARASOLID"]
    )
    min_clearance_mm: float = 0.1
    max_allowable_errors: int = 0
