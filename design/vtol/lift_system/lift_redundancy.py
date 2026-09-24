"""
VTOL Lift System Redundancy Subsystem

Purpose:
    Defines the `LiftRedundancyAnalysis` class modeling motor failures and margins.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class LiftRedundancyAnalysis:
    """
    Rotor failure fault tolerance and engine-out controllability.

    Attributes:
        redundancy_level (str): Controllability rating (e.g. Single motor failure safe).
        has_engine_out_capability (bool): True if remaining motors can support MTOW.
        motor_out_thrust_reserve_fraction (float): Sized thrust reserve fraction with one engine out.
        failure_scenarios_tested (List[str]): List of failures analyzed (e.g. Front Left Motor Out).
        metadata (Dict[str, Any]): Additional fail-safe metrics.
    """

    redundancy_level: str
    has_engine_out_capability: bool
    motor_out_thrust_reserve_fraction: float
    failure_scenarios_tested: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
