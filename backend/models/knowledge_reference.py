"""
KnowledgeReference Domain Model

Purpose:
    Defines the `KnowledgeReference` domain model representing document provenance and source tracking
    within the Torq Wings Design Studio backend.

Role in Architecture:
    `KnowledgeReference` captures where an engineering knowledge entity originated (e.g., source document,
    external engineering standard, research paper, or internal spec). While `KnowledgeRelationship`
    models semantic connections between domain objects, `KnowledgeReference` strictly records
    documentary provenance and traceability.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class KnowledgeReference:
    """
    Domain model representing documentation provenance and origin metadata for a knowledge entity.

    Does NOT inherit from `KnowledgeEntity` because a reference is source tracking metadata
    rather than a domain entity identity.

    Architectural Distinction:
        - Provenance vs. Relationship: Tracks document source origins rather than semantic graph connections.
        - Traceability: Enables auditing of engineering knowledge back to authoritative markdown specs or standards.
        - Framework Independent: Pure dataclass decoupled from filesystems, parsers, DBs, and APIs.

    Attributes:
        entity_id (str): Unique identifier of the associated knowledge entity (e.g., 'MP-001-001').
        entity_type (str): Type classification of the entity (e.g., 'EngineeringParameter').
        source_document (str): Path, URI, or title of the originating source document or specification.
        reference_type (str): Nature of the reference (e.g., 'SourceDocument', 'Standard', 'Specification').
    """

    entity_id: str
    entity_type: str
    source_document: str
    reference_type: str
