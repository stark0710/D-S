"""
Unit tests for Universal Engineering Artifact Framework.
"""

import pytest
import json
from dataclasses import FrozenInstanceError
from backend.design.studio.artifacts import (
    ArtifactCategory,
    ArtifactVersion,
    ArtifactMetadata,
    EngineeringArtifact,
    ArtifactFactory,
    ArtifactRegistry,
    ArtifactRepository,
    ArtifactNotFoundError,
    ArtifactValidator,
    ArtifactValidationError,
    ArtifactExporter,
)


def test_artifact_version():
    """Verify ArtifactVersion formatting and compatibility logic."""
    v1 = ArtifactVersion(1, 0, 0)
    v1_1 = ArtifactVersion(1, 1, 0)
    v2 = ArtifactVersion(2, 0, 0)

    assert str(v1) == "v1.0.0"
    assert v1.is_compatible_with(v1_1)
    assert not v1.is_compatible_with(v2)


def test_artifact_factory_and_immutability():
    """Verify ArtifactFactory creates immutable EngineeringArtifact instances."""
    factory = ArtifactFactory()
    data = {"motor": "T-Motor MN501S", "kv": 300}
    meta = ArtifactMetadata(studio_name="DroneDesignStudio", stage_name="PropulsionSizing")

    artifact = factory.create_artifact(
        name="Propulsion Spec",
        category=ArtifactCategory.MOTOR_SELECTION,
        data=data,
        author="EngineerA",
        metadata=meta
    )

    assert artifact.artifact_id.startswith("ART-")
    assert artifact.name == "Propulsion Spec"
    assert artifact.category == ArtifactCategory.MOTOR_SELECTION
    assert artifact.metadata.studio_name == "DroneDesignStudio"

    # Verify immutability
    with pytest.raises(FrozenInstanceError):
        artifact.name = "Modified Name"  # type: ignore


def test_artifact_repository_operations():
    """Verify ArtifactRepository save, lookup, list filtering, and querying."""
    factory = ArtifactFactory()
    repo = ArtifactRepository()

    art1 = factory.create_artifact(
        name="Wing Geometry",
        category=ArtifactCategory.WING_DESIGN,
        data={"span": 2.5, "area": 0.8}
    )
    art2 = factory.create_artifact(
        name="Motor Spec",
        category=ArtifactCategory.MOTOR_SELECTION,
        data={"kv": 300}
    )

    repo.save_artifact(art1)
    repo.save_artifact(art2)

    assert repo.get_artifact(art1.artifact_id) == art1
    assert len(repo.list_artifacts()) == 2
    assert len(repo.list_artifacts(category=ArtifactCategory.WING_DESIGN)) == 1

    # Query predicate search
    results = repo.query_artifacts(lambda a: a.name == "Motor Spec")
    assert len(results) == 1
    assert results[0] == art2

    with pytest.raises(ArtifactNotFoundError):
        repo.get_artifact("MISSING-ID")


def test_artifact_validator():
    """Verify ArtifactValidator validation checks."""
    validator = ArtifactValidator()
    factory = ArtifactFactory()

    art_ok = factory.create_artifact("OK Art", ArtifactCategory.REQUIREMENTS, {"req": 1})
    assert validator.validate(art_ok)

    art_invalid_id = EngineeringArtifact("", "Name", ArtifactCategory.REQUIREMENTS)
    with pytest.raises(ArtifactValidationError):
        validator.validate(art_invalid_id)


def test_artifact_exporter():
    """Verify ArtifactExporter JSON and YAML formatting."""
    factory = ArtifactFactory()
    exporter = ArtifactExporter()

    art = factory.create_artifact(
        name="Export Test",
        category=ArtifactCategory.CAD_MODEL,
        data={"file": "model.step"}
    )

    json_str = exporter.export_json(art)
    parsed_json = json.loads(json_str)
    assert parsed_json["artifact_id"] == art.artifact_id
    assert parsed_json["category"] == "CAD_MODEL"

    yaml_str = exporter.export_yaml(art)
    assert "Export Test" in yaml_str
    assert "CAD_MODEL" in yaml_str
