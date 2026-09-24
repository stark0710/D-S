"""
ConfigurationCandidate Subsystem

Purpose:
    Defines the `ConfigurationCandidate` domain model representing a candidate multirotor architecture evaluated for a mission.

Role in Architecture:
    `ConfigurationCandidate` encapsulates a `ConfigurationProfile`, evaluated suitability score (0.0 to 1.0), assigned rank,
    engineering justification, trade-offs, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.configuration.configuration_profile import ConfigurationProfile


@dataclass(slots=True)
class ConfigurationCandidate:
    """
    Evaluated multirotor configuration candidate.

    Attributes:
        profile (ConfigurationProfile): Multirotor frame architecture definition.
        suitability_score (float): Quantitative suitability score normalized between 0.0 and 1.0.
        rank (int): Assigned ordinal rank position (1 = top choice).
        justification (str): Technical explanation for assigned score and rank.
        tradeoffs (list[str]): Key trade-off points for selecting this configuration.
        metadata (dict[str, Any]): Additional candidate diagnostic metadata.
    """

    profile: ConfigurationProfile
    suitability_score: float = 0.0
    rank: int = 0
    justification: str = ""
    tradeoffs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
