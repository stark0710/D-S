"""
Fixed-Wing Flight Performance Result Subsystem

Purpose:
    Defines the `FlightResult` class representing the output of the flight performance analysis.

Role in Architecture:
    `FlightResult` carries flight speeds, glide ratios, climb/descent rate audits,
    range, endurance, ceilings, stable bank load factor, and mission completion probability.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.flight_performance.aerodynamic_analysis import AerodynamicAnalysis
from backend.design.fixed_wing.flight_performance.performance_analysis import PerformanceAnalysis
from backend.design.fixed_wing.flight_performance.takeoff_analysis import TakeoffAnalysis
from backend.design.fixed_wing.flight_performance.landing_analysis import LandingAnalysis
from backend.design.fixed_wing.flight_performance.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.flight_performance.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.flight_performance.descent_analysis import DescentAnalysis
from backend.design.fixed_wing.flight_performance.stall_analysis import StallAnalysis
from backend.design.fixed_wing.flight_performance.glide_analysis import GlideAnalysis
from backend.design.fixed_wing.flight_performance.turn_performance import TurnAnalysis
from backend.design.fixed_wing.flight_performance.range_analysis import RangeAnalysis
from backend.design.fixed_wing.flight_performance.endurance_analysis import EnduranceAnalysis
from backend.design.fixed_wing.flight_performance.ceiling_analysis import CeilingAnalysis
from backend.design.fixed_wing.flight_performance.stability_analysis import StabilityAnalysis
from backend.design.fixed_wing.flight_performance.mission_performance import MissionPerformance


@dataclass(slots=True)
class FlightResult:
    """
    Consolidated output of the flight performance, range, and stability simulation workflow.

    Attributes:
        aerodynamic_analysis (AerodynamicAnalysis): Lift and drag coefficient efficiency polars.
        performance_analysis (PerformanceAnalysis): Speeds (top speed, stall speed, range speeds).
        takeoff_analysis (TakeoffAnalysis): Ground roll acceleration run lengths.
        landing_analysis (LandingAnalysis): Ground roll deceleration braking lengths.
        climb_analysis (ClimbAnalysis): Vertical rate of climb capability.
        cruise_analysis (CruiseAnalysis): Cruise drag thrust and required engine power.
        descent_analysis (DescentAnalysis): Descent sink rate.
        stall_analysis (StallAnalysis): Clean and flap landing stall airspeeds.
        glide_analysis (GlideAnalysis): best glide ratio and unpowered sink rate.
        turn_analysis (TurnAnalysis): banking turn radius and load factors (G loads).
        range_analysis (RangeAnalysis): Maximum and operational travel range predictions.
        endurance_analysis (EnduranceAnalysis): Maximum and operational flight time predictions.
        ceiling_analysis (CeilingAnalysis): Service and absolute operational ceilings.
        stability_analysis (StabilityAnalysis): Longitudinal static stability margins.
        mission_performance (MissionPerformance): Completion probability and energy reserves.
        engineering_notes (List[str]): Sizing rationale notes.
        recommendations (List[str]): Sizing flight operation guidelines.
        warnings (List[str]): Non-fatal warnings about thrust limits or landing speeds.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    aerodynamic_analysis: AerodynamicAnalysis
    performance_analysis: PerformanceAnalysis
    takeoff_analysis: TakeoffAnalysis
    landing_analysis: LandingAnalysis
    climb_analysis: ClimbAnalysis
    cruise_analysis: CruiseAnalysis
    descent_analysis: DescentAnalysis
    stall_analysis: StallAnalysis
    glide_analysis: GlideAnalysis
    turn_analysis: TurnAnalysis
    range_analysis: RangeAnalysis
    endurance_analysis: EnduranceAnalysis
    ceiling_analysis: CeilingAnalysis
    stability_analysis: StabilityAnalysis
    mission_performance: MissionPerformance
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
"""
Fixed-Wing Flight Result model.
"""
