"""
OptimizationGoal Enumeration Subsystem

Purpose:
    Defines the `OptimizationGoal` enumeration representing target goals for engineering design optimization.

Role in Architecture:
    `OptimizationGoal` classifies target goals (Minimum Weight, Minimum Cost, Maximum Endurance, Maximum Range, Maximum Payload, Highest Efficiency, Balanced)
    used by the Universal Engineering Optimization Framework.
"""

from enum import Enum


class OptimizationGoal(str, Enum):
    """
    Aircraft design optimization goal classification.

    Members:
        MINIMUM_WEIGHT: Minimize Maximum Take-Off Weight (MTOW) and structural mass.
        MINIMUM_COST: Minimize total component bill of materials (BOM) cost.
        MAXIMUM_FLIGHT_TIME: Maximize endurance time (minutes).
        MAXIMUM_RANGE: Maximize operational range (kilometers).
        MAXIMUM_PAYLOAD: Maximize payload capacity mass.
        MAXIMUM_EFFICIENCY: Maximize energy and aerodynamic efficiency.
        BALANCED_DESIGN: Multi-objective trade-off balance across all metrics.
        CUSTOM: User-defined custom optimization goal objective.
    """
    MINIMUM_WEIGHT = "MINIMUM_WEIGHT"
    MINIMUM_COST = "MINIMUM_COST"
    MAXIMUM_FLIGHT_TIME = "MAXIMUM_FLIGHT_TIME"
    MAXIMUM_RANGE = "MAXIMUM_RANGE"
    MAXIMUM_PAYLOAD = "MAXIMUM_PAYLOAD"
    MAXIMUM_EFFICIENCY = "MAXIMUM_EFFICIENCY"
    BALANCED_DESIGN = "BALANCED_DESIGN"
    CUSTOM = "CUSTOM"
