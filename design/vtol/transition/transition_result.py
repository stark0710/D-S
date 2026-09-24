from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .transition_profile import TransitionProfile
from .transition_scheduler import TransitionSchedule
from .transition_control import ControlSchedule
from .transition_stability import StabilityAnalysis
from .transition_aerodynamics import AerodynamicAnalysis
from .transition_propulsion import PropulsionAnalysis
from .transition_energy import EnergyAnalysis
from .transition_failure_analysis import FailureAnalysis
from .transition_analysis import TransitionAnalysis

if TYPE_CHECKING:
    from .authoritative_transition import AuthoritativeTransitionResult

@dataclass(slots=True)
class TransitionResult:
    """
    Consolidated outputs of the VTOL Transition Flight Engineering pipeline.
    """
    transition_profile: TransitionProfile
    transition_schedule: TransitionSchedule
    flight_mode_schedule: ControlSchedule  # Maps logic scheduler schedules
    control_schedule: ControlSchedule
    stability_analysis: StabilityAnalysis
    aerodynamic_analysis: AerodynamicAnalysis
    propulsion_analysis: PropulsionAnalysis
    energy_analysis: EnergyAnalysis
    failure_analysis: FailureAnalysis
    transition_analysis: TransitionAnalysis

    authoritative_result: Optional[AuthoritativeTransitionResult] = None
    transition_corridor: List[Any] = field(default_factory=list)
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
