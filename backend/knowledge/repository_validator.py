"""
RepositoryValidator Subsystem

Purpose:
    Defines the `ValidationResult` and `RepositoryValidator` classes responsible for validating
    the structural organization and metadata of the Engineering Knowledge Repository index before parsing.

Role in Architecture:
    `RepositoryValidator` sits between the `RepositoryIndex` and the downstream `Markdown Parser`.
    It ensures that the repository index is free from structural defects (e.g., duplicate filenames,
    missing mandatory document types, empty repositories, invalid metadata) before content parsing begins,
    guaranteeing that the parser only receives a structurally valid repository.
"""

from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path
from backend.knowledge.repository_index import RepositoryIndex
from backend.models.repository_document import RepositoryDocument


@dataclass(slots=True)
class ValidationResult:
    """
    Data structure representing the outcome of a repository structural validation run.

    Attributes:
        valid (bool): True if no critical errors were detected; False otherwise.
        errors (list[str]): List of critical structural error messages that halt processing.
        warnings (list[str]): List of non-critical warning messages for advisory reporting.
    """

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class RepositoryValidator:
    """
    Structural validator for the Engineering Knowledge Repository index.

    Inspects a `RepositoryIndex` instance to enforce structural integrity constraints.

    Responsibilities:
        - Detect empty repository instances.
        - Check for invalid `RepositoryDocument` metadata (missing paths, filenames, or types).
        - Identify duplicate filenames (excluding directory README index files) and relative paths.
        - Detect unsupported or unknown document classifications.
        - Ensure mandatory engineering categories (parameters, domains, categories) are present.

    Limitations:
        - Structural Only: Does not open files, read markdown contents, or validate domain logic.
        - Immutable: Does not mutate the `RepositoryIndex` or `RepositoryDocument` instances.
    """

    SUPPORTED_TYPES: set[str] = {
        "engineering_parameter",
        "mission_category",
        "mission_domain",
        "readme",
    }

    REQUIRED_CATEGORIES: set[str] = {
        "engineering_parameter",
        "mission_category",
        "mission_domain",
    }

    def __init__(self, index: RepositoryIndex) -> None:
        """
        Initializes the RepositoryValidator with a RepositoryIndex instance.

        Args:
            index (RepositoryIndex): The document catalog index to validate.
        """
        self._index: RepositoryIndex = index

    def validate(self) -> ValidationResult:
        """
        Executes all structural validation checks and returns an aggregated ValidationResult.

        Returns:
            ValidationResult: Result object containing valid flag, errors, and warnings.
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Run focused validation rules
        self._validate_empty_repository(errors)
        if not errors:  # If repository is empty, skip detailed checks
            self._validate_documents(errors, warnings)
            self._validate_duplicate_filenames(errors)
            self._validate_duplicate_paths(errors)
            self._validate_document_types(warnings)
            self._validate_required_categories(warnings)

        return ValidationResult(
            valid=(len(errors) == 0),
            errors=errors,
            warnings=warnings,
        )

    def _validate_empty_repository(self, errors: list[str]) -> None:
        """Checks if the repository contains zero documents."""
        if self._index.count() == 0:
            errors.append("Repository is empty: No documents were found in the repository index.")

    def _validate_documents(self, errors: list[str], warnings: list[str]) -> None:
        """Validates that individual RepositoryDocument metadata objects are complete."""
        for doc in self._index.get_all_documents():
            if not doc.file_name or not doc.file_name.strip():
                errors.append(f"Invalid RepositoryDocument: Missing filename for document at path '{doc.path}'.")

            if doc.path is None or not str(doc.path).strip():
                errors.append(f"Invalid RepositoryDocument: Missing absolute path for file '{doc.file_name}'.")

            if not doc.document_type or not doc.document_type.strip():
                errors.append(f"Invalid RepositoryDocument: Missing document type for file '{doc.file_name}'.")

    def _validate_duplicate_filenames(self, errors: list[str]) -> None:
        """
        Detects if multiple documents share the same filename.

        Note: README index files ('README.md') are ignored for duplicate filename validation
        as they naturally recur across subdirectories.
        """
        filename_map: dict[str, list[Path]] = defaultdict(list)
        for doc in self._index.get_all_documents():
            if doc.file_name.upper() == "README.MD" or doc.document_type == "readme":
                continue
            filename_map[doc.file_name].append(doc.relative_path)

        for filename, paths in filename_map.items():
            if len(paths) > 1:
                formatted_paths = ", ".join(f"'{p}'" for p in paths)
                errors.append(
                    f"Duplicate filename detected: '{filename}' appears in multiple locations: {formatted_paths}."
                )

    def _validate_duplicate_paths(self, errors: list[str]) -> None:
        """Detects if multiple documents share the same relative path."""
        rel_path_map: dict[Path, list[str]] = defaultdict(list)
        for doc in self._index.get_all_documents():
            rel_path_map[Path(doc.relative_path)].append(doc.file_name)

        for rel_path, filenames in rel_path_map.items():
            if len(filenames) > 1:
                errors.append(f"Duplicate relative path detected: '{rel_path}' is shared by documents {filenames}.")

    def _validate_document_types(self, warnings: list[str]) -> None:
        """Checks for documents classified with unknown or unsupported document types."""
        for doc in self._index.get_all_documents():
            if doc.document_type not in self.SUPPORTED_TYPES:
                warnings.append(
                    f"Unsupported or unknown document type '{doc.document_type}' for document '{doc.relative_path}'."
                )

    def _validate_required_categories(self, warnings: list[str]) -> None:
        """Verifies that mandatory engineering document categories are present in the index."""
        counts = self._index.count_by_type()
        for required_cat in sorted(self.REQUIRED_CATEGORIES):
            if counts.get(required_cat, 0) == 0:
                warnings.append(
                    f"Missing required engineering category: No documents of type '{required_cat}' found in index."
                )
