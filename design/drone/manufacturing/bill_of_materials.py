"""
BillOfMaterials Subsystem

Purpose:
    Defines the `BillOfMaterials` domain model representing a structured Bill of Materials (BOM).

Role in Architecture:
    `BillOfMaterials` lists component parts, quantities, suppliers, estimated unit costs, and categories.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.cad.cad_result import CADResult


@dataclass(slots=True)
class BOMItem:
    """Single item record in a Bill of Materials."""
    part_number: str
    name: str
    category: str
    quantity: int
    unit_cost_usd: float
    supplier: str


@dataclass(slots=True)
class BillOfMaterials:
    """
    Multirotor Bill of Materials (BOM) definition.

    Attributes:
        items (list[BOMItem]): List of parts items.
        total_items (int): Total count of parts.
        total_cost_usd (float): Estimated total cost in USD.
        metadata (dict[str, Any]): Additional BOM metadata.
    """

    items: list[BOMItem] = field(default_factory=list)
    total_items: int = 0
    total_cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BOMGenerator:
    """
    Service for generating a structured Bill of Materials from CAD components.

    Design Principles:
        - Single Responsibility Principle: CAD components to BOM items translation and cost summation only.
    """

    def generate_bom(self, cad_result: CADResult) -> BillOfMaterials:
        """
        Converts CADComponents list into a structured Bill of Materials.

        Args:
            cad_result (CADResult): CAD result containing component geometries.

        Returns:
            BillOfMaterials: Computed BOM.
        """
        items: list[BOMItem] = []
        total_cost = 0.0

        for c in cad_result.components:
            # Map categories to cost assumptions
            cost = 15.0
            supplier = "Local Parts Distributor"
            cat = c.category.upper()

            if cat == "MOTOR":
                cost = 45.0
                supplier = "T-Motor Official"
            elif cat == "BATTERY":
                cost = 180.0
                supplier = "Gens Ace Supplier"
            elif cat == "FLIGHT_CONTROLLER":
                cost = 250.0
                supplier = "Cube Autopilot"
            elif cat == "PAYLOAD":
                cost = 400.0
                supplier = "Custom Imaging"

            items.append(
                BOMItem(
                    part_number=f"TW-{cat[:4]}-{len(items)+1:03d}",
                    name=c.name,
                    category=c.category,
                    quantity=1,
                    unit_cost_usd=cost,
                    supplier=supplier
                )
            )
            total_cost += cost

        return BillOfMaterials(
            items=items,
            total_items=len(items),
            total_cost_usd=round(total_cost, 2)
        )
