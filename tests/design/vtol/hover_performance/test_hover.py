import pytest

from backend.design.vtol.hover_performance.hover_engine import HoverPerformanceEngine
from backend.design.vtol.hover_performance.hover_requirements import HoverRequirements
from backend.design.vtol.mission import (
    MissionResult,
    MissionProfile,
    HoverRequirements as MissionHoverReq,
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
    hover = MissionHoverReq(
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
    
    # Mock propulsion layout
    config_result = MockResult()
    class PropLayout:
        motor_count = 8
    config_result.propulsion_layout = PropLayout()
    
    # Mock electrical battery pack
    elec_result = MockResult()
    class BatPack:
        total_capacity_kwh = 2.0
    elec_result.battery_pack = BatPack()
    
    return HoverRequirements(
        mission_result=mission_result,
        configuration_result=config_result,
        wing_result=MockResult(),
        airfoil_result=MockResult(),
        tail_result=MockResult(),
        fuselage_result=MockResult(),
        lift_system_result=MockResult(),
        forward_propulsion_result=MockResult(),
        electrical_result=elec_result,
        avionics_result=MockResult(),
        payload_result=MockResult(),
        mass_properties_result=MockResult()
    )

def test_survey_hover_performance(base_requirements):
    engine = HoverPerformanceEngine()
    result = engine.design(base_requirements)
    
    # Assert hover thrust
    assert result.hover_thrust.total_disk_area_m2 > 0
    assert result.hover_thrust.thrust_margin_ratio >= 1.30
    assert result.hover_thrust.ground_effect_thrust_gain_pct > 0
    
    # Assert hover power
    assert result.hover_power.total_hover_power_watts > 0
    assert result.hover_power.voltage_sag_multiplier <= 1.0
    
    # Assert efficiency
    assert 0.0 < result.hover_efficiency.figure_of_merit < 1.0
    assert result.hover_efficiency.hover_endurance_min > 0.0
    
    # Assert stability & control
    assert result.hover_stability.is_stably_damped is True
    assert result.hover_control.has_sufficient_authority is True
    
    # Assert wind / altitude / failure
    assert result.wind_analysis.crosswind_limit_kts >= 25.0
    assert result.altitude_analysis.hover_ceiling_oge_m > 0
    
    assert len(result.warnings) == 0

def test_military_hover_performance(base_requirements):
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.MILITARY
    base_requirements.mission_result.mission_analysis.estimated_mtow_kg = 50.0
    
    engine = HoverPerformanceEngine()
    result = engine.design(base_requirements)
    
    # Military should configure higher thrust margins
    assert result.hover_thrust.thrust_margin_ratio == 1.70
    assert result.wind_analysis.crosswind_limit_kts == 35.0
    assert result.hover_control.control_headroom_pct == 30.0

def test_validator_fails(base_requirements):
    from backend.design.vtol.hover_performance.hover_constraints import HoverConstraints
    
    # Highly restrict constraints to generate errors
    constraints = HoverConstraints(
        min_hover_thrust_margin_ratio=3.0,  # too high
        max_hover_power_watts=1.0,           # too low
        min_control_authority_headroom_pct=95.0, # too high
        max_wind_velocity_kts=100.0          # too high
    )
    
    engine = HoverPerformanceEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    assert len(result.warnings) > 0
    assert any("thrust-to-weight ratio" in w for w in result.warnings)
    assert any("power consumption" in w for w in result.warnings)
    assert any("control authority headroom" in w for w in result.warnings)
    assert any("Crosswind hover tolerance" in w for w in result.warnings)
