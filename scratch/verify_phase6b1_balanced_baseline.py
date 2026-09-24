import sys
import os
sys.path.insert(0, os.getcwd())

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

cases = [
    ("SURVEY 0.5kg", MissionType.SURVEY, 0.5, 45.0, 30.0, 70.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL, 4.367),
    ("SURVEY 1.0kg", MissionType.SURVEY, 1.0, 45.0, 30.0, 70.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL, 4.970),
    ("AGRICULTURE 2.0kg", MissionType.AGRICULTURE, 2.0, 45.0, 25.0, 65.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL, 5.802),
    ("SECURITY 0.5kg", MissionType.SECURITY, 0.5, 60.0, 40.0, 70.0, TakeoffType.CATAPULT, LandingType.BELLY_LANDING, OperatingEnvironment.RURAL, 3.921),
    ("INSPECTION 0.5kg", MissionType.INSPECTION, 0.5, 45.0, 25.0, 60.0, TakeoffType.HAND_LAUNCH, LandingType.BELLY_LANDING, OperatingEnvironment.RURAL, 3.921),
    ("MILITARY 1.5kg", MissionType.MILITARY, 1.5, 90.0, 80.0, 85.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL, 7.047),
    ("DELIVERY 1.0kg", MissionType.DELIVERY, 1.0, 30.0, 20.0, 75.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.URBAN, 4.388),
]

print("=== VERIFYING 7 CANONICAL BALANCED CASES AGAINST PHASE 5 BASELINE ===")
for name, mtype, payload, time_min, range_km, speed, takeoff, landing, env, expected_mtow in cases:
    req = RequirementModel(
        mission_type=mtype,
        payload_weight_kg=payload,
        target_flight_time_min=time_min,
        target_range_km=range_km,
        cruise_speed_kmh=speed,
        takeoff_type=takeoff,
        landing_type=landing,
        environment=env,
        optimization_priority=OptimizationPriority.BALANCED
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)
    assert res.success, f"Case {name} failed!"
    mtow = res.final_specification.mass_properties.maximum_takeoff_weight_kg
    span = res.final_specification.wing.wing_span
    ar = res.final_specification.wing.aspect_ratio
    diff = abs(mtow - expected_mtow)
    print(f"{name:<20}: MTOW = {mtow:.4f} kg (Baseline: {expected_mtow:.4f} kg, Delta: {diff:.4f} kg) | Span = {span:.3f} m | AR = {ar:.1f} | PASS")
    assert diff < 0.05, f"Discrepancy in {name}: got {mtow}, expected {expected_mtow}"

print("\n[SUCCESS] All 7 canonical cases match the Phase 5 baseline with 0 regressions!")
