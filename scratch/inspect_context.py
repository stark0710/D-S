import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
from backend.design.fixed_wing.pipeline.fixed_wing_pipeline import FixedWingDesignPipeline

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
context = FixedWingPipelineContext(mission_requirements=req)
context.pipeline = pipeline

from backend.design.fixed_wing.pipeline.pipeline_stage import (
    MissionTranslationStage,
    ConfigurationSelectionStage,
    WingPlanformOptimizationStage,
    FuselageOptimizationStage,
    PayloadPackagingStage,
    TailOptimizationStage,
    PropulsionOptimizationStage,
    ElectricalSystemIntegrationStage,
    MassPropertiesStage,
    CGOptimizerStage,
    FlightPerformanceStage,
    AircraftConvergenceStage,
    VerificationCertificationStage,
)
from backend.design.fixed_wing.pipeline.pipeline_executor import PipelineExecutor

stages = [
    MissionTranslationStage(),
    ConfigurationSelectionStage(),
    WingPlanformOptimizationStage(),
    FuselageOptimizationStage(),
    PayloadPackagingStage(),
    TailOptimizationStage(),
    PropulsionOptimizationStage(),
    ElectricalSystemIntegrationStage(),
    MassPropertiesStage(),
    CGOptimizerStage(),
    FlightPerformanceStage(),
    AircraftConvergenceStage(pipeline.max_iterations),
    VerificationCertificationStage(),
]

executor = PipelineExecutor(stages=stages, logger=pipeline.logger)
executor.execute(context)

print("\n=== SUBSYSTEM SPECIFICATIONS IN CONTEXT ===")
for k, v in context.subsystem_specifications.items():
    print(f"\n--- Subsystem: {k} ({type(v).__name__}) ---")
    if v is not None:
        for attr in dir(v):
            if not attr.startswith("_"):
                try:
                    val = getattr(v, attr)
                    if not callable(val):
                        print(f"  {attr}: {repr(val)[:120]}")
                except Exception as ex:
                    print(f"  {attr}: <err {ex}>")

print("\n=== CERTIFICATION REPORT IN CONTEXT ===")
cr = context.certification_report
if cr:
    print(f"Overall status: {cr.overall_status}")
    print(f"Certification score: {cr.certification_score}")
    print(f"Passed rules ({len(cr.passed_rules)}):")
    for r in cr.passed_rules:
        print(f"  [PASS] {r.rule_id}: {r.title} - {r.message}")
    print(f"Warnings ({len(cr.warnings)}):")
    for r in cr.warnings:
        print(f"  [WARN] {r.rule_id}: {r.title} - {r.message}")
    print(f"Failed rules ({len(cr.failed_rules)}):")
    for r in cr.failed_rules:
        print(f"  [FAIL] {r.rule_id}: {r.title} - {r.message} (sev={r.severity})")
    print(f"Critical failures ({len(cr.critical_failures)}):")
    for r in cr.critical_failures:
        print(f"  [CRITICAL] {r.rule_id}: {r.title} - {r.message}")

print("\n=== CONVERGENCE DIAGNOSTICS ===")
cd = context.execution_metadata.get("convergence_diagnostics", {})
print("Iterations count:", len(cd.get("iteration_history", [])))
for i, h in enumerate(cd.get("iteration_history", [])):
    print(f"  Iter {i+1}: MTOW={h.get('mtow')}, WingArea={h.get('wing_area')}, BatteryMass={h.get('battery_mass')}, CruisePower={h.get('cruise_power')}")
