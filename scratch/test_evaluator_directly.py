import sys
import os
import traceback
import copy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.propulsion.optimization.candidate_evaluator import CandidateEvaluator

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
    
    pipeline = FixedWingDesignPipeline()
    from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
    from backend.design.fixed_wing.pipeline.pipeline_stage import MissionTranslationStage, ConfigurationSelectionStage
    
    ctx = FixedWingPipelineContext(mission_requirements=req)
    MissionTranslationStage().execute(ctx)
    ConfigurationSelectionStage().execute(ctx)
    
    # Override MTOW constraints to 25.0 kg
    if ctx.mission_result.constraints:
        ctx.mission_result.constraints.maximum_takeoff_weight_kg = 25.0
    if ctx.mission_result.mission_profile:
        ctx.mission_result.mission_profile.maximum_takeoff_weight_limit_kg = 25.0
        
    from backend.design.fixed_wing.mass_properties.mass_registry import MassStrategyRegistry
    category = ctx.mission_result.mission_profile.mission_category
    strategy_name = category.value if hasattr(category, 'value') else str(category)
    orig_mass_strategy = MassStrategyRegistry._registry.get(strategy_name.lower())
    
    class DynamicOverrideMassStrategy(orig_mass_strategy):
        def get_target_static_margin(self):
            return 0.01, 0.40

    MassStrategyRegistry.register(strategy_name, DynamicOverrideMassStrategy)

    from backend.design.fixed_wing.wing.wing_engine import WingEngine
    from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
    from backend.design.fixed_wing.airfoil.airfoil_engine import AirfoilEngine
    from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements
    from backend.design.fixed_wing.tail.tail_engine import TailEngine
    from backend.design.fixed_wing.tail.tail_requirements import TailRequirements
    from backend.design.fixed_wing.fuselage.fuselage_engine import FuselageEngine
    from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements

    wing_engine = WingEngine()
    wing_reqs = WingRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
    )
    wing_res = wing_engine.process_wing_design(wing_reqs)
    ctx.subsystem_specifications["WingPlanformSpecification"] = wing_res
    ctx.subsystem_specifications["WingPlanformOptimizer"] = wing_res

    airfoil_engine = AirfoilEngine()
    airfoil_reqs = AirfoilRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
        wing_result=wing_res,
    )
    airfoil_res = airfoil_engine.process_airfoil_design(airfoil_reqs)
    ctx.subsystem_specifications["AirfoilSpecification"] = airfoil_res

    tail_engine = TailEngine()
    tail_reqs = TailRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
        wing_result=wing_res,
        airfoil_result=airfoil_res,
    )
    tail_res = tail_engine.process_tail_design(tail_reqs)
    ctx.subsystem_specifications["TailSpecification"] = tail_res
    ctx.subsystem_specifications["TailOptimizer"] = tail_res

    fuselage_engine = FuselageEngine()
    fuselage_reqs = FuselageRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
        wing_result=wing_res,
        airfoil_result=airfoil_res,
        tail_result=tail_res,
    )
    fuselage_res = fuselage_engine.process_fuselage_design(fuselage_reqs)
    ctx.subsystem_specifications["FuselageSpecification"] = fuselage_res
    ctx.subsystem_specifications["FuselageOptimizer"] = fuselage_res

    from backend.design.fixed_wing.pipeline.pipeline_stage import PipelineRequirements
    pipeline_reqs = PipelineRequirements(
        raw_requirements=ctx.mission_requirements,
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result
    )
    pipeline_reqs.wing_result = wing_res
    pipeline_reqs.airfoil_result = airfoil_res
    pipeline_reqs.tail_result = tail_res
    pipeline_reqs.fuselage_result = fuselage_res

    opt_ctx = OptimizationContext(
        requirements=pipeline_reqs,
        previous_specifications=ctx.subsystem_specifications
    )
    
    # We will run the wing, fuselage, payload, tail optimizers to set the optimized spec values
    from backend.design.fixed_wing.wing.optimization.wing_planform_optimizer import WingPlanformOptimizer
    from backend.design.fixed_wing.fuselage.optimization.fuselage_optimizer import FuselageOptimizer
    from backend.design.fixed_wing.payload.optimization.payload_optimizer import PayloadPackagingOptimizer
    from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer

    wing_opt = WingPlanformOptimizer()
    fuse_opt = FuselageOptimizer()
    payload_opt = PayloadPackagingOptimizer()
    tail_opt = TailOptimizer()

    wing_res = wing_opt.optimize(opt_ctx)
    opt_ctx.previous_specifications["WingPlanformSpecification"] = wing_res.generated_specification
    opt_ctx.previous_specifications["WingPlanformOptimizer"] = wing_res.generated_specification
    if wing_res.winning_candidate:
        geom_result = wing_res.winning_candidate.derived_variables.get("wing_result")
        if geom_result:
            opt_ctx.requirements.wing_result = geom_result

    fuse_res = fuse_opt.optimize(opt_ctx)
    opt_ctx.previous_specifications["FuselageSpecification"] = fuse_res.generated_specification
    opt_ctx.previous_specifications["FuselageOptimizer"] = fuse_res.generated_specification
    if fuse_res.winning_candidate:
        geom_result = fuse_res.winning_candidate.derived_variables.get("fuselage_result")
        if geom_result:
            opt_ctx.requirements.fuselage_result = geom_result

    payload_res = payload_opt.optimize(opt_ctx)
    opt_ctx.previous_specifications["PayloadPackagingSpecification"] = payload_res.generated_specification
    opt_ctx.previous_specifications["PayloadPackagingOptimizer"] = payload_res.generated_specification

    tail_res = tail_opt.optimize(opt_ctx)
    opt_ctx.previous_specifications["TailSpecification"] = tail_res.generated_specification
    opt_ctx.previous_specifications["TailOptimizer"] = tail_res

    # Select candidate
    motor = {"name": "SunnySky X2216", "kv": 1100.0, "weight_g": 72.0, "max_power_w": 380.0, "nominal_voltage_v": 11.1, "max_current_a": 35.0, "cell_count_s": 3}
    propeller = {"name": "9x6 APC", "diameter_in": 9.0, "pitch_in": 6.0, "diameter_m": 9.0 * 0.0254, "pitch_m": 6.0 * 0.0254}
    esc = {"name": "35A BLHeli_32", "continuous_current_a": 35.0, "max_supported_cells_s": 6, "weight_g": 18.0}
    battery = {
        "name": "LiHV 3S 3300mAh 40C Pack",
        "chemistry": "LiHV",
        "cell_count_s": 3,
        "nominal_voltage_v": 11.4,
        "capacity_mah": 3300.0,
        "discharge_rating_c": 40.0,
        "total_energy_wh": 37.6,
        "weight_g": 203.4,
        "max_discharge_current_a": 132.0,
    }
    
    cand = OptimizationCandidate(design_variables={
        "motor": motor, "propeller": propeller, "esc": esc, "battery": battery
    })
    
    # Call the real PropulsionEngine process_propulsion_design
    from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine
    engine = PropulsionEngine()
    
    print("Running process_propulsion_design...")
    try:
        res = engine.process_propulsion_design(opt_ctx.requirements)
        print("Success! Sized component:", res.selected_motor_or_engine)
        print("Sized propeller:", res.selected_propeller)
    except Exception as e:
        print("Caught exception:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
