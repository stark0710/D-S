"""
Unit tests for BuilderRegistry.
"""

import pytest
from backend.knowledge.builders.entity_builder import EntityBuilder
from backend.knowledge.builders.engineering_parameter_builder import EngineeringParameterBuilder
from backend.knowledge.builders.builder_registry import (
    BuilderRegistry,
    DuplicateBuilderRegistrationError,
    UnregisteredBuilderError,
)
from backend.models.parsed_document import ParsedDocument
from backend.models.knowledge_entity import KnowledgeEntity


def test_builder_registry_registration_and_lookup():
    """Verify builder registration, lookup, and has_builder checks."""
    registry = BuilderRegistry()
    builder = EngineeringParameterBuilder()

    assert not registry.has_builder("engineering_parameter")
    assert registry.registered_types() == []

    registry.register("engineering_parameter", builder)

    assert registry.has_builder("engineering_parameter")
    assert registry.get_builder("engineering_parameter") == builder
    assert registry.registered_types() == ["engineering_parameter"]


def test_duplicate_registration_raises_exception():
    """Verify DuplicateBuilderRegistrationError is raised when registering a type twice."""
    registry = BuilderRegistry()
    builder1 = EngineeringParameterBuilder()
    builder2 = EngineeringParameterBuilder()

    registry.register("engineering_parameter", builder1)

    with pytest.raises(DuplicateBuilderRegistrationError):
        registry.register("engineering_parameter", builder2)


def test_unregistered_lookup_raises_exception():
    """Verify UnregisteredBuilderError is raised when looking up an unregistered type."""
    registry = BuilderRegistry()

    with pytest.raises(UnregisteredBuilderError):
        registry.get_builder("nonexistent_type")


def test_multiple_registrations():
    """Verify registering multiple distinct builders."""
    class DummyMissionDomainBuilder(EntityBuilder):
        def build(self, document: ParsedDocument) -> KnowledgeEntity:
            return KnowledgeEntity(id="MD-001", name="Domain", description="Desc")

    registry = BuilderRegistry()
    ep_builder = EngineeringParameterBuilder()
    md_builder = DummyMissionDomainBuilder()

    registry.register("engineering_parameter", ep_builder)
    registry.register("mission_domain", md_builder)

    assert registry.has_builder("engineering_parameter")
    assert registry.has_builder("mission_domain")
    assert registry.registered_types() == ["engineering_parameter", "mission_domain"]
    assert registry.get_builder("mission_domain") == md_builder
