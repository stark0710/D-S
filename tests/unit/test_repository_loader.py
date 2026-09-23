"""
Unit tests for RepositoryLoader abstract base class.
"""

import pytest
from backend.knowledge.loader.repository_loader import RepositoryLoader
from backend.models.repository_document import RepositoryDocument


def test_cannot_instantiate_abstract_repository_loader():
    """Verify RepositoryLoader cannot be instantiated directly."""
    with pytest.raises(TypeError):
        RepositoryLoader()


def test_concrete_subclass_implementation():
    """Verify concrete subclass can implement discover_documents."""
    class DummyRepositoryLoader(RepositoryLoader):
        def discover_documents(self) -> list[RepositoryDocument]:
            return []

    loader = DummyRepositoryLoader()
    assert isinstance(loader, RepositoryLoader)
    assert loader.discover_documents() == []
