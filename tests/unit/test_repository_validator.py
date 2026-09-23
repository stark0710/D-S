"""
Unit tests for RepositoryValidator and ValidationResult.
"""

from pathlib import Path
import pytest
from backend.knowledge.repository_index import RepositoryIndex
from backend.knowledge.repository_validator import RepositoryValidator, ValidationResult
from backend.models.repository_document import RepositoryDocument
from backend.knowledge.loader.filesystem_loader import FilesystemRepositoryLoader


def test_empty_repository_validation():
    """Verify empty repository yields validation error."""
    index = RepositoryIndex([])
    validator = RepositoryValidator(index)
    result = validator.validate()

    assert not result.valid
    assert len(result.errors) == 1
    assert "Repository is empty" in result.errors[0]


def test_valid_repository_validation():
    """Verify repository with all required categories passes validation."""
    docs = [
        RepositoryDocument(
            path=Path("/repo/EP-001.md"),
            relative_path=Path("EP-001.md"),
            file_name="EP-001.md",
            document_type="engineering_parameter"
        ),
        RepositoryDocument(
            path=Path("/repo/MD-001.md"),
            relative_path=Path("MD-001.md"),
            file_name="MD-001.md",
            document_type="mission_domain"
        ),
        RepositoryDocument(
            path=Path("/repo/MC-001.md"),
            relative_path=Path("MC-001.md"),
            file_name="MC-001.md",
            document_type="mission_category"
        ),
    ]
    index = RepositoryIndex(docs)
    validator = RepositoryValidator(index)
    result = validator.validate()

    assert result.valid
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_duplicate_filename_validation():
    """Verify duplicate filename yields error."""
    docs = [
        RepositoryDocument(
            path=Path("/repo/dir1/EP-001.md"),
            relative_path=Path("dir1/EP-001.md"),
            file_name="EP-001.md",
            document_type="engineering_parameter"
        ),
        RepositoryDocument(
            path=Path("/repo/dir2/EP-001.md"),
            relative_path=Path("dir2/EP-001.md"),
            file_name="EP-001.md",
            document_type="engineering_parameter"
        ),
        RepositoryDocument(
            path=Path("/repo/MD-001.md"),
            relative_path=Path("MD-001.md"),
            file_name="MD-001.md",
            document_type="mission_domain"
        ),
        RepositoryDocument(
            path=Path("/repo/MC-001.md"),
            relative_path=Path("MC-001.md"),
            file_name="MC-001.md",
            document_type="mission_category"
        ),
    ]
    index = RepositoryIndex(docs)
    validator = RepositoryValidator(index)
    result = validator.validate()

    assert not result.valid
    assert any("Duplicate filename detected" in err for err in result.errors)


def test_missing_required_categories_warnings():
    """Verify missing categories trigger warnings."""
    docs = [
        RepositoryDocument(
            path=Path("/repo/EP-001.md"),
            relative_path=Path("EP-001.md"),
            file_name="EP-001.md",
            document_type="engineering_parameter"
        ),
    ]
    index = RepositoryIndex(docs)
    validator = RepositoryValidator(index)
    result = validator.validate()

    assert result.valid  # Warnings do not invalidate result
    assert len(result.warnings) == 2
    assert any("mission_domain" in warn for warn in result.warnings)
    assert any("mission_category" in warn for warn in result.warnings)


def test_unknown_document_type_warning():
    """Verify unknown document types generate warnings."""
    docs = [
        RepositoryDocument(
            path=Path("/repo/EP-001.md"),
            relative_path=Path("EP-001.md"),
            file_name="EP-001.md",
            document_type="engineering_parameter"
        ),
        RepositoryDocument(
            path=Path("/repo/MD-001.md"),
            relative_path=Path("MD-001.md"),
            file_name="MD-001.md",
            document_type="mission_domain"
        ),
        RepositoryDocument(
            path=Path("/repo/MC-001.md"),
            relative_path=Path("MC-001.md"),
            file_name="MC-001.md",
            document_type="mission_category"
        ),
        RepositoryDocument(
            path=Path("/repo/other.md"),
            relative_path=Path("other.md"),
            file_name="other.md",
            document_type="unknown"
        ),
    ]
    index = RepositoryIndex(docs)
    validator = RepositoryValidator(index)
    result = validator.validate()

    assert result.valid
    assert any("unknown" in warn for warn in result.warnings)


def test_workspace_repository_validation():
    """Test validation on actual workspace repository index."""
    workspace_docs = Path("docs/engineering_knowledge_base")
    if workspace_docs.exists():
        loader = FilesystemRepositoryLoader(workspace_docs)
        docs = loader.discover_documents()
        index = RepositoryIndex(docs)
        validator = RepositoryValidator(index)
        result = validator.validate()

        assert isinstance(result, ValidationResult)
        assert result.valid
