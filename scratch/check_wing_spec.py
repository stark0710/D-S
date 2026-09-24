from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

req = RequirementModel(
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
res = pipeline.execute(req)
spec = res.final_specification
print("type of spec.wing:", type(spec.wing))
print("dir of spec.wing:", dir(spec.wing))
for k in dir(spec.wing):
    if not k.startswith("_"):
        print(f"  {k}: {getattr(spec.wing, k)}")
