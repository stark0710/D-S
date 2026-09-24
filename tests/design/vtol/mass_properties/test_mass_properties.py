import pytest

from backend.design.vtol.mass_properties.mass_properties_engine import MassPropertiesEngine
from backend.design.vtol.mass_properties.mass_requirements import MassRequirements
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
    
    wing_result = MockResult()
    class WingGeo:
        mean_aerodynamic_chord_m = 0.40
    wing_result.wing_geometry = WingGeo()
    
    payload_result = MockResult()
    class PayloadSel:
        weight_kg = 0.65
    payload_result.payload_selection = PayloadSel()
    
    return MassRequirements(
        mission_result=mission_result,
        configuration_result=MockResult(),
        wing_result=wing_result,
        airfoil_result=MockResult(),
        tail_result=MockResult(),
        fuselage_result=MockResult(),
        lift_system_result=MockResult(),
        forward_propulsion_result=MockResult(),
        electrical_result=MockResult(),
        avionics_result=MockResult(),
        payload_result=payload_result
    )

def test_survey_mass_properties(base_requirements):
    engine = MassPropertiesEngine()
    result = engine.design(base_requirements)
    
    # Assert weight budget
    assert result.weight_budget.max_takeoff_weight_kg == 25.0
    assert result.weight_budget.empty_weight_kg == 15.0
    assert result.weight_budget.payload_mass_kg == 0.65
    
    # Assert center of gravity
    assert result.center_of_gravity.x_m > 0
    assert 15.0 <= result.center_of_gravity.x_pct_mac <= 35.0
    
    # Assert inertia
    assert result.inertia_tensor.ixx_kg_m2 > 0
    assert result.inertia_tensor.iyy_kg_m2 > 0
    assert result.inertia_tensor.izz_kg_m2 > 0
    
    # Assert shift analyses
    assert result.payload_shift_analysis.is_safe is True
    assert result.battery_shift_analysis.counterbalance_capable is True
    
    # Assert validator warnings empty
    assert len(result.warnings) == 0

def test_cargo_mass_properties(base_requirements):
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.CARGO
    base_requirements.mission_result.mission_analysis.estimated_mtow_kg = 35.0
    base_requirements.payload_result.payload_selection.weight_kg = 5.0
    
    engine = MassPropertiesEngine()
    result = engine.design(base_requirements)
    
    assert result.weight_budget.max_takeoff_weight_kg == 35.0
    assert result.weight_budget.payload_mass_kg == 5.0
    assert result.weight_budget.empty_weight_kg == 35.0 * 0.55
    assert result.mass_analysis.cruise_static_margin > 0.05

def test_validator_fails(base_requirements):
    from backend.design.vtol.mass_properties.mass_constraints import MassConstraints
    
    # Restrict constraints to cause warnings
    constraints = MassConstraints(
        max_takeoff_weight_kg=10.0,  # too low
        min_static_margin=0.90       # too high
    )
    engine = MassPropertiesEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    assert len(result.warnings) > 0
    assert any("takeoff weight" in w for w in result.warnings)
    assert any("static margin" in w for w in result.warnings)
