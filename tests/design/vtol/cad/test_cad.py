import pytest

from backend.design.vtol.cad.cad_engine import VTOLCADEngine
from backend.design.vtol.cad.cad_requirements import CADRequirements
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
    
    return CADRequirements(
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
        cruise_performance_result=MockResult(),
        verification_result=MockResult(),
        optimization_result=MockResult(),
        preferred_export_format="STEP"
    )

def test_survey_cad_generation(base_requirements):
    engine = VTOLCADEngine()
    result = engine.design(base_requirements)
    
    # Assert assembly model
    assert result.assembly_model.assembly_name == "VTOL Complete Aircraft Assembly"
    assert len(result.assembly_model.nodes) > 0
    assert result.assembly_model.total_parts_count == 8
    
    # Assert parts
    assert len(result.part_models) == 3
    assert result.part_models[0].material_name == "Carbon Fiber Composite"
    
    # Assert reference geometry
    assert len(result.reference_geometry.planes) > 0
    assert result.reference_geometry.origin_point_mm == [0.0, 0.0, 0.0]
    
    # Assert analyses
    assert result.interference_report.is_interference_free is True
    assert result.clearance_report.is_clearance_safe is True
    
    # Assert exports
    assert len(result.exported_files) == 1
    assert result.exported_files[0].file_format == "STEP"
    assert result.exported_files[0].is_valid is True
    
    assert len(result.warnings) == 0

def test_cargo_cad_generation(base_requirements):
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.CARGO
    base_requirements.preferred_export_format = None  # test all default formats
    
    engine = VTOLCADEngine()
    result = engine.design(base_requirements)
    
    assert result.clearance_report.actual_clearance_mm == 90.0
    assert len(result.exported_files) == 3  # STEP, STL, IGES

def test_validator_fails(base_requirements):
    from backend.design.vtol.cad.cad_constraints import CADConstraints
    
    # highly restrict constraints
    constraints = CADConstraints(
        min_rotor_clearance_mm=100.0,  # too high
        max_interference_volume_mm3=-1.0 # impossible, triggers warning on any overlap >= 0
    )
    
    engine = VTOLCADEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    # inject warning manually or let validator run
    from backend.design.vtol.cad.cad_validator import CADValidator
    errors = CADValidator.validate(result, constraints)
    
    assert len(errors) > 0
    assert any("rotor clearance" in err.lower() for err in errors)
