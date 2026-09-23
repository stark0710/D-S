import pytest

from backend.design.vtol.verification.verification_engine import VTOLVerificationEngine
from backend.design.vtol.verification.verification_requirements import VerificationRequirements
from backend.design.vtol.mission import (
    MissionResult,
    MissionProfile,
    HoverRequirements,
    TransitionRequirements,
    CruiseRequirements,
    MissionAnalysis,
    VTOLMissionCategory,
    VTOLType,
)

class MockResult:
    pass

@pytest.fixture
def base_requirements():
    hover = HoverRequirements(
        hover_duration_min=5.0, hover_altitude_m=100.0, wind_limit_hover_kts=12.0,
        climb_rate_vertical_m_s=2.5, descent_rate_vertical_m_s=2.0
    )
    transition = TransitionRequirements(
        transition_speed_kmh=60.0, transition_duration_s=15.0, transition_altitude_m=120.0,
        max_transition_pitch_deg=20.0
    )
    cruise = CruiseRequirements(
        cruise_speed_kmh=100.0, cruise_altitude_m=150.0, cruise_range_km=30.0,
        cruise_endurance_min=20.0, wind_limit_cruise_kts=18.0
    )
    profile = MissionProfile(
        mission_category=VTOLMissionCategory.SURVEY,
        vtol_type=VTOLType.LIFT_CRUISE,
        payload_kg=5.0, total_endurance_min=25.0, total_range_km=30.0,
        air_density_hover_kg_m3=1.21, air_density_cruise_kg_m3=1.20,
        energy_demand_hover_kwh=0.5, energy_demand_cruise_kwh=1.2,
        energy_demand_transition_kwh=0.1, total_energy_demand_kwh=1.8,
        complexity_score=0.55, complexity_category="Medium"
    )
    analysis = MissionAnalysis(
        hover_priority=0.6, cruise_priority=0.4, transition_complexity=0.5,
        estimated_mtow_kg=25.0, lift_to_drag_ratio_est=10.0, hover_thrust_to_weight_est=1.45,
        mission_energy_demand_kwh=1.8, mission_risk_score=0.4, mission_feasibility_score=85.0
    )
    mission_result = MissionResult(
        mission_profile=profile, hover_requirements=hover, transition_requirements=transition,
        cruise_requirements=cruise, mission_analysis=analysis
    )
    
    # Mock cruise result
    cruise_result = MockResult()
    class CruiseAnal:
        range_km = 32.5
        endurance_min = 22.0
        min_stability_margin = 0.08
    cruise_result.cruise_analysis = CruiseAnal
    
    return VerificationRequirements(
        mission_result=mission_result,
        configuration_result=MockResult(),
        wing_result=MockResult(),
        airfoil_result=MockResult(),
        tail_result=MockResult(),
        fuselage_result=MockResult(),
        lift_system_result=MockResult(),
        forward_propulsion_result=MockResult(),
        electrical_result=MockResult(),
        avionics_result=MockResult(),
        payload_result=MockResult(),
        mass_properties_result=MockResult(),
        hover_performance_result=MockResult(),
        transition_result=MockResult(),
        cruise_performance_result=cruise_result
    )

def test_survey_verification(base_requirements):
    engine = VTOLVerificationEngine()
    result = engine.design(base_requirements)
    
    # Assert mission verification
    assert result.mission_verification.is_mission_feasible is True
    assert result.mission_verification.mission_success_probability_pct > 80.0
    
    # Assert compliance matrix
    assert len(result.compliance_matrix.checklist) > 0
    assert result.compliance_matrix.compliance_score_pct == 100.0
    
    # Assert performance & stability
    assert result.performance_verification.average_performance_score_pct > 85.0
    assert result.stability_verification.is_stably_controllable is True
    
    # Assert reliability & safety
    assert result.reliability_verification.estimated_mtbf_hours >= 100.0
    assert result.safety_verification.is_safety_verified is True
    
    assert len(result.warnings) == 0

def test_military_verification(base_requirements):
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.MILITARY
    
    engine = VTOLVerificationEngine()
    result = engine.design(base_requirements)
    
    # Check that military strategy sets higher redundancy indexes
    assert result.reliability_verification.redundancy_level_index == 3.0
    assert result.environment_verification.wind_tolerance_limit_kts == 35.0

def test_validator_fails(base_requirements):
    from backend.design.vtol.verification.verification_constraints import VerificationConstraints
    
    # Highly restrict constraints to generate errors
    constraints = VerificationConstraints(
        min_overall_compliance_score_pct=100.1, # too high
        min_reliability_mtbf_hours=5000.0,     # too high
        min_stability_safety_margin_pct=95.0    # too high
    )
    
    engine = VTOLVerificationEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    assert len(result.warnings) > 0
    assert any("compliance score" in w for w in result.warnings)
    assert any("Estimated MTBF" in w for w in result.warnings)
    assert any("stability margin" in w for w in result.warnings)
