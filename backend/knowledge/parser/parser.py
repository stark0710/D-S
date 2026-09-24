"""
Parser Abstract Interface

Purpose:
    Defines the abstract base contract for all document parser implementations within the
    Torq Wings Engineering Knowledge Platform.

Role in Architecture:
    `Parser` establishes a clean architectural boundary using the Dependency Inversion
    Principle (DIP). Downstream knowledge platform services depend on this abstract interface
    to convert raw discovered `RepositoryDocument` metadata objects into strongly typed
    `KnowledgeEntity` domain models, remaining decoupled from concrete parser implementations.

Future Extensions:
    - `MarkdownParser`: Parses Markdown documents formatted according to EKB specifications.
    - `YAMLParser`: Parses YAML document specifications.
    - `JSONParser`: Parses JSON document specifications.
    - `XMLParser`: Parses XML engineering parameter schemas.
"""

from abc import ABC, abstractmethod
from backend.models.repository_document import RepositoryDocument
from backend.models.knowledge_entity import KnowledgeEntity


class Parser(ABC):
    """
    Abstract base class defining the contract for parsing repository documents into domain entities.

    Every concrete parser implementation (Markdown, YAML, JSON, etc.) must inherit from this
    class and implement the `parse` method.

    Responsibilities:
        - Declare the abstract parsing contract.
        - Enforce input (`RepositoryDocument`) and output (`KnowledgeEntity`) type signatures.

    Design Principles:
        - Dependency Inversion Principle (DIP): High-level knowledge services depend on this abstraction.
        - Single Responsibility Principle (SRP): Responsible solely for defining the parsing contract.
        - Open/Closed Principle (OCP): New parsers extend this interface without modifying existing code.
    """

    @abstractmethod
    def parse(self, document: RepositoryDocument) -> KnowledgeEntity:
        """
        Parses a single RepositoryDocument and returns its corresponding KnowledgeEntity domain model.

        Args:
            document (RepositoryDocument): Discovered document metadata instance.

        Returns:
            KnowledgeEntity: A concrete subclass of KnowledgeEntity (e.g., EngineeringParameter,
                             MissionDomain, MissionCategory).

        Raises:
            NotImplementedError: If invoked directly on the abstract base class.
        """
        pass
