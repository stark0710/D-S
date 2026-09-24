"""
Unit tests for Requirement Validation Framework.
"""

import pytest
from backend.design.common.requirements import (
    MissionType,
    AircraftType,
    TakeoffType,
    LandingType,
    OperatingEnvironment,
    OptimizationPriority,
    DesignMode,
    RequirementModel,
)
from backend.design.common.validation import (
    ValidationSeverity,
    ValidationCode,
    ValidationIssue,
    ValidationResult,
    ValidationPipeline,
    RequirementValidator,
    PayloadValidationRule,
    AircraftSelectionRule,
)


def test_valid_requirements_engineering_advisor_mode():
    """Verify validation passes for valid requirements in Engineering Advisor mode without aircraft_type."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.5,
        target_flight_time_min=45.0,
        target_range_km=40.0,
        cruise_speed_kmh=60.0,
        design_mode=DesignMode.ENGINEERING_ADVISOR
    )

    validator = RequirementValidator()
    result = validator.validate(req)

    assert result.is_valid
    assert len(result.errors) == 0


def test_valid_requirements_manual_mode():
    """Verify validation passes for valid requirements in Manual mode with specified aircraft_type."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=5.0,
        target_flight_time_min=30.0,
        target_range_km=25.0,
        cruise_speed_kmh=80.0,
        aircraft_type=AircraftType.HEXACOPTER,
        design_mode=DesignMode.MANUAL
    )

    validator = RequirementValidator()
    result = validator.validate(req)

    assert result.is_valid
    assert len(result.errors) == 0


def test_missing_aircraft_type_in_manual_mode_fails():
    """Verify validation fails when aircraft_type is missing in Manual design mode."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=5.0,
        target_flight_time_min=30.0,
        target_range_km=25.0,
        cruise_speed_kmh=80.0,
        aircraft_type=None,
        design_mode=DesignMode.MANUAL
    )

    validator = RequirementValidator()
    result = validator.validate(req)

    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].code == ValidationCode.AIRCRAFT_TYPE_REQUIRED


def test_invalid_numeric_parameters():
    """Verify validation catches negative or zero numeric parameters."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=-1.0,
        target_flight_time_min=0.0,
        target_range_km=-10.0,
        cruise_speed_kmh=0.0,
        budget=-500.0,
        maximum_takeoff_weight_kg=-2.0
    )

    validator = RequirementValidator()
    result = validator.validate(req)

    assert not result.is_valid
    error_codes = {issue.code for issue in result.errors}
    assert ValidationCode.INVALID_PAYLOAD in error_codes
    assert ValidationCode.INVALID_FLIGHT_TIME in error_codes
    assert ValidationCode.INVALID_RANGE_REQUIREMENT in error_codes
    assert ValidationCode.INVALID_CRUISE_SPEED in error_codes
    assert ValidationCode.INVALID_BUDGET in error_codes
    assert ValidationCode.INVALID_TAKEOFF_WEIGHT in error_codes


def test_mtow_less_than_payload_fails():
    """Verify MTOW limit less than payload weight triggers validation error."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=10.0,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=50.0,
        maximum_takeoff_weight_kg=8.0  # Impossible MTOW limit
    )

    validator = RequirementValidator()
    result = validator.validate(req)

    assert not result.is_valid
    assert any(issue.code == ValidationCode.INVALID_TAKEOFF_WEIGHT for issue in result.errors)


def test_custom_validation_pipeline():
    """Verify registering rules dynamically into ValidationPipeline."""
    pipeline = ValidationPipeline()
    pipeline.register_rule(PayloadValidationRule())
    pipeline.register_rule(AircraftSelectionRule())

    validator = RequirementValidator(pipeline=pipeline)

    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=50.0
    )

    res = validator.validate(req)
    assert res.is_valid
    assert res.metadata["rule_count"] == 2
