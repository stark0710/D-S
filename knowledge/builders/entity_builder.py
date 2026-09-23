"""
EntityBuilder Abstract Framework Interface

Purpose:
    Defines the `EntityBuilder` abstract base class contract for all domain entity builders within the
    Torq Wings Engineering Knowledge Platform.

Role in Architecture:
    `EntityBuilder` establishes a clean architectural boundary using the Dependency Inversion
    Principle (DIP). Downstream entity construction services depend on this abstract interface
    to transform generic `ParsedDocument` intermediate representations into strongly typed
    `KnowledgeEntity` domain models, remaining decoupled from specific entity construction algorithms.

Future Extensions:
    - `EngineeringParameterBuilder`: Constructs `EngineeringParameter` domain instances.
    - `MissionDomainBuilder`: Constructs `MissionDomain` domain instances.
    - `MissionCategoryBuilder`: Constructs `MissionCategory` domain instances.
    - `EngineeringLibraryBuilder`: Constructs library domain models.
    - `EngineeringStandardBuilder`: Constructs standard and specification models.
"""

from abc import ABC, abstractmethod
from backend.models.parsed_document import ParsedDocument
from backend.models.knowledge_entity import KnowledgeEntity


class EntityBuilder(ABC):
    """
    Abstract base class defining the contract for building domain entities from ParsedDocument instances.

    Every concrete entity builder implementation (e.g., EngineeringParameterBuilder,
    MissionDomainBuilder) must inherit from this class and implement the `build` method.

    Responsibilities:
        - Declare the abstract entity construction contract.
        - Enforce input (`ParsedDocument`) and output (`KnowledgeEntity`) signatures.

    Design Principles:
        - Dependency Inversion Principle (DIP): High-level entity services depend on this abstraction.
        - Single Responsibility Principle (SRP): Responsible solely for defining the entity build contract.
        - Open/Closed Principle (OCP): New entity builders extend this interface without modifying existing code.
    """

    @abstractmethod
    def build(self, document: ParsedDocument) -> KnowledgeEntity:
        """
        Transforms a ParsedDocument into a strongly typed KnowledgeEntity domain model.

        Args:
            document (ParsedDocument): The intermediate parsed document structure.

        Returns:
            KnowledgeEntity: A concrete subclass of KnowledgeEntity (e.g., EngineeringParameter,
                             MissionDomain, MissionCategory).

        Raises:
            NotImplementedError: If invoked directly on the abstract base class.
        """
        pass
