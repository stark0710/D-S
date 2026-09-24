"""
RepositoryIndex In-Memory Document Catalog

Purpose:
    Defines the `RepositoryIndex` class, which serves as the canonical in-memory catalog
    and query engine for `RepositoryDocument` metadata objects discovered by repository loaders.

Role in Architecture:
    `RepositoryIndex` indexes and organizes discovered document metadata without reading raw
    file content or performing parsing. Downstream components (such as the Markdown Parser,
    Relationship Resolvers, and Knowledge Graph builders) query `RepositoryIndex` to filter,
    retrieve, and count documents by type, filename, or relative path.
"""

from pathlib import Path
from backend.models.repository_document import RepositoryDocument


class RepositoryIndex:
    """
    In-memory catalog for querying RepositoryDocument instances.

    Provides indexed lookups by document type, file name, and relative path.

    Responsibilities:
        - Maintain an immutable catalog of discovered repository documents.
        - Provide fast query operations by document classification type.
        - Enable document lookups by filename or relative path.
        - Expose repository document count metrics.

    Limitations:
        - In-Memory Only: Does not persist state to disk or database.
        - Metadata Only: Does not hold parsed markdown content or relationship graphs.
    """

    def __init__(self, documents: list[RepositoryDocument] | None = None) -> None:
        """
        Initializes the RepositoryIndex with a list of RepositoryDocument objects.

        Args:
            documents (list[RepositoryDocument] | None): Initial list of discovered documents.
        """
        self._documents: list[RepositoryDocument] = list(documents) if documents else []
        self._by_type: dict[str, list[RepositoryDocument]] = {}
        self._by_filename: dict[str, RepositoryDocument] = {}
        self._by_relative_path: dict[Path, RepositoryDocument] = {}

        self._reindex()

    def _reindex(self) -> None:
        """Private helper to populate lookup dictionaries for fast O(1) queries."""
        self._by_type.clear()
        self._by_filename.clear()
        self._by_relative_path.clear()

        for doc in self._documents:
            # Index by type
            if doc.document_type not in self._by_type:
                self._by_type[doc.document_type] = []
            self._by_type[doc.document_type].append(doc)

            # Index by filename (last one wins if duplicate filenames exist across subdirs)
            self._by_filename[doc.file_name] = doc

            # Index by relative path (normalized Path)
            norm_rel_path = Path(doc.relative_path)
            self._by_relative_path[norm_rel_path] = doc

    def get_all_documents(self) -> list[RepositoryDocument]:
        """
        Returns all indexed RepositoryDocument objects.

        Returns:
            list[RepositoryDocument]: List of all stored documents.
        """
        return list(self._documents)

    def get_documents_by_type(self, document_type: str) -> list[RepositoryDocument]:
        """
        Returns all documents matching the specified document classification type.

        Args:
            document_type (str): Classification string (e.g., 'engineering_parameter', 'mission_category').

        Returns:
            list[RepositoryDocument]: List of documents matching the type, or empty list if none match.
        """
        return list(self._by_type.get(document_type, []))

    def find_by_filename(self, file_name: str) -> RepositoryDocument | None:
        """
        Finds a document by its exact file name.

        Args:
            file_name (str): The filename to search for (e.g., 'MP-001-001.md').

        Returns:
            RepositoryDocument | None: The matching document metadata, or None if not found.
        """
        return self._by_filename.get(file_name)

    def find_by_relative_path(self, relative_path: str | Path) -> RepositoryDocument | None:
        """
        Finds a document by its relative path within the repository.

        Args:
            relative_path (str | Path): Relative path string or Path object.

        Returns:
            RepositoryDocument | None: The matching document metadata, or None if not found.
        """
        path_obj = Path(relative_path)
        return self._by_relative_path.get(path_obj)

    def count(self) -> int:
        """
        Returns the total number of indexed documents.

        Returns:
            int: Total count of documents.
        """
        return len(self._documents)

    def count_by_type(self) -> dict[str, int]:
        """
        Returns document counts aggregated by document classification type.

        Returns:
            dict[str, int]: Dictionary mapping each document_type to its count.
        """
        return {doc_type: len(docs) for doc_type, docs in self._by_type.items()}
