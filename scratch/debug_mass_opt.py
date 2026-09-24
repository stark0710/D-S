import sys
import traceback
sys.path.insert(0, ".")

from backend.design.fixed_wing.mass_properties.optimization.candidate_evaluator import MassCandidateEvaluator

old_eval = MassCandidateEvaluator.evaluate

def debug_eval(self, candidate, context):
    try:
        return old_eval(self, candidate, context)
    except Exception as e:
        traceback.print_exc()
        raise e

MassCandidateEvaluator.evaluate = debug_eval

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.common.requirements import (
    RequirementModel, MissionType, TakeoffType, LandingType, OperatingEnvironment, OptimizationPriority, DesignMode
)

req = RequirementModel(
    mission_type=MissionType.SURVEY,
    payload_weight_kg=0.5,
    target_flight_time_min=45.0,
    target_range_km=30.0,
    cruise_speed_kmh=70.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED,
    design_mode=DesignMode.ENGINEERING_ADVISOR
)
p = FixedWingDesignPipeline(raise_on_failure=False)
res = p.execute(req)
