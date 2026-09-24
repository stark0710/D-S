import pytest

from backend.design.vtol.report.report_engine import VTOLReportEngine
from backend.design.vtol.report.report_requirements import ReportRequirements
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
    
    return ReportRequirements(
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
        cad_result=MockResult(),
        manufacturing_result=MockResult(),
        preferred_export_format="PDF"
    )

def test_survey_report_generation(base_requirements):
    engine = VTOLReportEngine()
    result = engine.design(base_requirements)
    
    # Assert executive summary
    assert "Takeoff Weight" in result.executive_summary.key_metrics_table
    assert result.executive_summary.overall_compliance_status == "Compliant"
    
    # Assert section sizes
    assert len(result.engineering_sections) == 2
    assert len(result.performance_sections) == 1
    assert len(result.verification_sections) == 1
    
    # Assert traceability matrix
    assert len(result.traceability_matrix) > 0
    assert result.traceability_matrix["REQ_RANGE_15KM"] == "Verified (Actual: 32.5 km)"
    
    # Assert appendices
    assert len(result.appendices) == 1
    assert result.appendices[0].title == "Revision logs & calculations reference"
    
    # Assert exports
    assert len(result.exported_documents) == 1
    assert result.exported_documents[0].format_type == "PDF"
    assert result.exported_documents[0].page_count == 24
    
    assert len(result.warnings) == 0

def test_certification_report_strategy(base_requirements):
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.DELIVERY
    base_requirements.preferred_export_format = None  # test all default formats
    
    engine = VTOLReportEngine()
    result = engine.design(base_requirements)
    
    assert "detailed" in result.executive_summary.summary_text.lower()
    assert len(result.exported_documents) == 3  # PDF, HTML, Markdown

def test_validator_fails(base_requirements):
    from backend.design.vtol.report.report_constraints import ReportConstraints
    
    # highly restrict constraints
    constraints = ReportConstraints(
        min_required_sections_count=20,      # too high, actual is 9
        require_requirements_traceability=True
    )
    
    engine = VTOLReportEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    from backend.design.vtol.report.report_validator import ReportValidator
    errors = ReportValidator.validate(result, constraints)
    
    assert len(errors) > 0
    assert any("section count" in err.lower() for err in errors)
    
    # test missing traceability warning
    result.traceability_matrix = {}
    errors_trace = ReportValidator.validate(result, constraints)
    assert any("traceability matrix is missing" in err.lower() for err in errors_trace)
