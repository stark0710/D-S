"""
Fixed-Wing Propulsion Result Subsystem

Purpose:
    Defines the `PropulsionResult` class representing the output of the propulsion design process.

Role in Architecture:
    `PropulsionResult` carries the selected motor, propeller, layout style, and
    detailed thrust, power, efficiency, cruise, climb, and takeoff analyses.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.propulsion.thrust_analysis import ThrustAnalysis
from backend.design.fixed_wing.propulsion.power_analysis import PowerAnalysis
from backend.design.fixed_wing.propulsion.efficiency_analysis import EfficiencyAnalysis
from backend.design.fixed_wing.propulsion.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.propulsion.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.propulsion.takeoff_analysis import TakeoffAnalysis


@dataclass(slots=True)
class PropulsionResult:
    """
    Consolidated output of the motor/engine, propeller, and performance analysis workflow.

    Attributes:
        selected_motor_or_engine (str): Name of selected brushless motor or gas engine.
        selected_propeller (str): Name of sized propeller (e.g. 12x6 APC).
        propulsion_layout (str): Layout style (e.g. Single Tractor, Twin Tractor).
        thrust_analysis (ThrustAnalysis): Static, takeoff, and cruise thrust ratings.
        power_analysis (PowerAnalysis): Power draw, cruise current, and throttle settings.
        efficiency_analysis (EfficiencyAnalysis): Motor, propeller, and system efficiencies.
        cruise_analysis (CruiseAnalysis): Cruise flight regime performance values.
        climb_analysis (ClimbAnalysis): Climb rate and time to altitude metrics.
        takeoff_analysis (TakeoffAnalysis): Ground run distance and acceleration duration.
        engineering_notes (List[str]): Sizing rationale and performance notes.
        recommendations (List[str]): Sizing layout tips.
        warnings (List[str]): Non-fatal warnings about thrust margins or propeller tip speeds.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    selected_motor_or_engine: str
    selected_propeller: str
    propulsion_layout: str
    thrust_analysis: ThrustAnalysis
    power_analysis: PowerAnalysis
    efficiency_analysis: EfficiencyAnalysis
    cruise_analysis: CruiseAnalysis
    climb_analysis: ClimbAnalysis
    takeoff_analysis: TakeoffAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
