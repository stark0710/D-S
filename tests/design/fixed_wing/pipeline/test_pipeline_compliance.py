import pytest
from unittest.mock import MagicMock
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
from backend.design.fixed_wing.verification.compliance_report import ComplianceReport

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

def test_pipeline_compliant_aircraft(base_requirements):
    """Verify that a compliant aircraft passes the pipeline checks."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    
    # Mock verification result to have a compliant report
    mock_report = MagicMock(spec=ComplianceReport)
    mock_report.is_fully_compliant = True
    
    mock_verif_res = MagicMock()
    mock_verif_res.compliance_report = mock_report
    
    pipeline._verification_engine.process_verification = MagicMock(return_value=mock_verif_res)
    
    res = pipeline.execute(base_requirements)
    assert res.status == PipelineStatus.SUCCESS
    assert res.success is True

def test_pipeline_non_compliant_aircraft(base_requirements):
    """Verify that a non-compliant aircraft fails the pipeline checks."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    
    # Mock verification result to have a non-compliant report
    mock_report = MagicMock(spec=ComplianceReport)
    mock_report.is_fully_compliant = False
    
    mock_verif_res = MagicMock()
    mock_verif_res.compliance_report = mock_report
    
    pipeline._verification_engine.process_verification = MagicMock(return_value=mock_verif_res)
    
    res = pipeline.execute(base_requirements)
    assert res.status == PipelineStatus.VERIFICATION_FAILED
    assert res.success is False
    assert "Aircraft design failed verification compliance checks." in res.errors

def test_pipeline_missing_compliance_report(base_requirements):
    """Verify that a missing compliance report fails safety-critically."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    
    # Mock verification result to have NO compliance report
    mock_verif_res = MagicMock()
    mock_verif_res.compliance_report = None
    
    pipeline._verification_engine.process_verification = MagicMock(return_value=mock_verif_res)
    
    res = pipeline.execute(base_requirements)
    assert res.status == PipelineStatus.VERIFICATION_FAILED
    assert res.success is False
    assert "Aircraft design failed verification compliance checks." in res.errors

def test_pipeline_missing_verification_result(base_requirements):
    """Verify that a missing verification result fails safety-critically."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    
    # Mock process_verification to return None
    pipeline._verification_engine.process_verification = MagicMock(return_value=None)
    
    res = pipeline.execute(base_requirements)
    assert res.status == PipelineStatus.VERIFICATION_FAILED
    assert res.success is False
    assert "Aircraft design failed verification compliance checks." in res.errors
