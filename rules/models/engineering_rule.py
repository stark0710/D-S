"""
EngineeringRule Domain Model Subsystem

Purpose:
    Defines the `EngineeringRule` domain model and `RuleSeverity` enumeration representing executable
    engineering constraints, safety boundaries, recommendations, and compatibility rules.

Role in Architecture:
    `EngineeringRule` extends `KnowledgeEntity` to serve as the canonical representation of engineering constraints
    throughout the Torq Wings Design Studio backend. It provides structured metadata and declarative condition
    expressions consumed by downstream engines (Rule Engine, Constraint Engine, Compatibility Engine, Design Engine,
    and Optimization Engine) while remaining completely decoupled from evaluation logic and infrastructure.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any
from backend.models.knowledge_entity import KnowledgeEntity


class RuleSeverity(str, Enum):
    """
    Enumeration of rule violation severity levels.

    Members:
        INFO: Informational recommendation or advisory note.
        WARNING: Non-critical constraint violation or sub-optimal parameter choice.
        ERROR: Significant engineering violation requiring design modification.
        CRITICAL: Catastrophic safety or structural failure condition.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(slots=True)
class EngineeringRule(KnowledgeEntity):
    """
    Canonical domain model for an Engineering Rule in Torq Wings Design Studio.

    Inherits baseline identity attributes (`id`, `name`, `description`) from `KnowledgeEntity`
    and extends them with rule classification, severity, condition logic, and diagnostic message metadata.

    Attributes:
        id (str): Unique rule identifier (inherited from KnowledgeEntity).
        name (str): Human-readable rule name (inherited from KnowledgeEntity).
        description (str): Detailed explanation of rule purpose (inherited from KnowledgeEntity).
        category (str): Subsystem or domain classification (e.g., 'Electrical', 'Aerodynamics', 'Safety').
        severity (RuleSeverity): Violation severity level (INFO, WARNING, ERROR, CRITICAL).
        condition (str): Declarative expression representation (e.g., 'motor.current <= esc.max_current').
        message (str): User-facing explanation displayed when the rule condition fails.
        metadata (dict[str, Any]): Additional implementation or execution metadata.

    Design Principles:
        - Pure Domain Model: Contains no expression evaluation or graph traversal logic.
        - Framework Independent: Decoupled from databases, parsers, and execution engines.
    """

    category: str
    severity: RuleSeverity
    condition: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
