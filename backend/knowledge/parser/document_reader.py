"""
DocumentReader Subsystem

Purpose:
    Defines the `DocumentReader` class responsible for reading raw text content from disk
    for a `RepositoryDocument` using UTF-8 encoding.

Role in Architecture:
    `DocumentReader` encapsulates file I/O operations within the Markdown Parsing Engine.
    By separating file reading from markdown parsing, it adheres to the Single Responsibility Principle (SRP).
    Downstream parsers (such as `MarkdownParser`) receive raw markdown text from `DocumentReader`
    without performing direct filesystem I/O themselves.
"""

from pathlib import Path
from backend.models.repository_document import RepositoryDocument


class DocumentReadError(IOError):
    """Base exception class for document reader errors."""
    pass


class DocumentNotFoundError(DocumentReadError, FileNotFoundError):
    """Raised when a RepositoryDocument file does not exist on disk."""
    pass


class DocumentAccessError(DocumentReadError, PermissionError):
    """Raised when a RepositoryDocument file exists but cannot be accessed or read."""
    pass


class EmptyDocumentError(DocumentReadError, ValueError):
    """Raised when a RepositoryDocument file exists but contains zero bytes of content."""
    pass


class DocumentReader:
    """
    Reusable file reader for repository documents.

    Responsibilities:
        - Read file content from `document.path` using UTF-8 encoding.
        - Enforce file presence, readability, and non-empty content rules.
        - Raise descriptive custom exceptions on failure.

    Limitations:
        - File I/O Only: Does not perform markdown parsing, section extraction, or entity construction.
    """

    def read(self, document: RepositoryDocument) -> str:
        """
        Reads the complete file contents of a RepositoryDocument from disk.

        Args:
            document (RepositoryDocument): Document metadata object containing absolute path.

        Returns:
            str: Complete text content of the document.

        Raises:
            DocumentNotFoundError: If the file does not exist.
            DocumentAccessError: If the file is a directory or cannot be accessed/read.
            EmptyDocumentError: If the file exists but is empty (0 bytes).
            DocumentReadError: For decoding or unexpected I/O errors.
        """
        file_path: Path = document.path

        if not file_path.exists():
            raise DocumentNotFoundError(
                f"Document file not found at path '{file_path}' (filename: '{document.file_name}')."
            )

        if not file_path.is_file():
            raise DocumentAccessError(
                f"Document path '{file_path}' exists but is not a regular file."
            )

        try:
            content = file_path.read_text(encoding="utf-8")
        except PermissionError as pe:
            raise DocumentAccessError(
                f"Permission denied when attempting to read document '{file_path}': {pe}"
            ) from pe
        except UnicodeDecodeError as ude:
            raise DocumentReadError(
                f"Failed to decode document '{file_path}' using UTF-8 encoding: {ude}"
            ) from ude
        except OSError as ose:
            raise DocumentReadError(
                f"I/O error encountered while reading document '{file_path}': {ose}"
            ) from ose

        if len(content.strip()) == 0:
            raise EmptyDocumentError(
                f"Document at path '{file_path}' is empty (contains no content)."
            )

        return content
