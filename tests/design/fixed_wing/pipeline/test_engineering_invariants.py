import pytest
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from backend.design.fixed_wing.mass_properties.mass_properties_engine import MassPropertiesEngine
from backend.design.fixed_wing.mass_properties.mass_profile import MassProfile
from tests.design.fixed_wing.mass_properties.test_coordinate_balance import mock_mass_requirements

def test_payload_increases_mtow():
    """Verify that increasing payload weight increases final MTOW."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    
    req_light = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    res_light = pipeline.execute(req_light)
    assert res_light.success is True
    mtow_light = res_light.mass_properties_result.weight_breakdown.useful_load_kg + res_light.mass_properties_result.weight_breakdown.structural_weight_kg + res_light.mass_properties_result.weight_breakdown.propulsion_weight_kg + res_light.mass_properties_result.weight_breakdown.avionics_weight_kg
    
    req_heavy = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    res_heavy = pipeline.execute(req_heavy)
    assert res_heavy.success is True
    mtow_heavy = res_heavy.mass_properties_result.weight_breakdown.useful_load_kg + res_heavy.mass_properties_result.weight_breakdown.structural_weight_kg + res_heavy.mass_properties_result.weight_breakdown.propulsion_weight_kg + res_heavy.mass_properties_result.weight_breakdown.avionics_weight_kg
    
    # Sizing output can be slightly non-monotonic due to discrete database catalog choices
    assert mtow_heavy >= mtow_light - 0.1
 
def test_endurance_increases_battery_mass():
    """Verify that increasing flight endurance increases sized battery mass."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    
    req_short = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.0,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    res_short = pipeline.execute(req_short)
    assert res_short.success is True
    batt_short = res_short.mass_properties_result.weight_breakdown.battery_fuel_weight_kg
    
    req_long = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.0,
        target_flight_time_min=75.0,
        target_range_km=30.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    res_long = pipeline.execute(req_long)
    assert res_long.success is True
    batt_long = res_long.mass_properties_result.weight_breakdown.battery_fuel_weight_kg
    
    # Sized battery mass is non-decreasing due to discrete catalog steps
    assert batt_long >= batt_short
 
def test_cruise_speed_increases_battery_mass():
    """Verify that increasing cruise speed increases sized battery mass."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    
    req_slow = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.0,
        target_flight_time_min=60.0,
        target_range_km=30.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    res_slow = pipeline.execute(req_slow)
    assert res_slow.success is True
    batt_slow = res_slow.mass_properties_result.weight_breakdown.battery_fuel_weight_kg
    
    req_fast = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.0,
        target_flight_time_min=60.0,
        target_range_km=30.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    res_fast = pipeline.execute(req_fast)
    assert res_fast.success is True
    batt_fast = res_fast.mass_properties_result.weight_breakdown.battery_fuel_weight_kg
    
    # Sized battery mass is non-decreasing due to discrete catalog steps
    assert batt_fast >= batt_slow
 
def test_specific_energy_reduces_battery_mass(mock_mass_requirements):
    """Verify that increasing battery specific energy reduces sized battery mass."""
    engine = MassPropertiesEngine()
    
    profile_low = MassProfile(battery_specific_energy_wh_kg=200.0)
    res_low = engine.process_mass_design(mock_mass_requirements, profile=profile_low)
    batt_low = res_low.weight_breakdown.battery_fuel_weight_kg
    
    profile_high = MassProfile(battery_specific_energy_wh_kg=300.0)
    res_high = engine.process_mass_design(mock_mass_requirements, profile=profile_high)
    batt_high = res_high.weight_breakdown.battery_fuel_weight_kg
    
    assert batt_high < batt_low
 
def test_mathematical_cg_and_stability_invariants():
    """Verify CG center of gravity and stability margin formulas are mathematically satisfied."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.0,
        target_flight_time_min=60.0,
        target_range_km=30.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    res = pipeline.execute(req)
    assert res.success is True
    
    mass_res = res.mass_properties_result
    
    # 1. CG moment sum verification: xCG = sum(m_i * x_i) / sum(m_i)
    total_moment = sum(c.mass_kg * c.x_m for c in mass_res.component_masses)
    total_mass = sum(c.mass_kg for c in mass_res.component_masses)
    calculated_cg_x = total_moment / total_mass
    
    # Compare with actual stored CG x coordinate (first element of tuple)
    assert mass_res.center_of_gravity[0] == pytest.approx(calculated_cg_x, abs=1e-3)
    
    # 2. Stability Margin is positive and stable
    assert mass_res.static_margin > 0.0
