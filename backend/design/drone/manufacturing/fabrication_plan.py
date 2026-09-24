"""
FabricationPlan Subsystem

Purpose:
    Defines the `FabricationPlan` domain model and service representing custom fabrication instructions (3D printing, CNC machining, laser cutting).

Role in Architecture:
    `FabricationPlan` generates cut lists, 3D printing lists, and CNC instructions for custom components.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.cad.cad_result import CADResult


@dataclass(slots=True)
class FabricationPlan:
    """
    Multirotor custom fabrication plan details.

    Attributes:
        cnc_machined_parts (list[str]): List of CNC aluminum/carbon parts instructions.
        laser_cut_parts (list[str]): List of laser cut plates.
        printed_parts_3d (list[str]): List of 3D printed accessory mounts.
        metadata (dict[str, Any]): Additional fabrication metadata.
    """

    cnc_machined_parts: list[str] = field(default_factory=list)
    laser_cut_parts: list[str] = field(default_factory=list)
    printed_parts_3d: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class FabricationPlanner:
    """
    Planning service for custom component fabrication.

    Design Principles:
        - Single Responsibility Principle: Fabrication method assignment and cut lists generation only.
    """

    def generate_fabrication_plan(self, cad_result: CADResult) -> FabricationPlan:
        """
        Builds fabrication instructions based on CAD components.

        Args:
            cad_result (CADResult): Input CAD result.

        Returns:
            FabricationPlan: Computed custom fabrication plan.
        """
        cnc = []
        laser = []
        printed = []

        for c in cad_result.components:
            name = c.name
            cat = c.category.upper()

            if cat == "FRAME":
                laser.append(f"Laser cut '{name}' from 2.5mm carbon fiber plate.")
            elif cat == "MOUNT":
                printed.append(f"3D print '{name}' using PLA/TPU filament (100% infill).")
            elif cat == "LANDING_GEAR":
                cnc.append(f"CNC machine '{name}' mounts from Aluminum 6061-T6.")

        if not printed:
            printed.append("3D print payload quick-release locking mechanism (PETG/ABS).")

        return FabricationPlan(
            cnc_machined_parts=cnc,
            laser_cut_parts=laser,
            printed_parts_3d=printed
        )
