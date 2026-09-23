import pytest

from backend.design.vtol.avionics.avionics_engine import AvionicsEngine
from backend.design.vtol.avionics.avionics_requirements import AvionicsRequirements
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
        payload_kg=10.0,
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
    
    return AvionicsRequirements(
        mission_result=mission_result,
        configuration_result=MockResult(),
        wing_result=MockResult(),
        airfoil_result=MockResult(),
        tail_result=MockResult(),
        fuselage_result=MockResult(),
        lift_system_result=MockResult(),
        forward_propulsion_result=MockResult(),
        electrical_result=MockResult()
    )

def test_survey_avionics(base_requirements):
    engine = AvionicsEngine()
    result = engine.design(base_requirements)
    
    # Check flight controller and companion computer
    assert result.flight_controller.redundancy_level in [2, 3]
    assert result.companion_computer.name in ["Raspberry Pi 4", "Jetson Nano", "Jetson Orin NX"]
    
    # Check sensor suite details
    assert result.sensor_suite.has_rangefinder is True
    assert result.sensor_suite.rangefinder_type == "Lidar"
    assert result.sensor_suite.gnss_receiver_type == "RTK"
    
    # Check EKF parameters
    assert result.navigation_system.rtk_active is True
    assert result.navigation_system.estimated_position_accuracy_m <= 0.05
    
    # Analysis & evaluation metrics
    assert result.analysis.cpu_utilization_pct <= 85.0
    assert result.analysis.power_consumption_watts <= 100.0
    assert result.analysis.reliability_score >= 0.85
    assert result.analysis.fault_tolerance_score >= 0.5
    
    # Health monitor & synchronizations
    assert result.health_monitor.pre_flight_checks_active is True
    assert result.time_synchronization.synchronization_protocol in ["NTP", "PTP"]

def test_military_avionics(base_requirements):
    # Overwrite category to military
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.MILITARY
    
    engine = AvionicsEngine()
    result = engine.design(base_requirements)
    
    assert result.flight_controller.redundancy_level == 3
    assert result.flight_controller.has_ethernet is True
    assert result.companion_computer.tops >= 100.0
    assert result.sensor_suite.has_optical_flow is True
    assert result.redundancy_analysis.dual_gps_active is True
    assert result.time_synchronization.synchronization_protocol == "PTP"

def test_preferred_overrides(base_requirements):
    base_requirements.preferred_flight_controller = "Auterion Skynode"
    base_requirements.preferred_companion_computer = "Jetson Orin NX"
    
    engine = AvionicsEngine()
    result = engine.design(base_requirements)
    
    assert result.flight_controller.name == "Auterion Skynode"
    assert result.companion_computer.name == "Jetson Orin NX"

def test_validator_warning(base_requirements):
    # Set constraints that will trigger warnings
    from backend.design.vtol.avionics.avionics_constraints import AvionicsConstraints
    constraints = AvionicsConstraints(
        max_cpu_utilization_pct=10.0,  # too low, will fail
        max_power_consumption_watts=1.0  # too low, will fail
    )
    engine = AvionicsEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    assert len(result.warnings) > 0
    assert any("CPU utilization" in w for w in result.warnings)
    assert any("Power draw" in w for w in result.warnings)
