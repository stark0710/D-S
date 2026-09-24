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

priorities = [
    OptimizationPriority.BALANCED,
    OptimizationPriority.LOWEST_COST,
    OptimizationPriority.LOWEST_WEIGHT,
    OptimizationPriority.MAXIMUM_ENDURANCE,
    OptimizationPriority.MAXIMUM_RANGE,
    OptimizationPriority.MAXIMUM_PAYLOAD,
    OptimizationPriority.HIGHEST_EFFICIENCY,
]

print("=== STEP 13: HARD CONSTRAINT REJECTION PROOF ===")
# Test 1: Impossible MTOW ceiling (payload 2.0 kg, user MTOW ceiling 1.0 kg)
for p in priorities:
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=2.0,
        maximum_takeoff_weight_kg=1.0,  # Physically impossible: MTOW < payload
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=p
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)
    assert not res.success, f"Failed: Priority {p} accepted impossible MTOW < payload!"
    print(f"Priority {p.value:<20}: Cleanly rejected (status: {res.status})")

# Test 2: Impossible speed/range (range 500 km, flight time 30 min, cruise 50 km/h -> needs 1000 km/h)
for p in priorities:
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=30.0,
        target_range_km=500.0,  # Physically impossible speed-range mismatch
        cruise_speed_kmh=50.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=p
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)
    assert not res.success, f"Failed: Priority {p} accepted impossible range/speed!"
    print(f"Priority {p.value:<20}: Cleanly rejected speed/range (status: {res.status})")

print("\n[SUCCESS] All hard constraints remained 100% hard across all 7 priorities!")
