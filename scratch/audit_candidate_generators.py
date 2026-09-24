import sys
import os
sys.path.insert(0, os.getcwd())

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.fixed_wing.pipeline.fixed_wing_pipeline import FixedWingDesignPipeline
from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
from backend.design.fixed_wing.pipeline.pipeline_stage import MissionTranslationStage, ConfigurationSelectionStage, ConstructionSelectionStage
from backend.design.common.optimization.optimization_context import OptimizationContext

# Build a mock context
req = RequirementModel(
    mission_type=MissionType.SURVEY,
    payload_weight_kg=0.5,
    target_flight_time_min=45.0,
    target_range_km=30.0,
    cruise_speed_kmh=70.0,
)
pipe_ctx = FixedWingPipelineContext(mission_requirements=req)
MissionTranslationStage().execute(pipe_ctx)
ConfigurationSelectionStage().execute(pipe_ctx)
ConstructionSelectionStage().execute(pipe_ctx)

from backend.design.fixed_wing.pipeline.pipeline_stage import PipelineRequirements
pipeline_reqs = PipelineRequirements(
    raw_requirements=pipe_ctx.mission_requirements,
    mission_result=pipe_ctx.mission_result,
    configuration_result=pipe_ctx.configuration_result
)
opt_ctx = OptimizationContext(
    requirements=pipeline_reqs,
    previous_specifications=pipe_ctx.subsystem_specifications
)

from backend.design.fixed_wing.wing.optimization.wing_planform_optimizer import WingPlanformOptimizer
from backend.design.fixed_wing.fuselage.optimization.fuselage_optimizer import FuselageOptimizer
from backend.design.fixed_wing.payload.optimization.payload_optimizer import PayloadPackagingOptimizer
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer
from backend.design.fixed_wing.propulsion.optimization.propulsion_optimizer import PropulsionOptimizer
from backend.design.fixed_wing.electrical.electrical_optimizer import ElectricalOptimizer
from backend.design.fixed_wing.mass_properties.optimization.mass_optimizer import MassPropertiesOptimizer
from backend.design.fixed_wing.cg.optimization.cg_optimizer import CGOptimizer
from backend.design.fixed_wing.performance.optimization.performance_engine import FlightPerformanceOptimizer

opts = [
    ("WingPlanformOptimizer", WingPlanformOptimizer()),
    ("FuselageOptimizer", FuselageOptimizer()),
    ("PayloadPackagingOptimizer", PayloadPackagingOptimizer()),
    ("TailOptimizer", TailOptimizer()),
    ("PropulsionOptimizer", PropulsionOptimizer()),
    ("ElectricalOptimizer", ElectricalOptimizer()),
    ("MassPropertiesOptimizer", MassPropertiesOptimizer()),
    ("CGOptimizer", CGOptimizer()),
    ("FlightPerformanceOptimizer", FlightPerformanceOptimizer()),
]

print("=== CANDIDATE GENERATION AUDIT ===")
for name, opt in opts:
    try:
        cands = opt.generate_candidates(opt_ctx)
        print(f"\n{name}:")
        print(f"  Generated candidate count: {len(cands)}")
        if cands:
            first = cands[0]
            print(f"  Design variables ({len(first.design_variables)}): {list(first.design_variables.keys())}")
            # Sample variable values
            for k, v in first.design_variables.items():
                all_vals = set(str(c.design_variables.get(k)) for c in cands)
                print(f"    - {k}: {len(all_vals)} distinct values (sample: {list(all_vals)[:4]})")
    except Exception as e:
        print(f"\n{name}: ERROR generating candidates: {e}")
