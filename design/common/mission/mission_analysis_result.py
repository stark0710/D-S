"""
MissionAnalysisResult Subsystem

Purpose:
    Defines the `MissionAnalysisResult` domain model returned by `MissionAnalysisService`.

Role in Architecture:
    `MissionAnalysisResult` encapsulates the constructed `MissionProfile` alongside analysis notes
    and execution diagnostic metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.mission.mission_profile import MissionProfile


@dataclass(slots=True)
class MissionAnalysisResult:
    """
    Diagnostic output returned by MissionAnalysisService.

    Attributes:
        mission_profile (MissionProfile): Constructed engineering mission profile object.
        analysis_notes (list[str]): Detailed human-readable notes detailing engineering assessments.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    mission_profile: MissionProfile
    analysis_notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
