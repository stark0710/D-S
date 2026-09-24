"""
OptimizationPriority Enumeration Subsystem

Purpose:
    Defines the `OptimizationPriority` enumeration representing target optimization trade-off metrics.

Role in Architecture:
    `OptimizationPriority` directs the Optimization Engine and Component Selection Engines toward specific optimization targets
    such as Lowest Cost, Lowest Weight, Maximum Endurance, Maximum Range, Maximum Payload, Highest Efficiency, or Balanced.
"""

from enum import Enum


class OptimizationPriority(str, Enum):
    """
    Design optimization priority targets.

    Members:
        LOWEST_COST: Minimize total bill of materials (BOM) component cost.
        LOWEST_WEIGHT: Minimize Maximum Take-Off Weight (MTOW) and structural mass.
        MAXIMUM_ENDURANCE: Maximize flight time (minutes) on a single energy charge/fuel capacity.
        MAXIMUM_RANGE: Maximize total flight distance (km) covered.
        MAXIMUM_PAYLOAD: Maximize payload mass fraction and capacity.
        HIGHEST_EFFICIENCY: Maximize aerodynamic (L/D) and propulsion overall efficiency.
        BALANCED: Trade-off balance across cost, weight, range, and endurance.
    """
    LOWEST_COST = "LOWEST_COST"
    LOWEST_WEIGHT = "LOWEST_WEIGHT"
    MAXIMUM_ENDURANCE = "MAXIMUM_ENDURANCE"
    MAXIMUM_RANGE = "MAXIMUM_RANGE"
    MAXIMUM_PAYLOAD = "MAXIMUM_PAYLOAD"
    HIGHEST_EFFICIENCY = "HIGHEST_EFFICIENCY"
    BALANCED = "BALANCED"
