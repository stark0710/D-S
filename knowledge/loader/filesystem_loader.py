"""
Filesystem Repository Loader Implementation

Purpose:
    Provides a concrete filesystem implementation of `RepositoryLoader` that recursively scans
    a local directory workspace to discover supported Markdown repository documents.

Role in Architecture:
    `FilesystemRepositoryLoader` implements the `RepositoryLoader` interface. It navigates the local
    filesystem, filters out ignored directories (such as .git, node_modules, .venv), classifies
    discovered Markdown documents based on file naming conventions, and returns canonical
    `RepositoryDocument` metadata instances.
"""

from pathlib import Path
from backend.knowledge.loader.repository_loader import RepositoryLoader
from backend.models.repository_document import RepositoryDocument


class FilesystemRepositoryLoader(RepositoryLoader):
    """
    Concrete RepositoryLoader that discovers Markdown documents from a local filesystem directory.

    Attributes:
        root_path (Path): Absolute path to the repository root directory.

    Ignored Directories:
        `.git`, `.github`, `__pycache__`, `node_modules`, `.venv`, `build`, `dist`

    Document Classification Conventions:
        - `EP-*.md` / `MP-*.md` -> `engineering_parameter`
        - `MC-*.md` -> `mission_category`
        - `MD-*.md` -> `mission_domain`
        - `README.md` -> `readme`
        - Other `*.md` -> `unknown`
    """

    IGNORED_DIRS: set[str] = {
        ".git",
        ".github",
        "__pycache__",
        "node_modules",
        ".venv",
        "build",
        "dist",
    }

    def __init__(self, root_path: str | Path) -> None:
        """
        Initializes the FilesystemRepositoryLoader with a repository root path.

        Args:
            root_path (str | Path): Root directory path of the repository to scan.

        Raises:
            ValueError: If the root_path does not exist or is not a directory.
        """
        self.root_path: Path = Path(root_path).resolve()
        if not self.root_path.exists() or not self.root_path.is_dir():
            raise ValueError(f"Repository root path '{self.root_path}' does not exist or is not a directory.")

    def discover_documents(self) -> list[RepositoryDocument]:
        """
        Recursively scans the repository root directory and returns a list of discovered documents.

        Returns:
            list[RepositoryDocument]: List of RepositoryDocument metadata objects.
        """
        discovered_paths = self._scan_repository()
        return [self._create_document(path) for path in discovered_paths]

    def _scan_repository(self) -> list[Path]:
        """
        Recursively scans the root directory, ignoring specified directories and non-markdown files.

        Returns:
            list[Path]: List of absolute Path objects matching supported document criteria.
        """
        matching_paths: list[Path] = []
        for path in self.root_path.rglob("*"):
            if path.is_file() and self._is_supported_document(path):
                matching_paths.append(path)
        return sorted(matching_paths)

    def _is_supported_document(self, path: Path) -> bool:
        """
        Determines whether a file path represents a supported Markdown document.

        Checks:
            1. File extension is `.md`.
            2. Path does not pass through any ignored directory.

        Args:
            path (Path): Absolute file path to evaluate.

        Returns:
            bool: True if the file is a supported repository document; False otherwise.
        """
        if path.suffix.lower() != ".md":
            return False

        # Check relative path parts for any ignored directory
        try:
            rel_parts = path.relative_to(self.root_path).parts
        except ValueError:
            rel_parts = path.parts

        # Check if any parent directory component is in IGNORED_DIRS
        for part in rel_parts[:-1]:  # exclude file name itself
            if part in self.IGNORED_DIRS:
                return False

        return True

    def _classify_document(self, path: Path) -> str:
        """
        Classifies a document based on filename conventions.

        Args:
            path (Path): File path to classify.

        Returns:
            str: Document type classification string.
        """
        file_name_upper = path.name.upper()

        if file_name_upper == "README.MD":
            return "readme"
        elif file_name_upper.startswith("EP-") or file_name_upper.startswith("MP-"):
            return "engineering_parameter"
        elif file_name_upper.startswith("MC-"):
            return "mission_category"
        elif file_name_upper.startswith("MD-"):
            return "mission_domain"
        else:
            return "unknown"

    def _create_document(self, path: Path) -> RepositoryDocument:
        """
        Constructs a RepositoryDocument metadata instance for a discovered file.

        Args:
            path (Path): Absolute path of the file.

        Returns:
            RepositoryDocument: Structured document metadata instance.
        """
        try:
            rel_path = path.relative_to(self.root_path)
        except ValueError:
            rel_path = path

        doc_type = self._classify_document(path)

        return RepositoryDocument(
            path=path,
            relative_path=rel_path,
            file_name=path.name,
            document_type=doc_type,
        )
