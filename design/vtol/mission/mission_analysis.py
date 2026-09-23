"""
VTOL Mission Analysis Subsystem

Purpose:
    Defines the `MissionAnalysis` dataclass storing prioritization,
    mass estimates, risk scoring, and expected aerodynamic coefficients.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class MissionAnalysis:
    """
    Subsystem-level analysis results of a VTOL mission.

    Attributes:
        hover_priority (float): Relative emphasis of hover capability (0.0 to 1.0).
        cruise_priority (float): Relative emphasis of cruise range capability (0.0 to 1.0).
        transition_complexity (float): Complexity rating of transition phase (0.0 to 1.0).
        estimated_mtow_kg (float): Preliminary estimate of Maximum Takeoff Weight.
        lift_to_drag_ratio_est (float): Estimated aerodynamic Lift-to-Drag ratio at cruise.
        hover_thrust_to_weight_est (float): Required hover thrust-to-weight safety margin.
        mission_energy_demand_kwh (float): Sized total electrical/fuel energy demand in kWh.
        mission_risk_score (float): Evaluated operational risk index (0.0 to 1.0).
        mission_feasibility_score (float): Suitability score for the mission profile (0.0 to 100.0).
        metadata (Dict[str, Any]): Intermediate physics results.
    """

    hover_priority: float
    cruise_priority: float
    transition_complexity: float
    estimated_mtow_kg: float
    lift_to_drag_ratio_est: float
    hover_thrust_to_weight_est: float
    mission_energy_demand_kwh: float
    mission_risk_score: float
    mission_feasibility_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
