"""
Repository Loader Abstract Interface

Purpose:
    Defines the abstract base contract for all repository loaders within the Torq Wings
    Engineering Knowledge Platform.

Role in Architecture:
    `RepositoryLoader` establishes a clean architectural boundary using the Dependency
    Inversion Principle (DIP). By depending on this abstraction, downstream services (such as
    the Markdown Parser and Knowledge Repository services) remain decoupled from concrete
    storage mechanisms.

Future Implementations:
    - `LocalFileSystemRepositoryLoader`: Discovers documents from the local disk workspace.
    - `GitRepositoryLoader`: Discovers documents from a local or remote Git repository.
    - `GitHubRepositoryLoader`: Discovers documents via GitHub API.
    - `CloudStorageRepositoryLoader`: Discovers documents from S3/GCS buckets.
    - `ZipArchiveRepositoryLoader`: Discovers documents embedded in ZIP archives.
"""

from abc import ABC, abstractmethod
from backend.models.repository_document import RepositoryDocument


class RepositoryLoader(ABC):
    """
    Abstract base class for discovering engineering repository documents.

    Every repository loader implementation (filesystem, Git, cloud, etc.) must implement
    this interface to scan and return metadata representations of available documents.

    Design Principles:
        - Dependency Inversion Principle (DIP): High-level modules depend on this abstraction.
        - Single Responsibility Principle (SRP): Responsible solely for document discovery contract.
    """

    @abstractmethod
    def discover_documents(self) -> list[RepositoryDocument]:
        """
        Discovers engineering knowledge documents from the target repository source.

        Returns:
            list[RepositoryDocument]: A list of metadata objects describing all discovered documents.

        Raises:
            NotImplementedError: If invoked directly on the abstract base class.
        """
        pass
