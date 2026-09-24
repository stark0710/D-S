"""
VTOL Lift System Result Subsystem

Purpose:
    Defines the consolidated `LiftSystemResult` dataclass outputted by the lift system stage.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from backend.design.vtol.lift_system.lift_rotor_layout import LiftRotorLayout
from backend.design.vtol.lift_system.hover_thrust_analysis import HoverThrustAnalysis
from backend.design.vtol.lift_system.lift_power_analysis import LiftPowerAnalysis
from backend.design.vtol.lift_system.lift_redundancy import LiftRedundancyAnalysis
from backend.design.vtol.lift_system.lift_system_analysis import LiftSystemAnalysis

if TYPE_CHECKING:
    from backend.design.vtol.hover_performance.authoritative_hover import AuthoritativeHoverResult


@dataclass(slots=True)
class LiftSystemResult:
    """
    Consolidated lift system sizing result package.

    Attributes:
        lift_motor_selection (Dict[str, Any]): Selected brushless motor specs (advisory/catalog).
        lift_propeller_selection (Dict[str, Any]): Selected carbon propeller specs (advisory/catalog).
        rotor_layout (LiftRotorLayout): coordinates and torque orientations.
        hover_analysis (HoverThrustAnalysis): Sized thrust safety margins.
        power_analysis (LiftPowerAnalysis): Electric power draws and C-rates.
        redundancy_analysis (LiftRedundancyAnalysis): Engine out controllability.
        engineering_analysis (LiftSystemAnalysis): Disk loading metrics.
        authoritative_result (Optional[AuthoritativeHoverResult]): Unified authoritative hover physics.
        technical_requirements (Dict[str, Any]): Manufacturer-independent engineering requirements.
        engineering_notes (List[str]): Sizing observations.
        recommendations (List[str]): Downstream recommendations.
        warnings (List[str]): Safety/thermal warnings.
        metadata (Dict[str, Any]): execution timestamps and versions.
    """

    lift_motor_selection: Dict[str, Any]
    lift_propeller_selection: Dict[str, Any]
    rotor_layout: LiftRotorLayout
    hover_analysis: HoverThrustAnalysis
    power_analysis: LiftPowerAnalysis
    redundancy_analysis: LiftRedundancyAnalysis
    engineering_analysis: LiftSystemAnalysis
    authoritative_result: Optional[AuthoritativeHoverResult] = None
    technical_requirements: Dict[str, Any] = field(default_factory=dict)
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
