"""
Unit tests for RepositoryDocument domain model.
"""

from pathlib import Path
import pytest
from backend.models.repository_document import RepositoryDocument


def test_repository_document_instantiation():
    """Verify RepositoryDocument initializes correctly with Path objects and strings."""
    abs_path = Path("/workspace/docs/mission_parameters/MP-001.md")
    rel_path = Path("docs/mission_parameters/MP-001.md")

    doc = RepositoryDocument(
        path=abs_path,
        relative_path=rel_path,
        file_name="MP-001.md",
        document_type="mission_parameter"
    )

    assert doc.path == abs_path
    assert doc.relative_path == rel_path
    assert doc.file_name == "MP-001.md"
    assert doc.document_type == "mission_parameter"
    assert isinstance(doc.path, Path)
    assert isinstance(doc.relative_path, Path)


def test_repository_document_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    doc = RepositoryDocument(
        path=Path("/tmp/test.md"),
        relative_path=Path("test.md"),
        file_name="test.md",
        document_type="general"
    )

    with pytest.raises(AttributeError):
        doc.file_contents = "Invalid"
