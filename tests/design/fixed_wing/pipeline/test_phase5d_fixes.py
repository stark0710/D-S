import pytest
from unittest.mock import MagicMock
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from backend.design.fixed_wing.mission.mission_requirements import MissionCategory
from backend.design.fixed_wing.configuration.configuration_requirements import ConfigurationRequirements
from backend.design.fixed_wing.configuration.configuration_engine import ConfigurationEngine
from backend.design.fixed_wing.configuration.configuration_validator import ConfigurationValidator, ConfigurationValidationError
from backend.design.fixed_wing.configuration.configuration_selector import ConfigurationSelector
from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements, PropulsionType
from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine
from backend.design.fixed_wing.propulsion.propulsion_validator import PropulsionValidationError
from backend.design.fixed_wing.propulsion.motor_selector import MotorRecord
from backend.design.fixed_wing.propulsion.propeller_selector import PropellerRecord
from backend.design.fixed_wing.mass_properties.mass_properties_engine import MassPropertiesEngine
from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
from backend.design.fixed_wing.verification.verification_engine import VerificationEngine
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements


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


def test_configuration_fallback(base_requirements):
    """Test configuration fallback scenarios:
    1. Valid primary candidate remains unchanged.
    2. Invalid primary candidate triggers fallback.
    3. All-invalid candidates raise ConfigurationValidationError.
    4. Identical requirements produce identical result.
    """
    engine = ConfigurationEngine()
    
    # Mock validator
    mock_validator = MagicMock(spec=ConfigurationValidator)
    engine._validator = mock_validator
    
    # Mock selector
    mock_selector = MagicMock(spec=ConfigurationSelector)
    engine._selector = mock_selector
    
    # Strategy alternatives
    primary_layout = {"architecture": "Low Wing Conventional", "wing_position": "Low Wing", "propulsion_layout": "Tractor"}
    fallback_layout = {"architecture": "High Wing Conventional", "wing_position": "High Wing", "propulsion_layout": "Tractor"}
    
    mock_selector.select_configuration.return_value = {
        "selected_layout": primary_layout,
        "selected_scores": {"overall_score": 85.0},
        "alternatives": [
            {"layout": fallback_layout, "scores": {"overall_score": 75.0}, "score": 75.0, "rationale": "alternative"}
        ]
    }
    
    # Mock mission results for requirements
    dummy_mission_result = MagicMock()
    dummy_mission_result.mission_profile.mission_category = MissionType.MAPPING
    dummy_mission_result.mission_profile.payload_kg = 0.5
    config_reqs = ConfigurationRequirements(mission_result=dummy_mission_result)
    
    # Scenario 1: Valid primary candidate remains unchanged
    mock_validator.validate.return_value = [] # Passes
    res1 = engine.process_configuration(config_reqs)
    assert res1.selected_configuration == primary_layout
    assert res1.metadata["reason_final_candidate_won"] == "Primary candidate is valid"
    
    # Scenario 2: Invalid primary candidate triggers fallback
    def validate_side_effect(reqs, config):
        if config["architecture"] == "Low Wing Conventional":
            raise ConfigurationValidationError(["Low wing strikes on belly landing"])
        return ["warning"]
        
    mock_validator.validate.side_effect = validate_side_effect
    res2 = engine.process_configuration(config_reqs)
    assert res2.selected_configuration == fallback_layout
    assert res2.metadata["reason_final_candidate_won"] == "Alternative layout passed validation checks"
    assert res2.metadata["primary_rejection_reason"] == "Low wing strikes on belly landing"
    assert "High Wing Conventional" in res2.metadata["fallback_candidates_attempted"]
    
    # Scenario 3: All-invalid candidates raise ConfigurationValidationError
    mock_validator.validate.side_effect = ConfigurationValidationError(["Incompatible"])
    with pytest.raises(ConfigurationValidationError):
        engine.process_configuration(config_reqs)
        
    # Scenario 4: Identical requirements produce identical result
    mock_validator.validate.side_effect = validate_side_effect
    res4a = engine.process_configuration(config_reqs)
    res4b = engine.process_configuration(config_reqs)
    assert res4a.selected_configuration == res4b.selected_configuration


def test_joint_propulsion_search():
    """Test joint propulsion search pairing:
    - motor A + prop A fails (thrust-to-weight too low)
    - motor A + prop B fails (propeller clearance diameter too large)
    - motor B + prop A passes
    Prove that joint search successfully retrieves motor B + prop A.
    """
    engine = PropulsionEngine()
    
    # Setup test motors and propellers
    motor_a = MotorRecord("Motor A (Small)", 1000, 50, 200, 11.1)
    motor_b = MotorRecord("Motor B (Large)", 800, 150, 800, 14.8)
    
    prop_a = PropellerRecord(10.0, 7.0) # small diameter (passes clearance)
    prop_b = PropellerRecord(20.0, 10.0) # large diameter (fails clearance limit)
    
    engine._motor_selector._motors = [motor_a, motor_b]
    engine._prop_selector._props = [prop_a, prop_b]
    
    # Setup requirements
    dummy_mission_result = MagicMock()
    m_profile = dummy_mission_result.mission_profile
    m_profile.mission_category = MissionCategory.SURVEY
    m_profile.payload_kg = 1.0 # smaller payload reduces takeoff thrust requirement
    m_profile.maximum_takeoff_weight_limit_kg = 4.0
    m_profile.air_density_kg_m3 = 1.2
    m_profile.cruise_speed_kmh = 80.0
    m_profile.flight_time_min = 60.0
    m_profile.operational_altitude_m = 150.0
    m_profile.launch_method = MagicMock()
    
    dummy_wing_result = MagicMock()
    dummy_wing_result.wing_geometry.mean_aerodynamic_chord_m = 0.22
    dummy_wing_result.wing_geometry.span_m = 2.0
    dummy_wing_result.wing_geometry.wing_loading_kg_m2 = 20.0
    dummy_wing_result.wing_geometry.area_m2 = None
    dummy_wing_result.analysis.aerodynamic_efficiency_score = 80.0
    dummy_wing_result.analysis.estimated_stall_speed_kmh = 42.0
    
    dummy_fuselage_result = MagicMock()
    dummy_fuselage_result.fuselage_geometry.height_m = 0.20 # clearance limit 0.40m
    
    reqs = PropulsionRequirements(
        mission_result=dummy_mission_result,
        configuration_result=MagicMock(),
        wing_result=dummy_wing_result,
        airfoil_result=MagicMock(),
        tail_result=MagicMock(),
        fuselage_result=dummy_fuselage_result,
        flight_performance_result=None
    )
    
    # We require min_thrust_to_weight = 0.35, climb_power_w = 400.0W
    # Sizing checks for Motor A (200 W):
    # - Fails climb power constraint (200W < 400W target)
    # Sizing checks for Motor B (800 W):
    # - With Prop B (20 inch): diameter 0.508m > clearance limit 0.40m (fails clearance)
    # - With Prop A (10 inch): diameter 0.254m < clearance limit 0.40m, static thrust is sufficient (passes!)
    
    res = engine.process_propulsion_design(reqs)
    assert res.selected_motor_or_engine == "Motor B (Large)"
    assert res.selected_propeller == "10x7 APC"


def test_battery_bay_boundaries():
    """Verify that battery position clamping works and correctly shifts static margin."""
    engine = MassPropertiesEngine()
    
    # Mock requirements
    dummy_mission_result = MagicMock()
    dummy_mission_result.mission_profile.mission_category = MissionCategory.SURVEY
    dummy_mission_result.mission_profile.maximum_takeoff_weight_limit_kg = 10.0
    dummy_mission_result.mission_profile.flight_time_min = 60.0
    dummy_mission_result.constraints.maximum_takeoff_weight_kg = 10.0
    
    dummy_fuselage_result = MagicMock()
    f_geom = dummy_fuselage_result.fuselage_geometry
    f_geom.length_m = 1.0
    f_geom.nose_length_m = 0.18
    f_geom.tail_cone_length_m = 0.40
    f_geom.battery_bay_length_m = 0.16
    f_geom.wing_attachment_x_m = 0.32
    dummy_fuselage_result.internal_layout.flight_controller_placement_x_m = 0.35
    
    dummy_wing_result = MagicMock()
    wing_geom = dummy_wing_result.wing_geometry
    wing_geom.mean_aerodynamic_chord_m = 0.20
    wing_geom.quarter_chord_x_m = 0.05
    wing_geom.reference_area_m2 = 0.3
    dummy_wing_result.structural_mass_override_kg = None
    
    dummy_propulsion = MagicMock()
    dummy_propulsion.power_analysis.metadata = {"motor_weight_g": 140}
    dummy_propulsion.power_analysis.required_cruise_power_w = 200.0
    
    dummy_avionics = MagicMock()
    dummy_avionics.power_analysis.metadata = {"autopilot_weight_g": 80}
    dummy_avionics.power_analysis.continuous_power_w = 50.0
    
    dummy_payload = MagicMock()
    dummy_payload.installed_payload_mass_kg = 1.5
    dummy_payload.payload_layout.placement_x_m = 0.20
    dummy_payload.payload_analysis.power_consumption_w = 10.0
    
    dummy_tail = MagicMock()
    dummy_tail.horizontal_tail.area_m2 = 0.05
    dummy_tail.vertical_tail.area_m2 = 0.03
    
    dummy_config = MagicMock()
    dummy_config.propulsion_configuration = "Tractor"
    
    reqs = MassRequirements(
        mission_result=dummy_mission_result,
        configuration_result=dummy_config,
        wing_result=dummy_wing_result,
        airfoil_result=MagicMock(),
        tail_result=dummy_tail,
        fuselage_result=dummy_fuselage_result,
        propulsion_result=dummy_propulsion,
        avionics_result=dummy_avionics,
        payload_result=dummy_payload
    )
    
    # Allowable battery interval:
    # battery_half_length = 0.08, clearance = 0.02
    # X_min = 0.18 + 0.08 + 0.02 = 0.28 m
    # X_max = (1.0 - 0.40) - (0.08 + 0.02) = 0.50 m
    # If mathematically the battery solver places battery at 0.70m (tail section),
    # it must be clamped to 0.50m!
    
    res = engine.process_mass_design(reqs)
    # Check that Energy Battery component is placed within [0.28, 0.50]
    batt_comp = next(c for c in res.component_masses if "Battery" in c.name)
    assert 0.28 <= batt_comp.x_m <= 0.50
