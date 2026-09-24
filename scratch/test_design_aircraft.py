import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

req = RequirementModel(
    mission_type=MissionType.SURVEY,
    aircraft_type=AircraftType.FIXED_WING,
    payload_weight_kg=0.5,
    target_flight_time_min=30.0,
    target_range_km=30.0,
    cruise_speed_kmh=80.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
)

pipeline = FixedWingDesignPipeline(raise_on_failure=False)
try:
    spec = pipeline.design_aircraft(req)
    print("design_aircraft succeeded:", spec)
except Exception as e:
    print("design_aircraft raised:", type(e), e)
