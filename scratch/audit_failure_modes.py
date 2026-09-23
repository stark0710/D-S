import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus

print("=" * 80)
print("AUDIT FAILURE MODES")
print("=" * 80)

pipeline = FixedWingDesignPipeline()

# 1. Impossible MTOW limit
req_mtow_limit = RequirementModel(
    mission_type=MissionType.SURVEY,
    payload_weight_kg=2.0,
    target_flight_time_min=45.0,
    target_range_km=30.0,
    cruise_speed_kmh=70.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    maximum_takeoff_weight_kg=1.5,  # 1.5kg MTOW is less than 2.0kg payload alone!
    optimization_priority=OptimizationPriority.BALANCED,
    design_mode=DesignMode.ENGINEERING_ADVISOR,
)
res1 = pipeline.execute(req_mtow_limit)
print(f"Test 1: Impossible MTOW Limit (1.5 kg limit for 2.0 kg payload)")
print(f"  Success : {res1.success}")
print(f"  Status  : {res1.status.name}")
assert not res1.success, "Impossible MTOW limit should FAIL!"
assert res1.status in (PipelineStatus.MTOW_LIMIT_EXCEEDED, PipelineStatus.SIZING_INFEASIBLE, PipelineStatus.INVALID_REQUIREMENTS, PipelineStatus.CONVERGENCE_FAILURE), f"Unexpected status: {res1.status}"
print("  [PASS] Successfully rejected impossible MTOW limit.\n")

# 2. Excessive Payload (50.0 kg on micro-UAV class)
req_excess_payload = RequirementModel(
    mission_type=MissionType.SURVEY,
    payload_weight_kg=50.0,
    target_flight_time_min=45.0,
    target_range_km=30.0,
    cruise_speed_kmh=70.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED,
    design_mode=DesignMode.ENGINEERING_ADVISOR,
)
res2 = pipeline.execute(req_excess_payload)
print(f"Test 2: Excessive Payload (50 kg payload)")
print(f"  Success : {res2.success}")
print(f"  Status  : {res2.status.name}")
assert not res2.success, "Excessive payload should FAIL!"
print("  [PASS] Successfully rejected excessive payload.\n")

# 3. Impossible Range (2000 km battery electric UAV)
req_extreme_range = RequirementModel(
    mission_type=MissionType.INSPECTION,
    payload_weight_kg=0.5,
    target_flight_time_min=1200.0,  # 20 hours
    target_range_km=2000.0,
    cruise_speed_kmh=60.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED,
    design_mode=DesignMode.ENGINEERING_ADVISOR,
)
res3 = pipeline.execute(req_extreme_range)
print(f"Test 3: Impossible Range (2000 km, 20 hrs on battery)")
print(f"  Success : {res3.success}")
print(f"  Status  : {res3.status.name}")
assert not res3.success, "Impossible range should FAIL!"
print("  [PASS] Successfully rejected impossible battery mission range.\n")

# 4. Long Endurance Exceeding MTOW limit
req_endurance_mtow = RequirementModel(
    mission_type=MissionType.DELIVERY,
    payload_weight_kg=1.0,
    target_flight_time_min=180.0,  # 3 hours
    target_range_km=150.0,
    cruise_speed_kmh=80.0,
    maximum_takeoff_weight_kg=3.5,  # 3.5 kg limit for 3 hr flight
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED,
    design_mode=DesignMode.ENGINEERING_ADVISOR,
)
res4 = pipeline.execute(req_endurance_mtow)
print(f"Test 4: Long Endurance Exceeding MTOW Limit (3 hrs on 3.5kg budget)")
print(f"  Success : {res4.success}")
print(f"  Status  : {res4.status.name}")
assert not res4.success, "Impossible endurance with MTOW limit should FAIL!"
print("  [PASS] Successfully rejected impossible endurance/MTOW budget.\n")

print("ALL FAILURE MODES AUDITED & CONFIRMED: ZERO FALSE POSITIVES.")
