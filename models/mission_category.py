"""
MissionCategory Domain Model

Purpose:
    Defines the `MissionCategory` domain model representing a specific mission type
    within the Torq Wings Design Studio backend.

Role in Architecture:
    `MissionCategory` acts as the critical conceptual bridge connecting Mission Knowledge
    to Engineering Knowledge. It links a specific mission category (e.g., Crop Spraying,
    Parcel Delivery, Pipeline Inspection, Border Surveillance) to its parent `MissionDomain`
    and references relevant `EngineeringParameter` entities strictly by string identifiers.
"""

from dataclasses import dataclass, field
from backend.models.knowledge_entity import KnowledgeEntity


@dataclass(slots=True)
class MissionCategory(KnowledgeEntity):
    """
    Canonical domain model for a Mission Category in Torq Wings Design Studio.

    Inherits baseline identity attributes (`id`, `name`, `description`) from `KnowledgeEntity`
    and connects mission intent with engineering domain parameters.

    Architectural Relationships:
        - Parent Domain: Linked to a parent `MissionDomain` via `domain_id`.
        - Engineering Knowledge Bridge: References associated `EngineeringParameter` instances
          strictly by ID list (`engineering_parameter_ids`), allowing downstream Relationship Resolvers
          to resolve actual entities cleanly without embedding objects here.

    Attributes:
        id (str): Unique mission category identifier (inherited from KnowledgeEntity).
        name (str): Human-readable mission category name (inherited from KnowledgeEntity).
        description (str): Detailed description of the mission category (inherited from KnowledgeEntity).
        domain_id (str): ID of the parent MissionDomain to which this category belongs.
        objective (str): Primary operational objective or goal statement for this mission type.
        engineering_parameter_ids (list[str]): List of Engineering Parameter IDs required by this category.
    """

    # Domain linkage and primary objective
    domain_id: str
    objective: str

    # Soft references to associated Engineering Parameters
    engineering_parameter_ids: list[str] = field(default_factory=list)
