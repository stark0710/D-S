"""
ProcurementList Subsystem

Purpose:
    Defines the `ProcurementList` domain model representing parts acquisition status.

Role in Architecture:
    `ProcurementList` identifies off-the-shelf vs custom fabrication parts, lead times, and suppliers.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.manufacturing.bill_of_materials import BillOfMaterials


@dataclass(slots=True)
class ProcurementItem:
    """Acquisition item tracking details."""
    part_number: str
    name: str
    supplier: str
    lead_time_days: int
    procurement_type: str  # 'COTS' (Commercial Off The Shelf) or 'CUSTOM_FABRICATION'


@dataclass(slots=True)
class ProcurementList:
    """
    Multirotor procurement status model.

    Attributes:
        items (list[ProcurementItem]): List of procurement track items.
        max_lead_time_days (int): Maximum lead time in days.
        metadata (dict[str, Any]): Additional procurement metadata.
    """

    items: list[ProcurementItem] = field(default_factory=list)
    max_lead_time_days: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ProcurementPlanner:
    """
    Service for generating a procurement list from a Bill of Materials.

    Design Principles:
        - Single Responsibility Principle: BOM list to procurement status translation only.
    """

    def generate_procurement_list(self, bom: BillOfMaterials) -> ProcurementList:
        """
        Builds procurement details from BOM.

        Args:
            bom (BillOfMaterials): Input BOM.

        Returns:
            ProcurementList: Computed procurement list.
        """
        items: list[ProcurementItem] = []
        max_lead = 0

        for it in bom.items:
            # Sizing lead times based on custom vs off-the-shelf
            cat = it.category.upper()
            ptype = "COTS"
            lead = 3

            if cat in ["FRAME", "MOUNT"]:
                ptype = "CUSTOM_FABRICATION"
                lead = 7

            items.append(
                ProcurementItem(
                    part_number=it.part_number,
                    name=it.name,
                    supplier=it.supplier,
                    lead_time_days=lead,
                    procurement_type=ptype
                )
            )
            max_lead = max(max_lead, lead)

        return ProcurementList(
            items=items,
            max_lead_time_days=max_lead
        )
