"""
VTOL Forward Propulsion Result Subsystem

Purpose:
    Defines the consolidated `ForwardPropulsionResult` dataclass outputted by the stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.design.vtol.forward_propulsion.propulsion_layout import ForwardPropulsionLayout
from backend.design.vtol.forward_propulsion.forward_propulsion_analysis import ForwardPropulsionAnalysis
from backend.design.vtol.forward_propulsion.cruise_power_analysis import CruisePowerAnalysis
from backend.design.vtol.forward_propulsion.cruise_performance_analysis import CruisePerformanceAnalysis


@dataclass(slots=True)
class ForwardPropulsionResult:
    """
    Consolidated forward flight propulsion sizing package.

    Attributes:
        motor_selection (Dict[str, Any]): Sized cruise motor specifications.
        propeller_selection (Dict[str, Any]): Sized cruise propeller specifications.
        esc_selection (Dict[str, Any]): Sized ESC specifications.
        propulsion_layout (ForwardPropulsionLayout): installation locations.
        cruise_analysis (ForwardPropulsionAnalysis): Thrust and drag metrics.
        power_analysis (CruisePowerAnalysis): Amps, watts, and C-rates.
        performance_analysis (CruisePerformanceAnalysis): Airspeed envelopes and rate of climb.
        engineering_notes (List[str]): Sizing observations.
        recommendations (List[str]): Sizing recommendations.
        warnings (List[str]): Clearance or power warnings.
        metadata (Dict[str, Any]): Execution timestamps and versions.
    """

    motor_selection: Dict[str, Any]
    propeller_selection: Dict[str, Any]
    esc_selection: Dict[str, Any]
    propulsion_layout: ForwardPropulsionLayout
    cruise_analysis: ForwardPropulsionAnalysis
    power_analysis: CruisePowerAnalysis
    performance_analysis: CruisePerformanceAnalysis
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
