"""
PackagingPlan Subsystem

Purpose:
    Defines the `PackagingPlan` domain model representing aircraft shipping and transport guidelines.

Role in Architecture:
    `PackagingPlan` specifies transport box dimensions in mm, required protective foam material, and safe shipping/handling instructions.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PackagingPlan:
    """
    Multirotor transport packaging guidelines model.

    Attributes:
        packaging_box_dimensions_mm (tuple[float, float, float]): Bounding box dimensions of the shipping crate (L, W, H).
        cushioning_material (str): Foam protection material description.
        handling_instructions (list[str]): Fragile item handling requirements.
        metadata (dict[str, Any]): Additional packaging metadata.
    """

    packaging_box_dimensions_mm: tuple[float, float, float] = (800.0, 800.0, 400.0)
    cushioning_material: str = "Polyethylene Custom Cut Foam"
    handling_instructions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
