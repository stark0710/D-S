import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

def main():
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    try:
        res = pipeline.execute(req)
        print("Success! Status:", res.status)
    except Exception as e:
        print("Exception caught:", type(e).__name__, str(e))
        traceback.print_exc()

if __name__ == "__main__":
    main()
