"""
MarkdownParser Implementation

Purpose:
    Defines the `MarkdownParser` class, a concrete implementation of the `Parser` interface
    responsible for orchestrating document parsing based on `RepositoryDocument.document_type`.

Role in Architecture:
    `MarkdownParser` acts as a dispatcher within the Markdown Parsing Engine. It receives a
    `RepositoryDocument`, inspects its classified `document_type`, and routes the document to a
    specialized parsing method (e.g., `_parse_engineering_parameter`, `_parse_mission_domain`,
    `_parse_mission_category`, `_parse_readme`). At this stage, detailed markdown section extraction
    is deferred to subsequent sprints.
"""

from backend.knowledge.parser.parser import Parser
from backend.models.repository_document import RepositoryDocument
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.engineering_parameter import EngineeringParameter
from backend.models.mission_domain import MissionDomain
from backend.models.mission_category import MissionCategory


class UnsupportedDocumentTypeError(ValueError):
    """Raised when MarkdownParser encounters an unclassifiable or unsupported document type."""
    pass


class MarkdownParser(Parser):
    """
    Concrete parser that dispatches repository documents to specialized parsing methods.

    Responsibilities:
        - Orchestrate parsing by inspecting `document.document_type`.
        - Dispatch to specialized private parsing methods for supported entity types.
        - Raise descriptive errors when encountering unsupported or unknown document types.

    Design Principles:
        - Single Responsibility Principle (SRP): Acts solely as a document type parser orchestrator.
        - Open/Closed Principle (OCP): New document types can be supported by adding focused handler methods.

    Current Limitations:
        - Placeholder parsing: Detailed regex, front matter extraction, and markdown AST parsing
          will be implemented in future C5 steps.
    """

    def parse(self, document: RepositoryDocument) -> KnowledgeEntity:
        """
        Parses a RepositoryDocument by dispatching to the appropriate specialized parsing method.

        Args:
            document (RepositoryDocument): The document metadata instance to parse.

        Returns:
            KnowledgeEntity: The resulting parsed domain model instance.

        Raises:
            UnsupportedDocumentTypeError: If document.document_type is unknown or unsupported.
        """
        doc_type = document.document_type.lower() if document.document_type else ""

        if doc_type == "engineering_parameter":
            return self._parse_engineering_parameter(document)
        elif doc_type == "mission_domain":
            return self._parse_mission_domain(document)
        elif doc_type == "mission_category":
            return self._parse_mission_category(document)
        elif doc_type == "readme":
            return self._parse_readme(document)
        else:
            raise UnsupportedDocumentTypeError(
                f"Unsupported document_type '{document.document_type}' for document '{document.file_name}' "
                f"at path '{document.path}'. Supported types are: 'engineering_parameter', 'mission_domain', "
                f"'mission_category', 'readme'."
            )

    def _parse_engineering_parameter(self, document: RepositoryDocument) -> EngineeringParameter:
        """
        Specialized handler for parsing Engineering Parameter markdown documents.

        Args:
            document (RepositoryDocument): Metadata of the parameter document.

        Returns:
            EngineeringParameter: Parsed EngineeringParameter domain object placeholder.
        """
        entity_id = document.file_name.removesuffix(".md")
        return EngineeringParameter(
            id=entity_id,
            name=document.file_name,
            description=f"Placeholder for EngineeringParameter from {document.file_name}",
            library="UNPARSED",
            parameter_group="UNPARSED",
            engineering_classification="UNPARSED",
        )

    def _parse_mission_domain(self, document: RepositoryDocument) -> MissionDomain:
        """
        Specialized handler for parsing Mission Domain markdown documents.

        Args:
            document (RepositoryDocument): Metadata of the mission domain document.

        Returns:
            MissionDomain: Parsed MissionDomain domain object placeholder.
        """
        entity_id = document.file_name.removesuffix(".md")
        return MissionDomain(
            id=entity_id,
            name=document.file_name,
            description=f"Placeholder for MissionDomain from {document.file_name}",
            category_ids=[],
        )

    def _parse_mission_category(self, document: RepositoryDocument) -> MissionCategory:
        """
        Specialized handler for parsing Mission Category markdown documents.

        Args:
            document (RepositoryDocument): Metadata of the mission category document.

        Returns:
            MissionCategory: Parsed MissionCategory domain object placeholder.
        """
        entity_id = document.file_name.removesuffix(".md")
        return MissionCategory(
            id=entity_id,
            name=document.file_name,
            description=f"Placeholder for MissionCategory from {document.file_name}",
            domain_id="UNPARSED",
            objective="UNPARSED",
            engineering_parameter_ids=[],
        )

    def _parse_readme(self, document: RepositoryDocument) -> KnowledgeEntity:
        """
        Specialized handler for parsing directory README markdown documents.

        Args:
            document (RepositoryDocument): Metadata of the readme document.

        Returns:
            KnowledgeEntity: Parsed base KnowledgeEntity domain object placeholder.
        """
        entity_id = document.file_name.removesuffix(".md")
        return KnowledgeEntity(
            id=entity_id,
            name=document.file_name,
            description=f"Placeholder for Readme document from {document.file_name}",
        )
