"""
Unit tests for KnowledgeEngine.
"""

from pathlib import Path
import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.engineering_parameter import EngineeringParameter
from backend.knowledge.loader.filesystem_loader import FilesystemRepositoryLoader
from backend.knowledge.repository_index import RepositoryIndex
from backend.knowledge.repository_validator import RepositoryValidator
from backend.knowledge.parser.document_reader import DocumentReader
from backend.knowledge.parser.front_matter_parser import FrontMatterParser
from backend.knowledge.parser.markdown_section_parser import MarkdownSectionParser
from backend.knowledge.parser.document_parsing_pipeline import DocumentParsingPipeline
from backend.knowledge.builders.engineering_parameter_builder import EngineeringParameterBuilder
from backend.knowledge.builders.builder_registry import BuilderRegistry
from backend.knowledge.builders.entity_construction_pipeline import EntityConstructionPipeline
from backend.knowledge.knowledge_engine import KnowledgeEngine, RepositoryValidationError


def test_knowledge_engine_end_to_end(tmp_path: Path):
    """Verify KnowledgeEngine coordinates discovery, validation, parsing, and construction."""
    # Setup test workspace directory with valid markdown files
    param_file = tmp_path / "EP-001.md"
    param_file.write_text(
        "---\n"
        "id: EP-001\n"
        "name: Payload Weight\n"
        "unit: kg\n"
        "---\n\n"
        "# Payload Weight\n"
        "Payload capacity specification.\n",
        encoding="utf-8"
    )

    # 1. Setup loader
    loader = FilesystemRepositoryLoader(tmp_path)

    # 2. Setup parsing pipeline
    parse_pipeline = DocumentParsingPipeline(
        reader=DocumentReader(),
        front_matter_parser=FrontMatterParser(),
        section_parser=MarkdownSectionParser()
    )

    # 3. Setup registry & construction pipeline
    registry = BuilderRegistry()
    registry.register("engineering_parameter", EngineeringParameterBuilder())
    construct_pipeline = EntityConstructionPipeline(registry=registry)

    # 4. Instantiate KnowledgeEngine
    engine = KnowledgeEngine(
        loader=loader,
        validator_factory=RepositoryValidator,
        parse_pipeline=parse_pipeline,
        construct_pipeline=construct_pipeline
    )

    entities = engine.load_repository()

    assert len(entities) == 1
    entity = entities[0]
    assert isinstance(entity, EngineeringParameter)
    assert isinstance(entity, KnowledgeEntity)
    assert entity.id == "EP-001"
    assert entity.name == "Payload Weight"
    assert entity.unit == "kg"


def test_knowledge_engine_validation_failure(tmp_path: Path):
    """Verify KnowledgeEngine raises RepositoryValidationError when validation fails."""
    # Setup empty repository (triggers validation error)
    loader = FilesystemRepositoryLoader(tmp_path)
    parse_pipeline = DocumentParsingPipeline(
        reader=DocumentReader(),
        front_matter_parser=FrontMatterParser(),
        section_parser=MarkdownSectionParser()
    )
    registry = BuilderRegistry()
    registry.register("engineering_parameter", EngineeringParameterBuilder())
    construct_pipeline = EntityConstructionPipeline(registry=registry)

    engine = KnowledgeEngine(
        loader=loader,
        validator_factory=RepositoryValidator,
        parse_pipeline=parse_pipeline,
        construct_pipeline=construct_pipeline
    )

    with pytest.raises(RepositoryValidationError):
        engine.load_repository()


def test_workspace_knowledge_engine_integration():
    """Verify KnowledgeEngine on actual workspace repository directory."""
    workspace_docs = Path("docs/engineering_knowledge_base")
    if workspace_docs.exists():
        loader = FilesystemRepositoryLoader(workspace_docs)
        parse_pipeline = DocumentParsingPipeline(
            reader=DocumentReader(),
            front_matter_parser=FrontMatterParser(),
            section_parser=MarkdownSectionParser()
        )
        registry = BuilderRegistry()
        registry.register("engineering_parameter", EngineeringParameterBuilder())
        construct_pipeline = EntityConstructionPipeline(registry=registry)

        engine = KnowledgeEngine(
            loader=loader,
            validator_factory=RepositoryValidator,
            parse_pipeline=parse_pipeline,
            construct_pipeline=construct_pipeline
        )

        entities = engine.load_repository()

        assert len(entities) > 0
        assert all(isinstance(e, KnowledgeEntity) for e in entities)
