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

req_balanced = RequirementModel(
    mission_type=MissionType.SURVEY,
    payload_weight_kg=0.5,
    target_flight_time_min=45.0,
    target_range_km=30.0,
    cruise_speed_kmh=70.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED
)

pipeline = FixedWingDesignPipeline()
res_balanced = pipeline.execute(req_balanced)
print("BALANCED success:", res_balanced.success)
if res_balanced.success:
    spec = res_balanced.final_aircraft_specification
    print(f"BALANCED MTOW: {spec.mass_properties.maximum_takeoff_weight_kg:.4f} kg")
    print(f"BALANCED Motor: {spec.propulsion.motor_name}, Battery: {spec.propulsion.battery_name}")
    print(f"BALANCED Wing Area: {spec.wing.wing_area:.4f} m2, AR: {spec.wing.aspect_ratio:.2f}")
    print(f"BALANCED Cruise Power: {spec.performance.cruise_power_w:.1f} W, Endurance: {spec.performance.estimated_flight_time_min:.1f} min")
