"""
Fixed-Wing Sizing Procurement list Subsystem

Purpose:
    Defines the `ProcurementList` class.

Role in Architecture:
    `ProcurementList` filters purchased standard items from the BOM to form suppliers procurement plans.
"""

from typing import List, Dict, Any


class ProcurementList:
    """
    Procurement planner filtering purchase components.
    """

    def generate_procurement_list(self, bom_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts components marked as purchased.

        Returns:
            List[Dict[str, Any]]: Procurement plan.
        """
        procurements: List[Dict[str, Any]] = []

        for item in bom_items:
            if item.get("type") == "Purchased":
                procurements.append({
                    "part_number": item["part_number"],
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "supplier": item.get("supplier", "Default Supplier"),
                })

        return procurements
