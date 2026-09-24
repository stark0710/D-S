import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.common.verification.verification_engine import VerificationEngine as CommonVerificationEngine
from backend.design.fixed_wing.convergence.models import FinalAircraftSpecification

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
result = pipeline.execute(req)

print("Pipeline status:", result.status)
print("Pipeline success:", result.success)

# Let's inspect verification_result
vr = result.verification_result
print("\n--- FW VerificationResult ---")
print("verification_status:", getattr(vr, "verification_status", None))
print("mission_status:", getattr(vr, "mission_status", None))
print("constraint_violations:", getattr(vr, "constraint_violations", None))

cr = getattr(vr, "compliance_report", None)
if cr:
    print("\n--- ComplianceReport ---")
    print("is_fully_compliant:", cr.is_fully_compliant)
    print("compliance_score_pct:", cr.compliance_score_pct)
    print("failed_categories:", cr.failed_categories)
    print("compliance_details:", cr.compliance_details)

# Let's see what rules CommonVerificationEngine executed
cve = CommonVerificationEngine()
from backend.design.common.verification.rule_registry import global_registry
rules = global_registry.get_rules("Conventional")
print(f"\nRules registered for 'Conventional' ({len(rules)} rules):")
for r in rules:
    print(f"  [{r.category}] {r.rule_id}: {r.name} (sev={r.severity})")

# Let's see rule evaluation results
from backend.design.common.verification.verification_context import VerificationContext
spec = FinalAircraftSpecification(
    mission_summary={},
    wing_specification=result.wing_result,
    fuselage_specification=result.fuselage_result,
    payload_specification=result.payload_result,
    tail_specification=result.tail_result,
    propulsion_specification=result.propulsion_result,
    electrical_specification=None,
    mass_properties_specification=result.mass_properties_result,
    cg_specification=None,
    performance_specification=result.performance_result,
    iteration_history=result.convergence_history,
    convergence_status="Converged" if result.converged else "Failed",
    final_design_score=result.final_design_score
)
rep = cve.verify_aircraft(
    mission_requirements=req,
    final_specification=spec,
    subsystem_specifications={},
    convergence_report={"convergence_status": "Converged", "iterations_performed": result.iterations}
)
print(f"\n--- CommonVerificationEngine Report ---")
print(f"Overall status: {rep.overall_status}")
print(f"Score: {rep.certification_score}")
print(f"Feasible: {rep.feasible}")
print(f"Passed rules ({len(rep.passed_rules)}):")
for r in rep.passed_rules:
    print(f"  [PASS] {r.rule_id}: {r.message}")
print(f"Warnings ({len(rep.warnings)}):")
for r in rep.warnings:
    print(f"  [WARN] {r.rule_id}: {r.message}")
print(f"Failed rules ({len(rep.failed_rules)}):")
for r in rep.failed_rules:
    print(f"  [FAIL] {r.rule_id}: {r.message} (sev={r.severity})")
print(f"Critical failures ({len(rep.critical_failures)}):")
for r in rep.critical_failures:
    print(f"  [CRITICAL] {r.rule_id}: {r.message}")
