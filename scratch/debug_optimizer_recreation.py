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
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.propulsion.optimization.propulsion_optimizer import PropulsionOptimizer

# import the optimizers
from backend.design.fixed_wing.wing.optimization.wing_planform_optimizer import WingPlanformOptimizer
from backend.design.fixed_wing.fuselage.optimization.fuselage_optimizer import FuselageOptimizer
from backend.design.fixed_wing.payload.optimization.payload_optimizer import PayloadPackagingOptimizer
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer

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
    
    # Override MTOW constraints to 25.0 kg during sizing to allow weight growth
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
    
    # Run the pre-loop pass to set starting points in ctx.subsystem_specifications
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

    # Added propulsion, avionics, payload, mass, performance engines
    from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine
    from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements
    from backend.design.fixed_wing.avionics.avionics_engine import AvionicsEngine
    from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements
    from backend.design.fixed_wing.payload.payload_engine import PayloadEngine
    from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements
    from backend.design.fixed_wing.mass_properties.mass_properties_engine import MassPropertiesEngine
    from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
    from backend.design.fixed_wing.flight_performance.flight_performance_engine import FlightPerformanceEngine
    from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements

    propulsion_engine = PropulsionEngine()
    propulsion_reqs = PropulsionRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
        wing_result=wing_res,
        airfoil_result=airfoil_res,
        tail_result=tail_res,
        fuselage_result=fuselage_res,
    )
    propulsion_res = propulsion_engine.process_propulsion_design(propulsion_reqs)
    ctx.subsystem_specifications["PropulsionSpecification"] = propulsion_res
    ctx.subsystem_specifications["PropulsionOptimizer"] = propulsion_res

    avionics_engine = AvionicsEngine()
    avionics_reqs = AvionicsRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
        wing_result=wing_res,
        airfoil_result=airfoil_res,
        tail_result=tail_res,
        fuselage_result=fuselage_res,
        propulsion_result=propulsion_res,
    )
    avionics_res = avionics_engine.process_avionics_design(avionics_reqs)
    ctx.subsystem_specifications["AvionicsSpecification"] = avionics_res

    payload_engine = PayloadEngine()
    payload_reqs = PayloadRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
        wing_result=wing_res,
        airfoil_result=airfoil_res,
        tail_result=tail_res,
        fuselage_result=fuselage_res,
        propulsion_result=propulsion_res,
        avionics_result=avionics_res,
    )
    payload_res = payload_engine.process_payload_design(payload_reqs)
    ctx.subsystem_specifications["PayloadPackagingSpecification"] = payload_res
    ctx.subsystem_specifications["PayloadPackagingOptimizer"] = payload_res

    mass_engine = MassPropertiesEngine()
    mass_reqs = MassRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
        wing_result=wing_res,
        airfoil_result=airfoil_res,
        tail_result=tail_res,
        fuselage_result=fuselage_res,
        propulsion_result=propulsion_res,
        avionics_result=avionics_res,
        payload_result=payload_res,
    )
    mass_res = mass_engine.process_mass_design(mass_reqs)
    ctx.subsystem_specifications["MassPropertiesSpecification"] = mass_res
    ctx.subsystem_specifications["MassPropertiesOptimizer"] = mass_res

    performance_engine = FlightPerformanceEngine()
    performance_reqs = FlightRequirements(
        mission_result=ctx.mission_result,
        configuration_result=ctx.configuration_result,
        wing_result=wing_res,
        airfoil_result=airfoil_res,
        tail_result=tail_res,
        fuselage_result=fuselage_res,
        propulsion_result=propulsion_res,
        avionics_result=avionics_res,
        payload_result=payload_res,
        mass_result=mass_res,
    )
    performance_res = performance_engine.process_performance_design(performance_reqs)
    ctx.subsystem_specifications["FlightPerformanceSpecification"] = performance_res
    ctx.subsystem_specifications["FlightPerformanceOptimizer"] = performance_res

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
    pipeline_reqs.propulsion_result = propulsion_res
    pipeline_reqs.avionics_result = avionics_res
    pipeline_reqs.payload_result = payload_res
    pipeline_reqs.mass_result = mass_res
    pipeline_reqs.mass_properties_result = mass_res
    pipeline_reqs.flight_performance_result = performance_res
    pipeline_reqs.performance_result = performance_res

    opt_ctx = OptimizationContext(
        requirements=pipeline_reqs,
        previous_specifications=ctx.subsystem_specifications
    )
    
    # NOW run the actual optimizers in order, modifying opt_ctx
    wing_opt = WingPlanformOptimizer()
    fuse_opt = FuselageOptimizer()
    payload_opt = PayloadPackagingOptimizer()
    tail_opt = TailOptimizer()
    
    print("Running WingPlanformOptimizer...")
    wing_res = wing_opt.optimize(opt_ctx)
    opt_ctx.previous_specifications["WingPlanformSpecification"] = wing_res.generated_specification
    opt_ctx.previous_specifications["WingPlanformOptimizer"] = wing_res.generated_specification
    if wing_res.winning_candidate:
        geom_result = wing_res.winning_candidate.derived_variables.get("wing_result")
        if geom_result:
            opt_ctx.requirements.wing_result = geom_result
            
    print("Running FuselageOptimizer...")
    fuse_res = fuse_opt.optimize(opt_ctx)
    opt_ctx.previous_specifications["FuselageSpecification"] = fuse_res.generated_specification
    opt_ctx.previous_specifications["FuselageOptimizer"] = fuse_res.generated_specification
    if fuse_res.winning_candidate:
        geom_result = fuse_res.winning_candidate.derived_variables.get("fuselage_result")
        if geom_result:
            opt_ctx.requirements.fuselage_result = geom_result
            
    print("Running PayloadPackagingOptimizer...")
    payload_res = payload_opt.optimize(opt_ctx)
    opt_ctx.previous_specifications["PayloadPackagingSpecification"] = payload_res.generated_specification
    opt_ctx.previous_specifications["PayloadPackagingOptimizer"] = payload_res.generated_specification
    
    print("Running TailOptimizer...")
    tail_res = tail_opt.optimize(opt_ctx)
    opt_ctx.previous_specifications["TailSpecification"] = tail_res.generated_specification
    opt_ctx.previous_specifications["TailOptimizer"] = tail_res
    
    # Now generate and evaluate propulsion candidates
    optimizer = PropulsionOptimizer()
    candidates = optimizer.generate_candidates(opt_ctx)
    print(f"Generated {len(candidates)} candidates.")
    
    count = 0
    for cand in candidates:
        optimizer.evaluate_candidate(cand, opt_ctx)
        if cand.status == "FAILED" or cand.status == "PENDING":
            m_name = cand.design_variables["motor"]["name"]
            p_name = cand.design_variables["propeller"]["name"]
            err = cand.derived_variables.get("evaluation_error")
            print(f"Cand {m_name} + {p_name} -> Status: {cand.status}, Error: {err}")
            
            # Print constraints checks results
            failed_checks = []
            for constraint in optimizer.constraints._constraints:
                passed, reason = constraint.evaluate(cand, opt_ctx)
                if not passed:
                    failed_checks.append(f"{constraint.name}: {reason}")
            if failed_checks:
                print(f"  Failed constraints: {failed_checks}")
                
            count += 1
            if count >= 5:
                break


if __name__ == "__main__":
    main()
