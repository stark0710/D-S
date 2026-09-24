"""
MissionDomain Domain Model

Purpose:
    Defines the `MissionDomain` domain model representing the highest-level mission domain grouping
    within the Torq Wings Design Studio backend.

Role in Architecture:
    `MissionDomain` is the canonical software representation of a top-level mission domain
    (e.g., Agriculture, Cargo Delivery, Surveillance, Mapping, Search & Rescue, Defense).
    It extends `KnowledgeEntity` and groups together related Mission Categories by storing their IDs,
    maintaining strict framework independence and loose coupling.
"""

from dataclasses import dataclass, field
from backend.models.knowledge_entity import KnowledgeEntity


@dataclass(slots=True)
class MissionDomain(KnowledgeEntity):
    """
    Canonical domain model for a Mission Domain in Torq Wings Design Studio.

    Inherits baseline identity attributes (`id`, `name`, `description`) from `KnowledgeEntity`
    and links to child Mission Categories strictly by ID references.

    Architectural Boundaries:
        - Represents a top-level mission classification in the Mission Knowledge Base.
        - References child Mission Categories exclusively via string IDs (`category_ids`).
        - Does NOT represent a mission profile, user mission, design project, or flight plan.
        - Completely independent of database schemas, REST APIs, AI logic, and parsers.

    Attributes:
        id (str): Unique mission domain identifier (inherited from KnowledgeEntity).
        name (str): Human-readable mission domain name (inherited from KnowledgeEntity).
        description (str): Detailed description of the mission domain (inherited from KnowledgeEntity).
        category_ids (list[str]): List of Mission Category IDs belonging to this domain.
    """

    # References to child Mission Categories strictly by identifier
    category_ids: list[str] = field(default_factory=list)
