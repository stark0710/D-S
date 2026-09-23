"""
VTOL Mission Result Subsystem

Purpose:
    Defines the consolidated `MissionResult` dataclass outputted by the framework.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.design.vtol.mission.mission_profile import MissionProfile
from backend.design.vtol.mission.hover_requirements import HoverRequirements
from backend.design.vtol.mission.transition_requirements import TransitionRequirements
from backend.design.vtol.mission.cruise_requirements import CruiseRequirements
from backend.design.vtol.mission.mission_analysis import MissionAnalysis
from backend.design.vtol.mission.mission_state import VTOLMissionProfileSequence


@dataclass(slots=True)
class MissionResult:
    """
    Consolidated output containing validated requirements, profiles, analyses, and recommendations.

    Attributes:
        mission_profile (MissionProfile): Computed mission parameters.
        hover_requirements (HoverRequirements): Sizing inputs for hover regime.
        transition_requirements (TransitionRequirements): Sizing inputs for transition regime.
        cruise_requirements (CruiseRequirements): Sizing inputs for cruise regime.
        mission_analysis (MissionAnalysis): Sized flight regime characteristics.
        mission_sequence (Optional[VTOLMissionProfileSequence]): Full 10-phase mission sequence representation.
        engineering_notes (List[str]): Design observations and notes.
        recommendations (List[str]): Strategic suggestions for downstream sizing.
        warnings (List[str]): Operational risk warnings or deficiencies.
        metadata (Dict[str, Any]): Framework versions and execution details.
    """

    mission_profile: MissionProfile
    hover_requirements: HoverRequirements
    transition_requirements: TransitionRequirements
    cruise_requirements: CruiseRequirements
    mission_analysis: MissionAnalysis
    mission_sequence: Optional[VTOLMissionProfileSequence] = None
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
