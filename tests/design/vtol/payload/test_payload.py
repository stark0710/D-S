import pytest

from backend.design.vtol.payload.payload_engine import PayloadEngine
from backend.design.vtol.payload.payload_requirements import PayloadRequirements
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
        hover_duration_min=5.0,
        hover_altitude_m=100.0,
        wind_limit_hover_kts=12.0,
        climb_rate_vertical_m_s=2.5,
        descent_rate_vertical_m_s=2.0,
    )
    transition = TransitionRequirements(
        transition_speed_kmh=60.0,
        transition_duration_s=15.0,
        transition_altitude_m=120.0,
        max_transition_pitch_deg=20.0,
    )
    cruise = CruiseRequirements(
        cruise_speed_kmh=100.0,
        cruise_altitude_m=150.0,
        cruise_range_km=30.0,
        cruise_endurance_min=20.0,
        wind_limit_cruise_kts=18.0,
    )
    profile = MissionProfile(
        mission_category=VTOLMissionCategory.SURVEY,
        vtol_type=VTOLType.LIFT_CRUISE,
        payload_kg=5.0,
        total_endurance_min=25.0,
        total_range_km=30.0,
        air_density_hover_kg_m3=1.21,
        air_density_cruise_kg_m3=1.20,
        energy_demand_hover_kwh=0.5,
        energy_demand_cruise_kwh=1.2,
        energy_demand_transition_kwh=0.1,
        total_energy_demand_kwh=1.8,
        complexity_score=0.55,
        complexity_category="Medium",
    )
    analysis = MissionAnalysis(
        hover_priority=0.6,
        cruise_priority=0.4,
        transition_complexity=0.5,
        estimated_mtow_kg=30.0,
        lift_to_drag_ratio_est=10.0,
        hover_thrust_to_weight_est=1.45,
        mission_energy_demand_kwh=1.8,
        mission_risk_score=0.4,
        mission_feasibility_score=85.0,
    )
    
    mission_result = MissionResult(
        mission_profile=profile,
        hover_requirements=hover,
        transition_requirements=transition,
        cruise_requirements=cruise,
        mission_analysis=analysis,
        engineering_notes=[],
        recommendations=[],
        warnings=[],
        metadata={},
    )
    
    # We can add mock attributes to WingResult to mock Mean Aerodynamic Chord
    wing_result = MockResult()
    class WingGeoMock:
        mean_aerodynamic_chord_m = 0.45
    wing_result.wing_geometry = WingGeoMock()
    
    return PayloadRequirements(
        mission_result=mission_result,
        configuration_result=MockResult(),
        wing_result=wing_result,
        airfoil_result=MockResult(),
        tail_result=MockResult(),
        fuselage_result=MockResult(),
        lift_system_result=MockResult(),
        forward_propulsion_result=MockResult(),
        electrical_result=MockResult(),
        avionics_result=MockResult()
    )

def test_survey_payload_selection(base_requirements):
    engine = PayloadEngine()
    result = engine.design(base_requirements)
    
    # Assert selection
    assert result.payload_selection.category == "RGB Camera"
    assert result.payload_selection.weight_kg <= 1.0
    
    # Assert mounting
    assert result.payload_mount.mount_type == "Gimbal 3-Axis"
    assert result.payload_mount.vibration_isolation is True
    
    # Assert interface mapping
    assert "USB3" in result.payload_interfaces.data_connections or "Ethernet" in result.payload_interfaces.data_connections
    
    # Assert power sizing
    assert result.payload_power.voltage_volts > 0
    assert result.payload_power.continuous_power_watts > 0
    
    # Assert thermal passive sizing
    assert result.payload_thermal.cooling_type == "Passive"
    
    # Check Center of Gravity estimations
    assert abs(result.payload_cg.cg_shift_pct_mac) <= 5.0
    assert result.payload_cg.cg_shift_x_m > 0 # Weight shifts CG forward in our calculations
    
    # Sizing analyses
    assert result.payload_analysis.packaging_efficiency_pct > 0
    assert result.payload_analysis.mission_suitability_score >= 0.90

def test_cargo_payload_selection(base_requirements):
    # Set to cargo mission
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.CARGO
    
    engine = PayloadEngine()
    result = engine.design(base_requirements)
    
    assert result.payload_selection.category == "Cargo Pod"
    assert result.payload_mount.mount_type == "Cargo Rails"
    assert result.payload_bay.fit_status is True
    assert result.payload_interfaces.control_protocol == "GPIO"
    assert result.payload_interfaces.quick_release_compatible is True

def test_preferred_overrides(base_requirements):
    base_requirements.preferred_payload_type = "Flir Duo Pro R"
    base_requirements.preferred_mount_type = "Fixed"
    
    engine = PayloadEngine()
    result = engine.design(base_requirements)
    
    assert result.payload_selection.name == "Flir Duo Pro R"
    assert result.payload_mount.mount_type == "Fixed"

def test_payload_validator_limits(base_requirements):
    from backend.design.vtol.payload.payload_constraints import PayloadConstraints
    
    # Constrain weight limits heavily to cause validation failures
    constraints = PayloadConstraints(
        max_payload_mass_kg=0.1,  # Too light for all cameras
        max_payload_power_watts=1.0  # Too low
    )
    
    engine = PayloadEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    assert len(result.warnings) > 0
    assert any("Payload mass" in w for w in result.warnings)
    assert any("Continuous power consumption" in w for w in result.warnings)
