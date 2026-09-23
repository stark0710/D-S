"""
EntityConstructionPipeline Orchestration Subsystem

Purpose:
    Defines the `EntityConstructionPipeline` class responsible for orchestrating the conversion of
    a `ParsedDocument` intermediate representation into a strongly typed `KnowledgeEntity` domain model.

Role in Architecture:
    `EntityConstructionPipeline` acts as the primary construction orchestration pipeline within the Entity Construction Engine.
    It receives an injected `BuilderRegistry`, inspects `document.repository_document.document_type`,
    retrieves the matching concrete `EntityBuilder`, and delegates domain entity creation.
"""

from backend.models.parsed_document import ParsedDocument
from backend.models.knowledge_entity import KnowledgeEntity
from backend.knowledge.builders.builder_registry import BuilderRegistry


class EntityConstructionPipeline:
    """
    Orchestration pipeline that delegates ParsedDocument construction to registered EntityBuilder instances.

    Workflow:
        1. Inspect `document.repository_document.document_type`.
        2. Look up the registered `EntityBuilder` from the injected `BuilderRegistry`.
        3. Invoke `builder.build(document)` to construct the domain model.
        4. Return the resulting `KnowledgeEntity` instance.

    Design Principles:
        - Dependency Injection: `BuilderRegistry` is injected via the constructor.
        - Single Responsibility Principle (SRP): Responsible solely for construction orchestration.
        - Open/Closed Principle (OCP): Works with any present or future registered builder without code changes.
    """

    def __init__(self, registry: BuilderRegistry) -> None:
        """
        Initializes the EntityConstructionPipeline with an injected BuilderRegistry dependency.

        Args:
            registry (BuilderRegistry): Injected builder registry instance.
        """
        self._registry: BuilderRegistry = registry

    def construct(self, document: ParsedDocument) -> KnowledgeEntity:
        """
        Constructs a KnowledgeEntity domain object from a ParsedDocument.

        Args:
            document (ParsedDocument): The parsed intermediate document instance.

        Returns:
            KnowledgeEntity: The constructed domain model object.

        Raises:
            UnregisteredBuilderError: If no builder is registered for document.repository_document.document_type.
        """
        doc_type = document.repository_document.document_type
        builder = self._registry.get_builder(doc_type)
        return builder.build(document)

    def has_builder(self, document_type: str) -> bool:
        """
        Checks whether a builder is registered in the registry for the specified document type.

        Args:
            document_type (str): Classification string to check.

        Returns:
            bool: True if a builder is registered; False otherwise.
        """
        return self._registry.has_builder(document_type)
