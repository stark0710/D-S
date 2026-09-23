"""
Unit tests for EntityConstructionPipeline.
"""

from pathlib import Path
import pytest
from backend.models.repository_document import RepositoryDocument
from backend.models.parsed_document import ParsedDocument
from backend.models.engineering_parameter import EngineeringParameter
from backend.models.knowledge_entity import KnowledgeEntity
from backend.knowledge.builders.entity_builder import EntityBuilder
from backend.knowledge.builders.engineering_parameter_builder import EngineeringParameterBuilder
from backend.knowledge.builders.builder_registry import BuilderRegistry, UnregisteredBuilderError
from backend.knowledge.builders.entity_construction_pipeline import EntityConstructionPipeline
from backend.knowledge.parser.document_reader import DocumentReader
from backend.knowledge.parser.front_matter_parser import FrontMatterParser
from backend.knowledge.parser.markdown_section_parser import MarkdownSectionParser
from backend.knowledge.parser.document_parsing_pipeline import DocumentParsingPipeline


def test_entity_construction_pipeline_delegation():
    """Verify EntityConstructionPipeline looks up builder from registry and delegates construction."""
    registry = BuilderRegistry()
    ep_builder = EngineeringParameterBuilder()
    registry.register("engineering_parameter", ep_builder)

    repo_doc = RepositoryDocument(
        path=Path("/repo/EP-001.md"),
        relative_path=Path("EP-001.md"),
        file_name="EP-001.md",
        document_type="engineering_parameter"
    )

    metadata = {"id": "EP-001", "name": "Stall Speed", "unit": "m/s"}
    parsed_doc = ParsedDocument(repository_document=repo_doc, metadata=metadata)

    pipeline = EntityConstructionPipeline(registry=registry)
    entity = pipeline.construct(parsed_doc)

    assert isinstance(entity, EngineeringParameter)
    assert entity.id == "EP-001"
    assert entity.name == "Stall Speed"
    assert entity.unit == "m/s"


def test_unregistered_document_type_raises_error():
    """Verify UnregisteredBuilderError is propagated when document_type has no registered builder."""
    registry = BuilderRegistry()
    pipeline = EntityConstructionPipeline(registry=registry)

    repo_doc = RepositoryDocument(
        path=Path("/repo/unregistered.md"),
        relative_path=Path("unregistered.md"),
        file_name="unregistered.md",
        document_type="unregistered_type"
    )
    parsed_doc = ParsedDocument(repository_document=repo_doc)

    with pytest.raises(UnregisteredBuilderError):
        pipeline.construct(parsed_doc)


def test_full_parsing_and_construction_pipeline_integration(tmp_path: Path):
    """Integration test connecting DocumentParsingPipeline to EntityConstructionPipeline."""
    file_path = tmp_path / "EP-007-001.md"
    file_path.write_text(
        "---\n"
        "id: MP-007-001\n"
        "name: Reliability Requirement\n"
        "unit: '%'\n"
        "---\n\n"
        "# Reliability Requirement\n"
        "System reliability specification.\n",
        encoding="utf-8"
    )

    repo_doc = RepositoryDocument(
        path=file_path,
        relative_path=Path("EP-007-001.md"),
        file_name="EP-007-001.md",
        document_type="engineering_parameter"
    )

    # 1. Parse document
    parse_pipeline = DocumentParsingPipeline(
        reader=DocumentReader(),
        front_matter_parser=FrontMatterParser(),
        section_parser=MarkdownSectionParser()
    )
    parsed_doc = parse_pipeline.parse(repo_doc)

    # 2. Setup Construction Pipeline
    registry = BuilderRegistry()
    registry.register("engineering_parameter", EngineeringParameterBuilder())
    construct_pipeline = EntityConstructionPipeline(registry=registry)

    # 3. Construct entity
    entity = construct_pipeline.construct(parsed_doc)

    assert isinstance(entity, EngineeringParameter)
    assert entity.id == "MP-007-001"
    assert entity.name == "Reliability Requirement"
    assert entity.unit == "%"
