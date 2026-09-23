from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.fixed_wing.propulsion.optimization.propulsion_optimizer import PropulsionOptimizer

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
# Execute until convergence starts or inspect optimizer directly
context = pipeline._create_initial_context(req)
# Run up to propulsion
for stage in pipeline.stages:
    if stage.name == "AircraftConvergenceStage":
        break
    stage.execute(context)

# Now inspect PropulsionOptimizer with context
opt = PropulsionOptimizer()
opt.initialize(context)
cands = opt.generate_candidates(context)
print(f"Total candidates: {len(cands)}")

rejection_reasons = {}
for c in cands:
    opt.evaluator.evaluate(c, context)
    for constraint in opt.constraints:
        passed, reason = constraint(c, context)
        if not passed:
            c.constraints_passed = False
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            break

print("Rejection summary:")
for r, count in sorted(rejection_reasons.items(), key=lambda x: -x[1]):
    print(f"  {count}x: {r}")
