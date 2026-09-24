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

# Let's inspect flight times of candidates in iteration 1
pipeline = FixedWingDesignPipeline()
context = None
# Run stages until convergence
for stage in pipeline.stages:
    if stage.name == "AircraftConvergenceStage":
        # Let's see what happens inside iteration 1
        mgr = stage.convergence_manager
        print("Initial MTOW seed:", context.current_mtow)
        ctrl = mgr.controller
        # run wing, fuse, payload, tail
        ctrl.wing_opt.optimize(context)
        ctrl.fuse_opt.optimize(context)
        ctrl.pay_opt.optimize(context)
        ctrl.tail_opt.optimize(context)
        # generate candidates
        cands = ctrl.prop_opt.generate_candidates(context)
        ctrl.prop_opt.initialize(context)
        print("Generated cands:", len(cands))
        max_ft = 0.0
        best_cand = None
        for c in cands:
            ctrl.prop_opt.evaluator.evaluate(c, context)
            ft = c.derived_variables.get("estimated_flight_time_min", 0.0)
            if ft > max_ft:
                max_ft = ft
                best_cand = c
        print(f"Max flight time in cands: {max_ft:.1f} min")
        if best_cand:
            print(f"Best cand battery: {best_cand.design_variables['battery']['name']}")
            print(f"Cruise power: {best_cand.derived_variables.get('cruise_power_w')} W")
            print(f"Cruise current: {best_cand.derived_variables.get('cruise_current_a')} A")
        break
    else:
        context = stage.execute(context) if context else stage.execute(pipeline._create_initial_context(req) if hasattr(pipeline, '_create_initial_context') else None)
