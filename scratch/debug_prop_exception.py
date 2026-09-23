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
from backend.design.fixed_wing.propulsion.optimization.candidate_evaluator import CandidateEvaluator, CustomMotorSelector, CustomPropellerSelector
from backend.design.fixed_wing.propulsion.motor_selector import MotorRecord
from backend.design.fixed_wing.propulsion.propeller_selector import PropellerRecord
from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine
import copy

def main():
    # Setup requirements
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
    
    # Run first few stages of the pipeline to get the context populated
    pipeline = FixedWingDesignPipeline()
    context = pipeline.logger = None
    from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
    from backend.design.fixed_wing.pipeline.pipeline_stage import MissionTranslationStage, ConfigurationSelectionStage
    
    ctx = FixedWingPipelineContext(mission_requirements=req)
    MissionTranslationStage().execute(ctx)
    ConfigurationSelectionStage().execute(ctx)
    
    # Now run pre-loop sizing to populate wing, fuselage, etc. specs
    from backend.design.fixed_wing.pipeline.pipeline_stage import AircraftConvergenceStage
    stage = AircraftConvergenceStage()
    
    # Run pre-loop sizing part of stage
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

    # Build optimizer context
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
    
    # Generate all candidates using PropulsionCandidateGenerator
    from backend.design.fixed_wing.propulsion.optimization.candidate_generator import GridSearchPropulsionCandidateGenerator
    generator = GridSearchPropulsionCandidateGenerator()
    candidates = generator.generate_candidates(opt_ctx)
    print(f"Generated {len(candidates)} candidates.")
    
    error_counts = {}
    
    for idx, cand in enumerate(candidates):
        dv = cand.design_variables
        motor = dv["motor"]
        propeller = dv["propeller"]
        esc = dv["esc"]
        battery = dv["battery"]
        
        # Setup engine
        motor_rec = MotorRecord(
            name=motor["name"],
            kv=motor["kv"],
            weight_g=motor["weight_g"],
            max_power_w=motor["max_power_w"],
            nominal_voltage_v=motor["nominal_voltage_v"]
        )
        prop_rec = PropellerRecord(
            diameter_in=propeller["diameter_in"],
            pitch_in=propeller["pitch_in"]
        )
        engine = PropulsionEngine(
            motor_selector=CustomMotorSelector(motor_rec),
            prop_selector=CustomPropellerSelector(prop_rec)
        )
        
        # Sizing requirements
        reqs = copy.deepcopy(pipeline_reqs)
        # Update battery capacity / cell count on the requirements so sizers see the candidate's battery choice
        # Wait, how does PropulsionEngine get battery/cell info? It gets it from requirements or candidate?
        # Actually, let's just evaluate:
        try:
            result = engine.process_propulsion_design(reqs)
            print(f"Candidate {idx} SUCCEEDED! Motor: {motor['name']}, Prop: {propeller['name']}, Battery: {battery['name']}")
        except Exception as e:
            err_msg = str(e)
            error_counts[err_msg] = error_counts.get(err_msg, 0) + 1
            if len(error_counts) <= 10 and error_counts[err_msg] == 1:
                print(f"Sample error for {motor['name']} + {propeller['name']}: {err_msg}")
                
    print("\nError Summary:")
    for err, count in error_counts.items():
        print(f" - {count} times: {err}")

if __name__ == "__main__":
    main()
