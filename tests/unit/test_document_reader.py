"""
Unit tests for DocumentReader.
"""

from pathlib import Path
import pytest
from backend.knowledge.parser.document_reader import (
    DocumentReader,
    DocumentNotFoundError,
    DocumentAccessError,
    EmptyDocumentError,
)
from backend.models.repository_document import RepositoryDocument
from backend.knowledge.loader.filesystem_loader import FilesystemRepositoryLoader


def test_document_reader_success(tmp_path: Path):
    """Verify DocumentReader successfully reads UTF-8 content."""
    file_path = tmp_path / "test_doc.md"
    file_path.write_text("# Title\nEngineering content.", encoding="utf-8")

    doc = RepositoryDocument(
        path=file_path,
        relative_path=Path("test_doc.md"),
        file_name="test_doc.md",
        document_type="engineering_parameter"
    )

    reader = DocumentReader()
    content = reader.read(doc)

    assert content == "# Title\nEngineering content."


def test_document_not_found(tmp_path: Path):
    """Verify DocumentNotFoundError is raised for non-existent files."""
    file_path = tmp_path / "non_existent.md"

    doc = RepositoryDocument(
        path=file_path,
        relative_path=Path("non_existent.md"),
        file_name="non_existent.md",
        document_type="engineering_parameter"
    )

    reader = DocumentReader()
    with pytest.raises(DocumentNotFoundError):
        reader.read(doc)


def test_document_access_error(tmp_path: Path):
    """Verify DocumentAccessError is raised when path is a directory."""
    dir_path = tmp_path / "sub_dir"
    dir_path.mkdir()

    doc = RepositoryDocument(
        path=dir_path,
        relative_path=Path("sub_dir"),
        file_name="sub_dir",
        document_type="engineering_parameter"
    )

    reader = DocumentReader()
    with pytest.raises(DocumentAccessError):
        reader.read(doc)


def test_empty_document_error(tmp_path: Path):
    """Verify EmptyDocumentError is raised for zero-byte files."""
    file_path = tmp_path / "empty.md"
    file_path.write_text("   \n  \n", encoding="utf-8")

    doc = RepositoryDocument(
        path=file_path,
        relative_path=Path("empty.md"),
        file_name="empty.md",
        document_type="engineering_parameter"
    )

    reader = DocumentReader()
    with pytest.raises(EmptyDocumentError):
        reader.read(doc)


def test_document_reader_workspace_integration():
    """Verify DocumentReader on real workspace Markdown files."""
    workspace_docs = Path("docs/engineering_knowledge_base")
    if workspace_docs.exists():
        loader = FilesystemRepositoryLoader(workspace_docs)
        documents = loader.discover_documents()
        assert len(documents) > 0

        reader = DocumentReader()
        first_doc_content = reader.read(documents[0])
        assert isinstance(first_doc_content, str)
        assert len(first_doc_content) > 0
