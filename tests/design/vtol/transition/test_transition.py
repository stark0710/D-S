import pytest

from backend.design.vtol.transition.transition_engine import TransitionFlightEngine
from backend.design.vtol.transition.transition_requirements import TransitionRequirements
from backend.design.vtol.mission import (
    MissionResult,
    MissionProfile,
    HoverRequirements,
    TransitionRequirements as MissionTransitionReq,
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
    transition = MissionTransitionReq(
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
    
    # Mock hover performance result
    hover_result = MockResult()
    class HoverPow:
        total_hover_power_watts = 3500.0
    hover_result.hover_power = HoverPow()
    
    return TransitionRequirements(
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
        hover_performance_result=hover_result
    )

def test_lift_cruise_transition_performance(base_requirements):
    engine = TransitionFlightEngine()
    result = engine.design(base_requirements)
    
    # Assert scheduling
    assert len(result.transition_schedule.airspeed_steps_kmh) > 0
    assert result.transition_schedule.lift_throttle_percentage[-1] == 0.0
    assert result.transition_schedule.forward_throttle_percentage[-1] == 100.0
    
    # Assert aerodynamic & propulsion
    assert result.aerodynamic_analysis.wing_lift_growth_coefficient > 0.0
    assert result.propulsion_analysis.rotor_unloading_speed_kmh > 0.0
    
    # Assert stability & control
    assert result.stability_analysis.min_stability_margin > 0.0
    assert len(result.control_schedule.control_stages) > 0
    
    # Assert energy & failure
    assert result.energy_analysis.total_energy_consumed_kwh > 0.0
    assert result.failure_analysis.oei_conversion_safety_status is True
    
    assert len(result.warnings) == 0

def test_quadplane_transition_strategy(base_requirements):
    base_requirements.mission_result.mission_profile.vtol_type = VTOLType.QUADPLANE
    
    engine = TransitionFlightEngine()
    result = engine.design(base_requirements)
    
    assert result.transition_analysis.conversion_speed_kmh == 55.0
    assert result.transition_analysis.duration_s == 18.0

def test_validator_fails(base_requirements):
    from backend.design.vtol.transition.transition_constraints import TransitionConstraints
    
    # Highly restrict constraints to generate errors
    constraints = TransitionConstraints(
        min_conversion_speed_kmh=100.0,    # too high
        max_transition_duration_s=2.0,     # too low
        min_stability_margin_transition=0.50 # too high
    )
    
    engine = TransitionFlightEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    assert len(result.warnings) > 0
    assert any("conversion speed" in w for w in result.warnings)
    assert any("duration" in w for w in result.warnings)
    assert any("stability margin" in w for w in result.warnings)
