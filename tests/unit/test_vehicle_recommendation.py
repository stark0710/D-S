"""
Unit tests for Vehicle Recommendation Platform.
"""

import pytest
from backend.design.common.requirements import (
    MissionType,
    TakeoffType,
    LandingType,
    OperatingEnvironment,
    RequirementModel,
)
from backend.design.common.context import (
    DesignStage,
    DesignStatus,
    ContextBuilder,
)
from backend.design.common.mission import MissionAnalysisService
from backend.design.advisor.recommendation import (
    VehicleType,
    RecommendationScore,
    RecommendationReason,
    VehicleRecommendation,
    RecommendationReport,
    QuadcopterRecommendationStrategy,
    FixedWingRecommendationStrategy,
    VTOLRecommendationStrategy,
    RecommendationRanker,
    RecommendationExplanationService,
    RecommendationPipeline,
    RecommendationEngine,
    MissingMissionProfileError,
)


def test_recommendation_enums():
    """Verify recommendation enum member values."""
    assert VehicleType.QUADCOPTER == "QUADCOPTER"
    assert VehicleType.FIXED_WING == "FIXED_WING"
    assert VehicleType.VTOL == "VTOL"
    assert RecommendationScore.EXCELLENT == "EXCELLENT"
    assert RecommendationScore.UNSUITABLE == "UNSUITABLE"
    assert RecommendationReason.HOVER_CAPABILITY == "HOVER_CAPABILITY"
    assert RecommendationReason.RANGE == "RANGE"


def test_quadcopter_strategy_evaluation():
    """Verify QuadcopterRecommendationStrategy assigns high score for short-range hover and low score for long-range."""
    service = MissionAnalysisService()

    # Short range mission -> High quadcopter score
    req_short = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=5.0,
        cruise_speed_kmh=40.0
    )
    profile_short = service.analyze_requirements(req_short).mission_profile
    strategy = QuadcopterRecommendationStrategy()

    rec_short = strategy.evaluate(profile_short)
    assert rec_short.vehicle_type == VehicleType.QUADCOPTER
    assert rec_short.overall_score >= 0.70

    # Long range mission -> Low quadcopter score
    req_long = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=2.0,
        target_flight_time_min=60.0,
        target_range_km=50.0,
        cruise_speed_kmh=60.0
    )
    profile_long = service.analyze_requirements(req_long).mission_profile
    rec_long = strategy.evaluate(profile_long)
    assert rec_long.overall_score < rec_short.overall_score


def test_fixed_wing_strategy_evaluation():
    """Verify FixedWingRecommendationStrategy evaluates long range highly and penalizes vertical takeoff requirement."""
    service = MissionAnalysisService()

    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=2.0,
        target_flight_time_min=60.0,
        target_range_km=50.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING
    )
    profile = service.analyze_requirements(req).mission_profile
    strategy = FixedWingRecommendationStrategy()

    rec = strategy.evaluate(profile)
    assert rec.vehicle_type == VehicleType.FIXED_WING
    assert rec.overall_score >= 0.80
    assert rec.engineering_score in (RecommendationScore.EXCELLENT, RecommendationScore.GOOD)


def test_vtol_strategy_evaluation():
    """Verify VTOLRecommendationStrategy assigns high score for Vertical Takeoff combined with Long Range."""
    service = MissionAnalysisService()

    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=3.0,
        target_flight_time_min=50.0,
        target_range_km=40.0,
        cruise_speed_kmh=75.0,
        takeoff_type=TakeoffType.VERTICAL,
        landing_type=LandingType.VERTICAL
    )
    profile = service.analyze_requirements(req).mission_profile
    strategy = VTOLRecommendationStrategy()

    rec = strategy.evaluate(profile)
    assert rec.vehicle_type == VehicleType.VTOL
    assert rec.overall_score >= 0.85
    assert rec.engineering_score == RecommendationScore.EXCELLENT


def test_recommendation_ranker():
    """Verify RecommendationRanker sorts recommendations by overall_score descending."""
    ranker = RecommendationRanker()

    r1 = VehicleRecommendation(
        vehicle_type=VehicleType.QUADCOPTER, overall_score=0.60, confidence=0.9,
        engineering_score=RecommendationScore.ACCEPTABLE, estimated_cost=1500, estimated_complexity="Low"
    )
    r2 = VehicleRecommendation(
        vehicle_type=VehicleType.VTOL, overall_score=0.90, confidence=0.9,
        engineering_score=RecommendationScore.EXCELLENT, estimated_cost=8500, estimated_complexity="High"
    )
    r3 = VehicleRecommendation(
        vehicle_type=VehicleType.FIXED_WING, overall_score=0.75, confidence=0.9,
        engineering_score=RecommendationScore.GOOD, estimated_cost=4500, estimated_complexity="Medium"
    )

    ranked = ranker.rank([r1, r2, r3])

    assert [rec.vehicle_type for rec in ranked] == [VehicleType.VTOL, VehicleType.FIXED_WING, VehicleType.QUADCOPTER]


def test_recommendation_engine_workflow():
    """Verify RecommendationEngine updates DesignContext with RecommendationReport and advances stage to WAITING_FOR_USER."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=3.0,
        target_flight_time_min=45.0,
        target_range_km=35.0,
        cruise_speed_kmh=60.0
    )

    context = ContextBuilder.create_context(req)
    mission_service = MissionAnalysisService()
    context.mission_profile = mission_service.analyze_requirements(req).mission_profile

    engine = RecommendationEngine()
    updated_context = engine.recommend(context)

    assert updated_context.vehicle_recommendations is not None
    assert isinstance(updated_context.vehicle_recommendations, RecommendationReport)
    assert updated_context.current_stage == DesignStage.VEHICLE_RECOMMENDATION
    assert updated_context.current_status == DesignStatus.WAITING_FOR_USER
    assert len(updated_context.snapshots) == 2


def test_missing_mission_profile_raises_error():
    """Verify MissingMissionProfileError is raised when context has no mission_profile."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=50.0
    )

    context = ContextBuilder.create_context(req)  # context.mission_profile is None
    engine = RecommendationEngine()

    with pytest.raises(MissingMissionProfileError):
        engine.recommend(context)
