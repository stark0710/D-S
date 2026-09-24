import pytest
from unittest.mock import MagicMock
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from backend.design.fixed_wing.verification.verification_engine import VerificationEngine
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements
from backend.design.fixed_wing.verification.compliance_report import ComplianceReport
from backend.design.fixed_wing.avionics.telemetry_selector import TelemetrySelector
from backend.design.fixed_wing.payload.payload_selector import PayloadSelector, PayloadType
from backend.design.fixed_wing.payload.payload_result import PayloadResult
from backend.design.fixed_wing.payload.payload_engine import PayloadEngine
from backend.design.fixed_wing.mass_properties.mass_properties_engine import MassPropertiesEngine
from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements

@pytest.fixture
def base_requirements():
    return RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )

def test_verification_engine_aggregation_states():
    """Verify aggregation states: FAILED on violations, VERIFIED_WITH_WARNINGS on warnings, VERIFIED on clean pass."""
    engine = VerificationEngine()
    
    # Mock requirements with None to trigger missing mandatory check -> FAILED
    result_none = engine.process_verification(None)
    assert result_none.verification_status == "FAILED"
    assert "Missing mandatory result:" in result_none.constraint_violations[0]
    
    # Mock a dummy reqs object
    dummy_reqs = MagicMock(spec=VerificationRequirements)
    for field in ["mission_result", "configuration_result", "wing_result", "airfoil_result", "tail_result", "fuselage_result", "propulsion_result", "avionics_result", "payload_result", "mass_result", "flight_result"]:
        setattr(dummy_reqs, field, MagicMock())
    
    # 1. Clean pass (no violations, no warnings)
    engine._req_checker.check_requirements = MagicMock(return_value=[])
    engine._mission_checker.check_mission_suitability = MagicMock(return_value=[])
    engine._perf_checker.check_performance_suitability = MagicMock(return_value=[])
    engine._stab_checker.check_stability_suitability = MagicMock(return_value=[])
    engine._safety_checker.check_safety_suitability = MagicMock(return_value=[])
    engine._comp_checker.check_subsystem_compatibility = MagicMock(return_value=[])
    engine._const_checker.check_constraints = MagicMock(return_value=[])
    
    res_clean = engine.process_verification(dummy_reqs)
    assert res_clean.verification_status == "VERIFIED"
    assert res_clean.compliance_report.is_fully_compliant is True
    
    # 2. Warnings only (e.g. req_failures, no violations)
    engine._req_checker.check_requirements = MagicMock(return_value=["Warning label"])
    res_warn = engine.process_verification(dummy_reqs)
    assert res_warn.verification_status == "VERIFIED_WITH_WARNINGS"
    assert res_warn.compliance_report.is_fully_compliant is True
    
    # 3. Violations exist (e.g. safety check failure is now a violation/hard fail)
    engine._req_checker.check_requirements = MagicMock(return_value=[])
    engine._safety_checker.check_safety_suitability = MagicMock(return_value=["Safety critical deficiency"])
    res_fail = engine.process_verification(dummy_reqs)
    assert res_fail.verification_status == "FAILED"
    assert res_fail.compliance_report.is_fully_compliant is False

def test_telemetry_selector_database_limits():
    """Verify that TelemetrySelector raises COMPONENT_DATABASE_LIMITATION for range > 80 km."""
    selector = TelemetrySelector()
    
    # Range of 50 km is valid (Microhard or Silvus)
    rec = selector.select_telemetry(50.0, needs_video=False)
    assert rec.max_range_km >= 50.0
    
    # Range of 100 km should raise database limitation error
    with pytest.raises(ValueError) as excinfo:
        selector.select_telemetry(100.0, needs_video=False)
    assert "COMPONENT_DATABASE_LIMITATION" in str(excinfo.value)
    assert "exceeds the maximum range available" in str(excinfo.value)
    
    # Range of 70 km requiring video but none matching bandwidth + range
    # Silvus matches video and 80km range, so it should succeed.
    rec_vid = selector.select_telemetry(70.0, needs_video=True)
    assert rec_vid.name == "Silvus StreamCaster Lite"

def test_payload_mass_propagation_and_conservation():
    """Verify requested vs installed payload mass and its propagation into mass properties."""
    # Sizer checks
    engine = PayloadEngine()
    reqs = MagicMock()
    reqs.preferred_payloads = None
    reqs.mission_result.mission_profile.payload_kg = 0.5
    reqs.mission_result.mission_profile.mission_category.value = "Survey"
    reqs.mission_result.constraints.maximum_takeoff_weight_kg = 20.0
    reqs.fuselage_result.fuselage_geometry.payload_bay_length_m = 0.5
    reqs.fuselage_result.fuselage_geometry.payload_bay_width_m = 0.2
    reqs.fuselage_result.fuselage_geometry.payload_bay_height_m = 0.2
    reqs.wing_result.wing_geometry.quarter_chord_x_m = 0.3
    reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m = 0.25
    
    result = engine.process_payload_design(reqs)
    
    assert result.requested_payload_mass_kg == 0.5
    assert result.installed_payload_mass_kg == 0.51
    assert result.payload_design_margin_kg == pytest.approx(0.01)
    
    # Test Payload Selector raising COMPONENT_DATABASE_LIMITATION when constraint is extremely strict
    p_selector = PayloadSelector()
    with pytest.raises(ValueError) as excinfo:
        p_selector.select_payload(PayloadType.RGB_CAMERA, 0.05)
    assert "COMPONENT_DATABASE_LIMITATION" in str(excinfo.value)
    assert "Lightest available component of type" in str(excinfo.value)

def test_pipeline_taxonomy_mappings(base_requirements):
    """Verify that pipeline maps errors to correct PipelineStatus enums."""
    from backend.design.fixed_wing.payload.payload_engine import PayloadEngine
    orig_process = PayloadEngine.process_payload_design
    
    def mock_payload_error(*args, **kwargs):
        raise ValueError("COMPONENT_DATABASE_LIMITATION: Sized payload weight exceeds maximum structural")
        
    PayloadEngine.process_payload_design = mock_payload_error
    try:
        pipeline = FixedWingDesignPipeline(raise_on_failure=False)
        res = pipeline.execute(base_requirements)
        assert res.status == PipelineStatus.COMPONENT_DATABASE_LIMITATION
    finally:
        PayloadEngine.process_payload_design = orig_process
