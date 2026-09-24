"""
TorqWingsApplication Root Application Subsystem

Purpose:
    Defines the `TorqWingsApplication` class, which serves as the single top-level root application
    object and public entry point for the entire Torq Wings backend platform.

Role in Architecture:
    `TorqWingsApplication` manages the backend application lifecycle. It accepts an injected
    `KnowledgeEngine`, orchestrates system initialization, instantiates the canonical `KnowledgeRepository`,
    and exposes it to downstream platform services (Knowledge Graph, Query Engine, Design Engine,
    Optimization Engine, REST APIs, and CLI tools).
"""

from backend.knowledge.knowledge_engine import KnowledgeEngine
from backend.knowledge.knowledge_repository import KnowledgeRepository


class ApplicationError(RuntimeError):
    """Base exception class for application lifecycle errors."""
    pass


class ApplicationNotInitializedError(ApplicationError):
    """Raised when accessing application services before initialize() has completed."""
    pass


class TorqWingsApplication:
    """
    Root application object for Torq Wings Design Studio.

    Responsibilities:
        - Orchestrate backend application startup and lifecycle.
        - Trigger knowledge repository loading via the injected `KnowledgeEngine`.
        - Hold and expose the canonical in-memory `KnowledgeRepository` instance.
        - Serve as the root dependency injection container boundary for APIs and CLI.

    Lifecycle:
        1. Instantiate `TorqWingsApplication` with an injected `KnowledgeEngine`.
        2. Call `initialize()` to execute repository loading and build `KnowledgeRepository`.
        3. Query `is_initialized()` to check readiness.
        4. Access `get_repository()` to interact with loaded engineering knowledge.

    Design Principles:
        - Single Responsibility Principle (SRP): Responsible solely for application lifecycle.
        - Dependency Injection: Injects `KnowledgeEngine` collaborator.
        - Clean Architecture: Decouples platform entry point from internal parsing/loader mechanics.
    """

    def __init__(self, engine: KnowledgeEngine) -> None:
        """
        Initializes the TorqWingsApplication with an injected KnowledgeEngine dependency.

        Args:
            engine (KnowledgeEngine): Injected top-level knowledge engine instance.
        """
        self._engine: KnowledgeEngine = engine
        self._repository: KnowledgeRepository | None = None

    def initialize(self) -> None:
        """
        Executes application initialization by loading the engineering knowledge repository.

        Loads all engineering entities into memory using `KnowledgeEngine` and instantiates
        the canonical `KnowledgeRepository`.

        Raises:
            RepositoryValidationError: If repository structural validation fails.
            ApplicationError: If initialization fails.
        """
        entities = self._engine.load_repository()
        self._repository = KnowledgeRepository(entities)

    def is_initialized(self) -> bool:
        """
        Returns whether the application has completed initialization.

        Returns:
            bool: True if initialize() has successfully run; False otherwise.
        """
        return self._repository is not None

    def get_repository(self) -> KnowledgeRepository:
        """
        Retrieves the initialized KnowledgeRepository instance.

        Returns:
            KnowledgeRepository: The active in-memory knowledge repository.

        Raises:
            ApplicationNotInitializedError: If initialize() has not been called prior to this invocation.
        """
        if self._repository is None:
            raise ApplicationNotInitializedError(
                "TorqWingsApplication is not initialized. You must call initialize() before accessing the repository."
            )
        return self._repository
