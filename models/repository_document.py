"""
RepositoryDocument Infrastructure Domain Model

Purpose:
    Defines the `RepositoryDocument` infrastructure domain model representing a single discoverable document
    within the Torq Wings Engineering Knowledge Repository.

Role in Architecture:
    `RepositoryDocument` serves as the canonical metadata object passed between repository discovery
    and parsing subsystems:
        - The Repository Loader discovers files and outputs `RepositoryDocument` instances.
        - `RepositoryDocument` describes file paths, relative locations, and document type classifications.
        - The Markdown Parser consumes `RepositoryDocument` instances to extract structured domain objects.
    This separation enforces Single Responsibility Principle (SRP) across the repository loading pipeline.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class RepositoryDocument:
    """
    Infrastructure domain model representing metadata for a discovered repository document.

    It encapsulates location and classification metadata for a document without performing any
    file I/O, parsing, validation, or business logic.

    Architectural Responsibilities:
        - Repository Loader: Discovers repository files and constructs `RepositoryDocument` objects.
        - Markdown Parser: Receives `RepositoryDocument` objects as input instead of raw string paths.
        - Infrastructure Pure Dataclass: Free of filesystem reading, parsing logic, DB, or API calls.

    Attributes:
        path (Path): Absolute filesystem path to the repository document.
        relative_path (Path): Path relative to the repository root directory.
        file_name (str): The file name (including extension, e.g., 'MP-001-001.md').
        document_type (str): Classification type of the document (e.g., 'mission_parameter', 'mission_category').
    """

    path: Path
    relative_path: Path
    file_name: str
    document_type: str
