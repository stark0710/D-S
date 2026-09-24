"""
Knowledge subsystem package for Torq Wings Design Studio.
"""

from backend.knowledge.repository_index import RepositoryIndex
from backend.knowledge.repository_validator import RepositoryValidator, ValidationResult
from backend.knowledge.knowledge_engine import KnowledgeEngine, RepositoryValidationError
from backend.knowledge.knowledge_repository import (
    KnowledgeRepository,
    KnowledgeRepositoryError,
    DuplicateEntityIDError,
    EntityNotFoundError,
)

__all__ = [
    "RepositoryIndex",
    "RepositoryValidator",
    "ValidationResult",
    "KnowledgeEngine",
    "RepositoryValidationError",
    "KnowledgeRepository",
    "KnowledgeRepositoryError",
    "DuplicateEntityIDError",
    "EntityNotFoundError",
]
