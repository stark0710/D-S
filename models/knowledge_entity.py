"""
KnowledgeEntity Base Domain Model

Purpose:
    This file defines the foundational `KnowledgeEntity` base domain model for the Torq Wings
    Design Studio backend.

Role in Architecture:
    `KnowledgeEntity` serves as the core base class for the entire Engineering Knowledge Platform.
    It establishes the minimum identity contract shared by all engineering objects in the system
    (e.g., Engineering Parameters, Mission Domains, Categories, Aircraft Platforms, Rules,
    Components, and Constraints), ensuring domain consistency while remaining entirely decoupled
    from frameworks, data sources, and infrastructure.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class KnowledgeEntity:
    """
    Base domain model for all engineering knowledge entities in Torq Wings.

    This class serves as the foundational identity model from which every engineering object
    inherits. It captures only the essential identity attributes shared across all domain objects.

    Key Attributes & Characteristics:
        - Base Domain Model: Provides identity (id, name, description) for engineering knowledge.
        - Inherited by All Entities: Parametric models, platforms, rules, and components inherit from it.
        - Framework Independent: Completely decoupled from parsers, APIs, databases, ORMs, and AI engines.
        - Extensible: Child domain classes extend this entity with domain-specific attributes and rules.
    """

    # Essential identity attributes shared by all domain entities
    id: str
    name: str
    description: str
