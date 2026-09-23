"""
ConfigurationResult Subsystem

Purpose:
    Defines the `ConfigurationResult` domain model representing output from the Drone Configuration Engineering Framework.

Role in Architecture:
    `ConfigurationResult` encapsulates the winning recommended `ConfigurationCandidate`, full candidate ranking list,
    engineering justification text, trade-offs, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.configuration.configuration_candidate import ConfigurationCandidate


@dataclass(slots=True)
class ConfigurationResult:
    """
    Multirotor configuration engineering evaluation output summary.

    Attributes:
        recommended_configuration (ConfigurationCandidate): Top Rank-1 winning multirotor configuration candidate.
        candidate_configurations (list[ConfigurationCandidate]): Ranked candidate list (highest rank first).
        engineering_justification (str): Detailed engineering rationale for the selection.
        tradeoffs (list[str]): Key system trade-off points considered during evaluation.
        warnings (list[str]): Non-fatal diagnostic warnings.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    recommended_configuration: ConfigurationCandidate
    candidate_configurations: list[ConfigurationCandidate]
    engineering_justification: str
    tradeoffs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
