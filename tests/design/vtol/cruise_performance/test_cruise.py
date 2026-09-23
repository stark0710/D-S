import pytest

from backend.design.vtol.cruise_performance.cruise_engine import CruisePerformanceEngine
from backend.design.vtol.cruise_performance.cruise_requirements import CruiseRequirements
from backend.design.vtol.mission import (
    MissionResult,
    MissionProfile,
    HoverRequirements,
    TransitionRequirements,
    CruiseRequirements as MissionCruiseReq,
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
    cruise = MissionCruiseReq(
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
    
    # Mock hover performance result
    hover_result = MockResult()
    class HoverEff:
        energy_consumption_kwh_min = 0.05
    hover_result.hover_efficiency = HoverEff()
    
    # Mock transition result
    transition_result = MockResult()
    class TransEnergy:
        total_energy_consumed_kwh = 0.04
    transition_result.energy_analysis = TransEnergy()
    
    return CruiseRequirements(
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
        hover_performance_result=hover_result,
        transition_result=transition_result
    )

def test_survey_cruise_performance(base_requirements):
    engine = CruisePerformanceEngine()
    result = engine.design(base_requirements)
    
    # Assert speed analysis
    assert result.speed_analysis.cruise_speed_kmh == 100.0
    assert result.speed_analysis.stall_speed_kmh > 0
    assert result.speed_analysis.best_range_speed_kmh > 0
    
    # Assert power analysis
    assert result.power_analysis.cruise_power_watts > 0
    assert result.power_analysis.drag_n > 0
    
    # Assert range & endurance
    assert result.range_analysis.estimated_range_km > 0.0
    assert result.endurance_analysis.estimated_endurance_min > 0.0
    
    # Assert climb & descent
    assert result.climb_analysis.max_rate_of_climb_m_s >= 2.0
    assert result.descent_analysis.nominal_descent_rate_m_s > 0.0
    
    # Assert envelope & maneuvers
    assert result.performance_envelope.service_ceiling_m > 0
    assert result.maneuver_analysis.max_bank_angle_deg > 0
    
    assert len(result.warnings) == 0

def test_long_endurance_strategy(base_requirements):
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.LONG_ENDURANCE
    
    engine = CruisePerformanceEngine()
    result = engine.design(base_requirements)
    
    # Check that cleaner glider L/D of 12.5 gives better specific range
    assert result.descent_analysis.best_glide_ratio == 12.5

def test_validator_fails(base_requirements):
    from backend.design.vtol.cruise_performance.cruise_constraints import CruiseConstraints
    
    # Highly restrict constraints to generate errors
    constraints = CruiseConstraints(
        min_range_km=1000.0,         # too high
        min_endurance_min=500.0,     # too high
        min_climb_rate_m_s=20.0,     # too high
        max_cruise_power_watts=1.0   # too low
    )
    
    engine = CruisePerformanceEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    assert len(result.warnings) > 0
    assert any("range" in w for w in result.warnings)
    assert any("endurance" in w for w in result.warnings)
    assert any("rate of climb" in w for w in result.warnings)
    assert any("power required" in w for w in result.warnings)
