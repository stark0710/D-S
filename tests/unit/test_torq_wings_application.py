"""
Unit tests for TorqWingsApplication.
"""

from pathlib import Path
import pytest
from backend.application.torq_wings_application import (
    TorqWingsApplication,
    ApplicationNotInitializedError,
)
from backend.knowledge.knowledge_repository import KnowledgeRepository
from backend.models.engineering_parameter import EngineeringParameter
from backend.knowledge.loader.filesystem_loader import FilesystemRepositoryLoader
from backend.knowledge.repository_validator import RepositoryValidator
from backend.knowledge.parser.document_reader import DocumentReader
from backend.knowledge.parser.front_matter_parser import FrontMatterParser
from backend.knowledge.parser.markdown_section_parser import MarkdownSectionParser
from backend.knowledge.parser.document_parsing_pipeline import DocumentParsingPipeline
from backend.knowledge.builders.engineering_parameter_builder import EngineeringParameterBuilder
from backend.knowledge.builders.builder_registry import BuilderRegistry
from backend.knowledge.builders.entity_construction_pipeline import EntityConstructionPipeline
from backend.knowledge.knowledge_engine import KnowledgeEngine


def test_torq_wings_application_lifecycle(tmp_path: Path):
    """Verify application lifecycle: init state, initialize(), get_repository()."""
    param_file = tmp_path / "EP-001.md"
    param_file.write_text(
        "---\n"
        "id: EP-001\n"
        "name: Wing Span\n"
        "unit: m\n"
        "---\n\n"
        "# Wing Span\n"
        "Wing span description.\n",
        encoding="utf-8"
    )

    # Setup knowledge engine dependencies
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

    app = TorqWingsApplication(engine=engine)

    # 1. Initially not initialized
    assert not app.is_initialized()

    # 2. get_repository before initialize raises ApplicationNotInitializedError
    with pytest.raises(ApplicationNotInitializedError):
        app.get_repository()

    # 3. Initialize application
    app.initialize()

    # 4. Now initialized
    assert app.is_initialized()

    # 5. Access repository
    repo = app.get_repository()
    assert isinstance(repo, KnowledgeRepository)
    assert repo.count() == 1
    assert repo.has_entity("EP-001")


def test_workspace_application_integration():
    """Verify TorqWingsApplication integration on actual workspace repository."""
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

        app = TorqWingsApplication(engine=engine)
        app.initialize()

        assert app.is_initialized()
        repo = app.get_repository()
        assert repo.count() > 0
        assert len(repo.get_by_type(EngineeringParameter)) > 0
