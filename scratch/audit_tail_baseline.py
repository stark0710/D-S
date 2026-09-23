import math
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer
from backend.design.fixed_wing.tail.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.tail.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.tail.optimization.constraints import build_tail_constraints
from backend.design.fixed_wing.tail.optimization.objective_function import TailObjectiveFunction
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

def audit_tail_objective_terms():
    # Run Survey 0.5kg pipeline to get a realistic context at tail optimization stage
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
    # Execute pipeline to examine baseline
    res = pipeline.execute(req)
    print("Baseline Survey 0.5kg success:", res.success)
    spec = res.final_specification
    print(f"Tail spec: {spec.tail.tail_configuration}, V_h={spec.tail.horizontal_volume_coefficient}, V_v={spec.tail.vertical_volume_coefficient}, S_h={spec.tail.horizontal_tail_area_m2}, S_v={spec.tail.vertical_tail_area_m2}, arm={spec.tail.tail_arm_m}")

if __name__ == "__main__":
    audit_tail_objective_terms()
