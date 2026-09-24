"""
KnowledgeEngine Top-Level Orchestration Subsystem

Purpose:
    Defines the `KnowledgeEngine` class, which serves as the primary top-level entry point into the
    Engineering Knowledge Platform.

Role in Architecture:
    `KnowledgeEngine` orchestrates the complete end-to-end knowledge loading workflow:
        1. Discovery: Uses `RepositoryLoader` to discover repository documents.
        2. Indexing: Constructs `RepositoryIndex` in memory.
        3. Structural Validation: Validates repository integrity via `RepositoryValidator`.
        4. Parsing: Converts `RepositoryDocument` objects into `ParsedDocument` instances using `DocumentParsingPipeline`.
        5. Entity Construction: Converts `ParsedDocument` instances into strongly typed `KnowledgeEntity` models using `EntityConstructionPipeline`.
    It relies entirely on injected collaborator dependencies and contains no direct file I/O, parsing, or domain logic.
"""

from typing import Callable, Type
from backend.models.knowledge_entity import KnowledgeEntity
from backend.knowledge.loader.repository_loader import RepositoryLoader
from backend.knowledge.repository_index import RepositoryIndex
from backend.knowledge.repository_validator import RepositoryValidator, ValidationResult
from backend.knowledge.parser.document_parsing_pipeline import DocumentParsingPipeline
from backend.knowledge.builders.entity_construction_pipeline import EntityConstructionPipeline


class RepositoryValidationError(ValueError):
    """Raised when repository structural validation fails during KnowledgeEngine execution."""
    pass


class KnowledgeEngine:
    """
    Primary orchestration engine for loading the Engineering Knowledge Platform into memory.

    Workflow:
        1. Discover repository documents via `RepositoryLoader`.
        2. Catalog documents in a `RepositoryIndex`.
        3. Validate repository structure using `RepositoryValidator`.
        4. Parse each document into a `ParsedDocument` via `DocumentParsingPipeline`.
        5. Construct domain entities via `EntityConstructionPipeline`.
        6. Return list of instantiated `KnowledgeEntity` objects.

    Design Principles:
        - Single Responsibility Principle (SRP): Top-level workflow orchestration only.
        - Dependency Injection: All collaborators injected via constructor.
        - Clean Architecture & DIP: Decoupled from filesystem details and concrete builder logic.
    """

    def __init__(
        self,
        loader: RepositoryLoader,
        validator_factory: Type[RepositoryValidator] | Callable[[RepositoryIndex], RepositoryValidator],
        parse_pipeline: DocumentParsingPipeline,
        construct_pipeline: EntityConstructionPipeline,
    ) -> None:
        """
        Initializes the KnowledgeEngine with injected collaborator dependencies.

        Args:
            loader (RepositoryLoader): Injected repository document loader.
            validator_factory (Type[RepositoryValidator] | Callable[[RepositoryIndex], RepositoryValidator]):
                Factory or class used to instantiate a RepositoryValidator for a RepositoryIndex.
            parse_pipeline (DocumentParsingPipeline): Injected document parsing pipeline.
            construct_pipeline (EntityConstructionPipeline): Injected entity construction pipeline.
        """
        self._loader: RepositoryLoader = loader
        self._validator_factory = validator_factory
        self._parse_pipeline: DocumentParsingPipeline = parse_pipeline
        self._construct_pipeline: EntityConstructionPipeline = construct_pipeline

    def load_repository(self) -> list[KnowledgeEntity]:
        """
        Executes the complete knowledge platform loading pipeline and returns all parsed engineering entities.

        Returns:
            list[KnowledgeEntity]: List of constructed engineering domain entities.

        Raises:
            RepositoryValidationError: If repository structural validation fails.
            DocumentReadError: If document reading fails.
            FrontMatterParseError: If YAML metadata parsing fails.
            UnregisteredBuilderError: If a document type has no registered builder and fails construction.
        """
        # Step 1: Discover repository documents
        documents = self._loader.discover_documents()

        # Step 2: Build in-memory RepositoryIndex
        index = RepositoryIndex(documents)

        # Step 3: Validate repository structure
        validator = self._validator_factory(index)
        validation_result: ValidationResult = validator.validate()

        if not validation_result.valid:
            error_msg = "; ".join(validation_result.errors)
            raise RepositoryValidationError(
                f"Repository validation failed with {len(validation_result.errors)} error(s): {error_msg}"
            )

        # Step 4: Parse documents and construct engineering entities for registered types
        entities: list[KnowledgeEntity] = []
        for doc in index.get_all_documents():
            if not self._construct_pipeline.has_builder(doc.document_type):
                continue

            parsed_doc = self._parse_pipeline.parse(doc)
            entity = self._construct_pipeline.construct(parsed_doc)
            entities.append(entity)

        return entities
