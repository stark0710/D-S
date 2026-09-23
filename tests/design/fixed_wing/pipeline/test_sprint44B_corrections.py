"""
Regression tests for Sprint 44B-1 corrections of the Fixed-Wing Design Pipeline.
"""

import pytest
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from backend.design.fixed_wing.wing.wing_planform import PlanformGeometryService, PlanformType


def test_mass_conservation_holds():
    """Verify that MTOW is equal to the sum of all weight breakdown fields."""
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=0.8,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)
    assert res.success is True
    
    wb = res.mass_properties_result.weight_breakdown
    expected_mtow = (
        wb.structural_weight_kg +
        wb.propulsion_weight_kg +
        wb.avionics_weight_kg +
        wb.payload_weight_kg +
        wb.battery_fuel_weight_kg
    )
    comp_sum = sum(c.mass_kg for c in res.mass_properties_result.component_masses)
    
    assert abs(wb.useful_load_kg - (wb.payload_weight_kg + wb.battery_fuel_weight_kg)) < 1e-5
    assert abs(comp_sum - expected_mtow) < 1e-4


def test_static_margin_and_battery_placement():
    """Verify static margin lies inside the stable envelope due to balanced battery placement."""
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=0.8,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)
    assert res.success is True
    
    sm = res.mass_properties_result.static_margin
    assert 0.05 <= sm <= 0.40


def test_rectangular_wing_taper_ratio():
    """Verify that a rectangular wing has a taper ratio of 1.0 and equal chords."""
    service = PlanformGeometryService()
    dims = service.calculate_planform_dimensions(
        planform=PlanformType.RECTANGULAR,
        area_m2=0.5,
        aspect_ratio=8.0
    )
    assert dims["taper_ratio"] == 1.0
    assert dims["root_chord_m"] == dims["tip_chord_m"]


def test_performance_missed_results_in_verification_failure():
    """Verify that case 1708 which misses performance requirements fails with VERIFICATION_FAILED."""
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.6,
        target_flight_time_min=46.3,
        target_range_km=58.8,
        cruise_speed_kmh=73.9,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)
    assert res.success is False
    assert res.status == PipelineStatus.VERIFICATION_FAILED
