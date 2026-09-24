"""
Fixed-Wing Sizing Manufacturing Cost Estimator

Purpose:
    Defines the `CostEstimator` class.

Role in Architecture:
    `CostEstimator` calculates material, component, labor, and overhead costs.
"""

from typing import List, Dict, Any


class CostEstimator:
    """
    Cost estimation calculator for fixed-wing production units.
    """

    def estimate_costs(
        self,
        bom_items: List[Dict[str, Any]],
        build_hours: float,
        labor_rate: float,
        tooling_overhead_usd: float,
        material_multiplier: float,
    ) -> float:
        """
        Computes the total unit manufacturing cost estimate.

        Returns:
            float: Sized total cost in USD.
        """
        # Sum purchased component costs (or assume standard defaults if pricing is missing)
        component_cost = 0.0
        for item in bom_items:
            # Sizing component base prices
            if "fc" in item["name"].lower():
                component_cost += 150.0
            elif "motor" in item["name"].lower():
                component_cost += 45.0
            elif "propeller" in item["name"].lower():
                component_cost += 8.0
            elif "battery" in item["name"].lower():
                component_cost += 85.0
            elif "bolt" in item["name"].lower():
                component_cost += 1.5 * item["quantity"]

        # Raw materials (balsa wood panels, composite resins, glue)
        raw_material_base_usd = 120.0
        material_cost = raw_material_base_usd * material_multiplier

        # Labor cost
        labor_cost = build_hours * labor_rate

        # Total
        total_cost = component_cost + material_cost + labor_cost + tooling_overhead_usd
        return round(total_cost, 2)
