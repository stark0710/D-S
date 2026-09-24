"""
ComponentSelectionRequest Subsystem

Purpose:
    Defines the `ComponentSelectionRequest` domain model representing a query for component selection.

Role in Architecture:
    `ComponentSelectionRequest` encapsulates category target, performance requirements, physical constraints,
    filtering criteria, and metadata sent to `ComponentSelectionPipeline`.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.component_category import ComponentCategory


@dataclass(slots=True)
class ComponentSelectionRequest:
    """
    Component selection query request.

    Attributes:
        category (ComponentCategory): Target component category (e.g. MOTOR, ESC, BATTERY).
        requirements (dict[str, Any]): Performance targets (e.g., {'thrust_g': 1200, 'voltage_v': 22.2}).
        constraints (dict[str, Any]): Physical/hard constraints (e.g., {'max_weight_g': 150}).
        filters (dict[str, Any]): Filtering criteria (e.g., {'brand': 'T-Motor'}).
        metadata (dict[str, Any]): Additional query context metadata.
    """

    category: ComponentCategory
    requirements: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    filters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
