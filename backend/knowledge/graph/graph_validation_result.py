"""
GraphValidationResult Subsystem

Purpose:
    Defines the `GraphValidationResult` dataclass returned by `GraphValidator`.

Role in Architecture:
    `GraphValidationResult` encapsulates structural validation status (`is_valid`), recorded
    error messages (`errors`), non-fatal warnings (`warnings`), and topological metrics (`statistics`)
    for a `KnowledgeGraph`.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GraphValidationResult:
    """
    Validation result and diagnostic report for a KnowledgeGraph instance.

    Attributes:
        is_valid (bool): True if no validation errors were detected; False otherwise.
        errors (list[str]): List of structural validation error messages.
        warnings (list[str]): List of non-fatal structural warning messages (e.g., duplicate edges, isolated nodes).
        statistics (dict[str, Any]): Topological statistics (entity_count, edge_count, isolated_nodes, average_degree, etc.).
    """

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
