from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

req = RequirementModel(
    mission_type=MissionType.MILITARY,
    payload_weight_kg=1.5,
    target_flight_time_min=90.0,
    target_range_km=80.0,
    cruise_speed_kmh=85.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED,
    design_mode=DesignMode.ENGINEERING_ADVISOR,
)

pipeline = FixedWingDesignPipeline()
# Let's inspect why it failed
try:
    res = pipeline.execute(req)
    print("Success:", res.success)
    if not res.success:
        print("Errors:", res.errors)
        print("Warnings:", res.warnings)
except Exception as e:
    import traceback
    traceback.print_exc()
