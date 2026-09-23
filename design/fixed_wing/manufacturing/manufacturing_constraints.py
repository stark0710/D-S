"""
Fixed-Wing Manufacturing Constraints Subsystem

Purpose:
    Defines the `ManufacturingConstraints` class.

Role in Architecture:
    `ManufacturingConstraints` gathers budget boundaries and material yield rates.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ManufacturingConstraints:
    """
    Sizing limits restricting manufacturing cost and process plans.

    Attributes:
        max_budget_limit (float): Upper financial threshold on unit cost.
        min_material_yield_pct (float): Minimum nesting layout sheet utilization (default 75.0).
        max_lead_time_days (int): Allowed build duration limits.
    """

    max_budget_limit: float = 5000.0
    min_material_yield_pct: float = 75.0
    max_lead_time_days: int = 14
