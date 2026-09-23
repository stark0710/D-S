"""
Unit tests for RepositoryIndex.
"""

from pathlib import Path
import pytest
from backend.knowledge.repository_index import RepositoryIndex
from backend.models.repository_document import RepositoryDocument
from backend.knowledge.loader.filesystem_loader import FilesystemRepositoryLoader


@pytest.fixture
def sample_documents() -> list[RepositoryDocument]:
    return [
        RepositoryDocument(
            path=Path("/repo/docs/EP-001.md"),
            relative_path=Path("docs/EP-001.md"),
            file_name="EP-001.md",
            document_type="engineering_parameter"
        ),
        RepositoryDocument(
            path=Path("/repo/docs/MP-002.md"),
            relative_path=Path("docs/MP-002.md"),
            file_name="MP-002.md",
            document_type="engineering_parameter"
        ),
        RepositoryDocument(
            path=Path("/repo/docs/MC-001.md"),
            relative_path=Path("docs/MC-001.md"),
            file_name="MC-001.md",
            document_type="mission_category"
        ),
        RepositoryDocument(
            path=Path("/repo/README.md"),
            relative_path=Path("README.md"),
            file_name="README.md",
            document_type="readme"
        ),
    ]


def test_repository_index_queries(sample_documents: list[RepositoryDocument]):
    index = RepositoryIndex(sample_documents)

    # Test count
    assert index.count() == 4

    # Test get_all_documents
    all_docs = index.get_all_documents()
    assert len(all_docs) == 4

    # Test get_documents_by_type
    ep_docs = index.get_documents_by_type("engineering_parameter")
    assert len(ep_docs) == 2
    assert {d.file_name for d in ep_docs} == {"EP-001.md", "MP-002.md"}

    mc_docs = index.get_documents_by_type("mission_category")
    assert len(mc_docs) == 1
    assert mc_docs[0].file_name == "MC-001.md"

    # Test find_by_filename
    doc = index.find_by_filename("EP-001.md")
    assert doc is not None
    assert doc.document_type == "engineering_parameter"

    missing = index.find_by_filename("NONEXISTENT.md")
    assert missing is None

    # Test find_by_relative_path
    doc_rel = index.find_by_relative_path("docs/MC-001.md")
    assert doc_rel is not None
    assert doc_rel.file_name == "MC-001.md"

    doc_path = index.find_by_relative_path(Path("README.md"))
    assert doc_path is not None
    assert doc_path.document_type == "readme"

    # Test count_by_type
    type_counts = index.count_by_type()
    assert type_counts == {
        "engineering_parameter": 2,
        "mission_category": 1,
        "readme": 1
    }


def test_empty_repository_index():
    index = RepositoryIndex()
    assert index.count() == 0
    assert index.get_all_documents() == []
    assert index.get_documents_by_type("engineering_parameter") == []
    assert index.find_by_filename("EP-001.md") is None
    assert index.find_by_relative_path("docs/EP-001.md") is None
    assert index.count_by_type() == {}


def test_index_with_loader_integration():
    workspace_docs = Path("docs/engineering_knowledge_base")
    if workspace_docs.exists():
        loader = FilesystemRepositoryLoader(workspace_docs)
        docs = loader.discover_documents()
        index = RepositoryIndex(docs)

        assert index.count() > 0
        ep_docs = index.get_documents_by_type("engineering_parameter")
        assert len(ep_docs) > 0
