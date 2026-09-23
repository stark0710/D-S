"""
Unit tests for FilesystemRepositoryLoader.
"""

from pathlib import Path
import pytest
from backend.knowledge.loader.filesystem_loader import FilesystemRepositoryLoader
from backend.knowledge.loader.repository_loader import RepositoryLoader
from backend.models.repository_document import RepositoryDocument


def test_filesystem_loader_inheritance():
    """Verify FilesystemRepositoryLoader inherits from RepositoryLoader."""
    loader = FilesystemRepositoryLoader(Path("."))
    assert isinstance(loader, RepositoryLoader)


def test_invalid_root_path():
    """Verify ValueError is raised when root_path does not exist."""
    with pytest.raises(ValueError):
        FilesystemRepositoryLoader(Path("/invalid/path/that/does/not/exist"))


def test_discovery_and_classification(tmp_path: Path):
    """Test recursive file discovery and document type classification."""
    # Setup test directory structure
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "ignored.md").write_text("# Ignored")

    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.md").write_text("# Ignored")

    (tmp_path / "subfolder").mkdir()
    (tmp_path / "subfolder" / "EP-001.md").write_text("# Engineering Parameter")
    (tmp_path / "subfolder" / "MP-002.md").write_text("# Mission Parameter")
    (tmp_path / "subfolder" / "MC-001.md").write_text("# Mission Category")
    (tmp_path / "subfolder" / "MD-001.md").write_text("# Mission Domain")
    (tmp_path / "README.md").write_text("# Readme")
    (tmp_path / "other.md").write_text("# Unknown Markdown")
    (tmp_path / "script.py").write_text("# Non-markdown")

    loader = FilesystemRepositoryLoader(tmp_path)
    documents = loader.discover_documents()

    assert len(documents) == 6

    doc_map = {doc.file_name: doc for doc in documents}

    assert "EP-001.md" in doc_map
    assert doc_map["EP-001.md"].document_type == "engineering_parameter"

    assert "MP-002.md" in doc_map
    assert doc_map["MP-002.md"].document_type == "engineering_parameter"

    assert "MC-001.md" in doc_map
    assert doc_map["MC-001.md"].document_type == "mission_category"

    assert "MD-001.md" in doc_map
    assert doc_map["MD-001.md"].document_type == "mission_domain"

    assert "README.md" in doc_map
    assert doc_map["README.md"].document_type == "readme"

    assert "other.md" in doc_map
    assert doc_map["other.md"].document_type == "unknown"


def test_workspace_discovery():
    """Test discovery on actual project docs directory."""
    workspace_docs = Path("docs/engineering_knowledge_base")
    if workspace_docs.exists():
        loader = FilesystemRepositoryLoader(workspace_docs)
        documents = loader.discover_documents()
        assert len(documents) > 0
        assert all(isinstance(doc, RepositoryDocument) for doc in documents)
