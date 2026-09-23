"""
Unit tests for Drone Configuration Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import DroneMissionProfile
from backend.design.drone.configuration import (
    ConfigurationProfile,
    ConfigurationCandidate,
    ConfigurationConstraints,
    ConfigurationResult,
    ConfigurationValidator,
    LowestCostConfigurationStrategy,
    MaximumReliabilityStrategy,
    HeavyLiftStrategy,
    ConfigurationEngine,
)


def test_lowest_cost_strategy_ranks_quad_x_top():
    """Verify LowestCostConfigurationStrategy ranks QUAD_X as top choice."""
    mission = DroneMissionProfile(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_hover_time_min=10.0,
        target_cruise_time_min=15.0,
        target_range_km=10.0,
        cruise_speed_kmh=40.0
    )

    engine = ConfigurationEngine()
    result = engine.evaluate_configurations(mission, strategy_name="LowestCostConfigurationStrategy")

    assert isinstance(result, ConfigurationResult)
    assert result.recommended_configuration.profile.config_type == "QUAD_X"
    assert result.recommended_configuration.rank == 1


def test_maximum_reliability_strategy_ranks_octo_top():
    """Verify MaximumReliabilityStrategy ranks OCTOCOPTER as top choice due to dual motor loss redundancy."""
    mission = DroneMissionProfile(
        mission_type=MissionType.MILITARY,
        payload_weight_kg=5.0,
        target_hover_time_min=20.0,
        target_cruise_time_min=20.0,
        target_range_km=20.0,
        cruise_speed_kmh=60.0
    )

    engine = ConfigurationEngine()
    result = engine.evaluate_configurations(mission, strategy_name="MaximumReliabilityStrategy")

    assert result.recommended_configuration.profile.config_type == "OCTOCOPTER"
    assert result.recommended_configuration.profile.rotor_count == 8


def test_heavy_lift_strategy_ranks_x8_or_octo_top():
    """Verify HeavyLiftStrategy ranks X8 or OCTOCOPTER top."""
    mission = DroneMissionProfile(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=12.0,
        target_hover_time_min=15.0,
        target_cruise_time_min=15.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0
    )

    engine = ConfigurationEngine()
    result = engine.evaluate_configurations(mission, strategy_name="HeavyLiftStrategy")

    assert result.recommended_configuration.profile.config_type in ("X8", "OCTOCOPTER")


def test_configuration_validator():
    """Verify ConfigurationValidator checks constraints and issues warnings."""
    validator = ConfigurationValidator()

    quad = ConfigurationCandidate(
        profile=ConfigurationProfile(
            config_type="QUAD_X",
            rotor_count=4,
            coaxial=False,
            description="Quad X"
        )
    )

    constraints = ConfigurationConstraints(
        min_rotors=6,  # Quad fails min rotors
        required_redundancy="SINGLE"
    )

    warnings = validator.validate_candidate(quad, constraints)

    assert len(warnings) >= 2
    assert any("below minimum allowed" in w for w in warnings)
    assert any("lacks single motor loss redundancy" in w for w in warnings)
