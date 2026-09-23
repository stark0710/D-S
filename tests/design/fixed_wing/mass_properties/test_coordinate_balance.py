import pytest
from unittest.mock import MagicMock
from backend.design.fixed_wing.mass_properties.mass_properties_engine import MassPropertiesEngine
from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
from backend.design.fixed_wing.mass_properties.component_mass import ComponentMass
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.mission.mission_profile import MissionProfile
from backend.design.fixed_wing.mission.mission_constraints import MissionConstraints
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult
from backend.design.fixed_wing.propulsion.power_analysis import PowerAnalysis as PropPowerAnalysis
from backend.design.fixed_wing.avionics.avionics_result import AvionicsResult
from backend.design.fixed_wing.avionics.power_analysis import PowerAnalysis as AvPowerAnalysis
from backend.design.fixed_wing.payload.payload_result import PayloadResult
from backend.design.fixed_wing.payload.payload_layout import PayloadLayout
from backend.design.fixed_wing.payload.payload_analysis import PayloadAnalysis
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail
from backend.design.fixed_wing.tail.tail_analysis import TailAnalysis

@pytest.fixture
def mock_mass_requirements():
    m_profile = MagicMock(spec=MissionProfile)
    m_profile.mission_category = MagicMock()
    m_profile.mission_category.value = "Survey"
    m_profile.payload_kg = 2.0
    m_profile.flight_time_min = 90.0
    m_profile.maximum_takeoff_weight_limit_kg = 15.0
    
    constraints = MagicMock(spec=MissionConstraints)
    constraints.maximum_takeoff_weight_kg = 25.0
    constraints.min_static_margin = 0.05
    constraints.max_static_margin = 0.25
    
    mission_res = MagicMock(spec=MissionResult)
    mission_res.mission_profile = m_profile
    mission_res.constraints = constraints
    
    # Wing Result
    wing_geom = MagicMock(spec=WingGeometry)
    wing_geom.reference_area_m2 = 1.2
    wing_geom.quarter_chord_x_m = 0.08
    wing_geom.mean_aerodynamic_chord_m = 0.32
    wing_geom.wing_loading_kg_m2 = 13.5
    
    wing_res = MagicMock(spec=WingResult)
    wing_res.wing_geometry = wing_geom
    
    # Fuselage Result
    f_geom = MagicMock(spec=FuselageGeometry)
    f_geom.length_m = 2.8
    f_geom.wing_attachment_x_m = 1.1 # wing attached at 1.1m from nose
    
    f_res = MagicMock(spec=FuselageResult)
    f_res.fuselage_geometry = f_geom
    f_layout = MagicMock()
    f_layout.flight_controller_placement_x_m = None
    f_res.internal_layout = f_layout
    
    # Configuration Result
    config_res = MagicMock(spec=ConfigurationResult)
    config_res.propulsion_configuration = "pusher"
    
    # Tail Result
    tail_res = MagicMock(spec=TailResult)
    h_tail = MagicMock(spec=HorizontalTail)
    h_tail.area_m2 = 0.12
    v_tail = MagicMock(spec=VerticalTail)
    v_tail.area_m2 = 0.09
    t_anal = MagicMock(spec=TailAnalysis)
    tail_res.horizontal_tail = h_tail
    tail_res.vertical_tail = v_tail
    tail_res.analysis = t_anal
    
    # Airfoil Result
    airfoil_res = MagicMock(spec=AirfoilResult)
    
    # Propulsion Result
    prop_power = MagicMock(spec=PropPowerAnalysis)
    prop_power.required_cruise_power_w = 400.0 # 400W cruise
    prop_power.metadata = {"motor_weight_g": 350}
    
    prop_res = MagicMock(spec=PropulsionResult)
    prop_res.power_analysis = prop_power
    
    # Avionics Result
    av_power = MagicMock(spec=AvPowerAnalysis)
    av_power.continuous_power_w = 15.0
    av_power.metadata = {"autopilot_weight_g": 85}
    
    av_res = MagicMock(spec=AvionicsResult)
    av_res.power_analysis = av_power
    
    # Payload Result
    pay_layout = MagicMock(spec=PayloadLayout)
    pay_layout.placement_x_m = 0.08 # placed at 0.08m from nose
    pay_anal = MagicMock(spec=PayloadAnalysis)
    pay_anal.power_consumption_w = 10.0
    
    pay_res = MagicMock(spec=PayloadResult)
    pay_res.payload_layout = pay_layout
    pay_res.payload_analysis = pay_anal
    pay_res.installed_payload_mass_kg = 2.0
    pay_res.requested_payload_mass_kg = 2.0
    
    reqs = MagicMock(spec=MassRequirements)
    reqs.mission_result = mission_res
    reqs.wing_result = wing_res
    reqs.airfoil_result = airfoil_res
    reqs.tail_result = tail_res
    reqs.fuselage_result = f_res
    reqs.propulsion_result = prop_res
    reqs.avionics_result = av_res
    reqs.payload_result = pay_res
    reqs.configuration_result = config_res
    reqs.structural_mass_override_kg = None
    
    return reqs

def test_target_cg_incorporates_wing_attachment(mock_mass_requirements):
    """Verify target CG uses the global coordinate system (wing_attachment_x_m offset)."""
    engine = MassPropertiesEngine()
    
    # Run the mass design process
    res = engine.process_mass_design(mock_mass_requirements)
    
    # We retrieve the actual wing attachment location
    f_geom = mock_mass_requirements.fuselage_result.fuselage_geometry
    wing_geom = mock_mass_requirements.wing_result.wing_geometry
    
    # The expected target CG should be wing_attachment_x + quarter_chord_x + 0.24 * MAC
    expected_target_cg = f_geom.wing_attachment_x_m + wing_geom.quarter_chord_x_m + 0.24 * wing_geom.mean_aerodynamic_chord_m
    # i.e., 1.1 + 0.08 + 0.24 * 0.32 = 1.2568 m
    
    # Check that the balanced center of gravity is very close to this expected target CG
    # (since the battery bay layout allows enough room for exact balance)
    assert abs(res.center_of_gravity[0] - expected_target_cg) < 0.05

def test_battery_sizing_units(mock_mass_requirements):
    """Verify that battery mass is calculated correctly using physical power energy units."""
    engine = MassPropertiesEngine()
    
    # Sizing variables:
    # prop_cruise = 400.0 W, avionics = 15.0 W, payload = 10.0 W -> continuous = 425.0 W
    # flight_time = 90 min (1.5 h)
    # Required energy (DoD 0.85): 425.0 * 1.5 / 0.85 = 750.0 Wh
    # Battery mass (specific energy 200 Wh/kg): 750.0 / 200.0 = 3.75 kg
    
    res = engine.process_mass_design(mock_mass_requirements)
    wb = res.weight_breakdown
    assert abs(wb.battery_fuel_weight_kg - 3.75) < 0.01

def test_battery_bay_clamping(mock_mass_requirements):
    """Verify that the battery position is clamped to physical bay boundaries (0.10m and length-0.20m)."""
    engine = MassPropertiesEngine()
    
    # Case 1: Extremely light battery (should try to balance way forward, clamped to 0.10 m)
    mock_mass_requirements.propulsion_result.power_analysis.required_cruise_power_w = 1.0 # tiny power
    mock_mass_requirements.avionics_result.power_analysis.continuous_power_w = 1.0
    mock_mass_requirements.payload_result.payload_analysis.power_consumption_w = 1.0
    
    res = engine.process_mass_design(mock_mass_requirements)
    battery_comp = [c for c in res.component_masses if c.name == "Energy Battery"][0]
    # The battery is extremely light, so to balance, it is placed at the front limit
    assert battery_comp.x_m >= 0.10
    
    # Case 2: Extremely heavy battery (should try to balance way aft, clamped to length-0.20 m)
    mock_mass_requirements.propulsion_result.power_analysis.required_cruise_power_w = 3000.0 # huge power
    mock_mass_requirements.mission_result.constraints.maximum_takeoff_weight_kg = 100.0
    
    res = engine.process_mass_design(mock_mass_requirements)
    battery_comp = [c for c in res.component_masses if c.name == "Energy Battery"][0]
    f_geom = mock_mass_requirements.fuselage_result.fuselage_geometry
    assert battery_comp.x_m <= f_geom.length_m - 0.20
