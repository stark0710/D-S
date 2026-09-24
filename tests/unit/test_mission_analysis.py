"""
Unit tests for Mission Analysis Platform.
"""

import pytest
from backend.design.common.requirements import (
    MissionType,
    OperatingEnvironment,
    RequirementModel,
)
from backend.design.common.validation import (
    ValidationResult,
    ValidationIssue,
    ValidationCode,
    ValidationSeverity,
)
from backend.design.common.context import (
    DesignStage,
    DesignStatus,
    ContextBuilder,
)
from backend.design.common.mission import (
    MissionComplexity,
    MissionConstraints,
    MissionProfile,
    MissionAnalysisService,
    MissionAnalysisEngine,
    InvalidRequirementError,
)


def test_mission_complexity_enum():
    """Verify MissionComplexity enum member values."""
    assert MissionComplexity.VERY_LOW == "VERY_LOW"
    assert MissionComplexity.LOW == "LOW"
    assert MissionComplexity.MEDIUM == "MEDIUM"
    assert MissionComplexity.HIGH == "HIGH"
    assert MissionComplexity.VERY_HIGH == "VERY_HIGH"


def test_mission_analysis_service_low_complexity():
    """Verify MissionAnalysisService assesses low complexity for simple requirements."""
    service = MissionAnalysisService()
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=20.0,
        target_range_km=5.0,
        cruise_speed_kmh=40.0,
        environment=OperatingEnvironment.RURAL
    )

    result = service.analyze_requirements(req)

    assert isinstance(result.mission_profile, MissionProfile)
    assert result.mission_profile.mission_complexity == MissionComplexity.VERY_LOW
    assert result.mission_profile.payload_requirement == 0.5
    assert result.mission_profile.constraints.minimum_payload_kg == 0.5


def test_mission_analysis_service_high_complexity():
    """Verify MissionAnalysisService assesses high/very high complexity for demanding requirements."""
    service = MissionAnalysisService()
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=20.0,
        target_flight_time_min=150.0,
        target_range_km=120.0,
        cruise_speed_kmh=100.0,
        environment=OperatingEnvironment.MOUNTAIN
    )

    result = service.analyze_requirements(req)

    assert result.mission_profile.mission_complexity in (MissionComplexity.HIGH, MissionComplexity.VERY_HIGH)
    assert len(result.analysis_notes) > 1


def test_mission_analysis_engine_workflow():
    """Verify MissionAnalysisEngine updates DesignContext stage, stores MissionProfile, and adds snapshot."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=3.0,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=60.0
    )

    context = ContextBuilder.create_context(req)
    engine = MissionAnalysisEngine()

    updated_context = engine.analyze(context)

    assert updated_context.mission_profile is not None
    assert updated_context.current_stage == DesignStage.MISSION_ANALYSIS
    assert updated_context.current_status == DesignStatus.IN_PROGRESS
    assert len(updated_context.snapshots) == 2
    assert updated_context.snapshots[1].stage == DesignStage.MISSION_ANALYSIS


def test_invalid_requirements_raises_error():
    """Verify InvalidRequirementError is raised when analyzing context with failed validation."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=-1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=50.0
    )

    context = ContextBuilder.create_context(req)
    context.validation_result = ValidationResult(
        is_valid=False,
        errors=[
            ValidationIssue(
                code=ValidationCode.INVALID_PAYLOAD,
                severity=ValidationSeverity.ERROR,
                field_name="payload_weight_kg",
                message="Invalid payload mass."
            )
        ]
    )

    engine = MissionAnalysisEngine()

    with pytest.raises(InvalidRequirementError):
        engine.analyze(context)
