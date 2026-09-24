"""
ComponentCandidate Subsystem

Purpose:
    Defines the `ComponentCandidate` domain model representing an evaluated component candidate option.

Role in Architecture:
    `ComponentCandidate` pairs raw component data dictionary or entity with calculated suitability scores,
    compatibility metrics, selection notes, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ComponentCandidate:
    """
    Evaluated component candidate option.

    Attributes:
        component (dict[str, Any]): Raw component database record or entity dictionary.
        score (float): Normalized overall match score from 0.0 to 1.0.
        compatibility_score (float): Normalized physical/electrical compatibility score from 0.0 to 1.0.
        selection_notes (list[str]): Technical notes regarding evaluation findings.
        metadata (dict[str, Any]): Additional candidate metadata.
    """

    component: dict[str, Any]
    score: float
    compatibility_score: float
    selection_notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
