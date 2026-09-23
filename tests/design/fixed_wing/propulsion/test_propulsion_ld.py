import pytest
from unittest.mock import MagicMock
from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine
from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.mission.mission_profile import MissionProfile
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_analysis import WingAnalysis
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult

@pytest.fixture
def mock_propulsion_requirements():
    m_profile = MagicMock(spec=MissionProfile)
    m_profile.mission_category = MagicMock()
    m_profile.mission_category.value = "Survey"
    m_profile.maximum_takeoff_weight_limit_kg = 5.0
    m_profile.cruise_speed_kmh = 90.0
    m_profile.operational_altitude_m = 100.0
    m_profile.air_density_kg_m3 = 1.2
    
    m_res = MagicMock(spec=MissionResult)
    m_res.mission_profile = m_profile
    
    config_res = MagicMock(spec=ConfigurationResult)
    config_res.propulsion_configuration = "Tractor"
    
    wing_geom = MagicMock(spec=WingGeometry)
    wing_geom.reference_area_m2 = 0.5
    wing_geom.wing_loading_kg_m2 = 10.0
    wing_geom.span_m = 2.0
    
    wing_anal = MagicMock(spec=WingAnalysis)
    wing_anal.aerodynamic_efficiency_score = 80.0 # estimated L/D = 80 * 0.18 = 14.4
    wing_anal.estimated_stall_speed_kmh = 45.0
    
    wing_res = MagicMock(spec=WingResult)
    wing_res.wing_geometry = wing_geom
    wing_res.analysis = wing_anal
    
    f_geom = MagicMock(spec=FuselageGeometry)
    f_geom.length_m = 1.5
    f_geom.height_m = 0.2
    
    fuse_res = MagicMock(spec=FuselageResult)
    fuse_res.fuselage_geometry = f_geom
    
    reqs = PropulsionRequirements(
        mission_result=m_res,
        configuration_result=config_res,
        wing_result=wing_res,
        airfoil_result=MagicMock(spec=AirfoilResult),
        tail_result=MagicMock(spec=TailResult),
        fuselage_result=fuse_res,
        flight_performance_result=None,
    )
    return reqs

def test_propulsion_uses_estimated_ld_initially(mock_propulsion_requirements):
    """Verify propulsion uses estimated L/D when flight_performance_result is None."""
    engine = PropulsionEngine()
    
    # Process propulsion design
    res = engine.process_propulsion_design(mock_propulsion_requirements)
    
    # Estimated L/D: 80.0 * 0.18 = 14.4
    # Cruise drag: weight_n / 14.4. MTOW = 5.0 kg -> weight_n = 5.0 * 9.80665 = 49.03 N.
    # Cruise drag = 49.03 / 14.4 = 3.40 N.
    assert abs(res.cruise_analysis.required_cruise_thrust_n - (49.03 / 14.4)) < 0.05

def test_propulsion_uses_final_calculated_ld_when_provided(mock_propulsion_requirements):
    """Verify propulsion uses the final calculated L/D when flight_performance_result is provided."""
    engine = PropulsionEngine()
    
    # Mock flight performance result with actual L/D = 12.0
    mock_flight_perf = MagicMock()
    mock_flight_perf.aerodynamic_analysis = MagicMock()
    mock_flight_perf.aerodynamic_analysis.lift_to_drag_ratio = 12.0
    
    mock_propulsion_requirements.flight_performance_result = mock_flight_perf
    
    res = engine.process_propulsion_design(mock_propulsion_requirements)
    
    # Cruise drag should use actual L/D = 12.0: cruise drag = 49.03 / 12.0 = 4.09 N.
    assert abs(res.cruise_analysis.required_cruise_thrust_n - (49.03 / 12.0)) < 0.05
