"""
ComponentSelectionResult Subsystem

Purpose:
    Defines the `ComponentSelectionResult` domain model representing the output of a component selection query.

Role in Architecture:
    `ComponentSelectionResult` encapsulates the winning `ComponentCandidate` (if found), the full list of ranked candidate options,
    selection summary text, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.component_candidate import ComponentCandidate


@dataclass(slots=True)
class ComponentSelectionResult:
    """
    Component selection query result summary.

    Attributes:
        selected_component (ComponentCandidate | None): Top-ranked winning component candidate, or None if no candidate matched.
        candidates (list[ComponentCandidate]): All evaluated component candidates sorted by score descending.
        selection_summary (str): Transparent human-readable summary of selection rationale.
        metadata (dict[str, Any]): Additional diagnostic execution metadata.
    """

    selected_component: ComponentCandidate | None
    candidates: list[ComponentCandidate] = field(default_factory=list)
    selection_summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
