import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from scripts.run_fixed_wing_pipeline import to_dict, save_json_artifact, audit_mass_accounting

req = RequirementModel(
    mission_type=MissionType.DELIVERY,
    payload_weight_kg=1.0,
    target_flight_time_min=45.0,
    target_range_km=40.0,
    cruise_speed_kmh=80.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED,
    design_mode=DesignMode.ENGINEERING_ADVISOR,
)

pipeline = FixedWingDesignPipeline()

print("=" * 80)
print("AUDIT JSON SERIALIZATION & EXPORT")
print("=" * 80)

# Run with Pareto enabled
res_pareto = pipeline.execute(req, pareto=True)
mass_audit = audit_mass_accounting(res_pareto)

json_path = save_json_artifact(req, res_pareto, mass_audit, "audit_test")
with open(json_path, "r") as f:
    data = json.load(f)

print(f"JSON File Successfully Loaded: {json_path}")
print(f"Top-level keys: {list(data.keys())}")

# Check final_specification
final_spec = data.get("final_specification", {})
assert final_spec, "final_specification should NOT be empty!"
print(f"final_specification keys: {list(final_spec.keys())}")

# Verify specific sections
sections = [
    "mission_summary",
    "wing_specification",
    "fuselage_specification",
    "payload_specification",
    "tail_specification",
    "propulsion_specification",
    "electrical_specification",
    "mass_properties_specification",
    "cg_specification",
    "performance_specification",
    "convergence_status",
    "iteration_history",
]
for s in sections:
    assert s in final_spec, f"Missing section in final_specification: {s}"
    val = final_spec[s]
    assert val is not None, f"Section {s} is None"
    print(f"  [OK] Section '{s}' populated (type: {type(val).__name__})")

# Check propulsion details in JSON
prop_spec = final_spec.get("propulsion_specification", {})
print("\nPropulsion Details in JSON:")
print(f"  engine_count              : {prop_spec.get('engine_count')}")
print(f"  propulsion_layout         : {prop_spec.get('propulsion_layout')}")
print(f"  static_thrust_n           : {prop_spec.get('static_thrust_n')}")
print(f"  per_motor_static_thrust_n : {prop_spec.get('per_motor_static_thrust_n')}")
print(f"  cruise_power_w            : {prop_spec.get('cruise_power_w')}")
print(f"  per_motor_cruise_power_w  : {prop_spec.get('per_motor_cruise_power_w')}")

# Check Pareto section in JSON
pareto_data = data.get("pareto_front")
assert pareto_data is not None, "pareto_front must be present when pareto=True"
print("\nPareto Section in JSON:")
print(f"  candidate_count           : {pareto_data.get('candidate_count')}")
print(f"  feasible_candidate_count  : {pareto_data.get('feasible_candidate_count')}")
print(f"  front_size                : {pareto_data.get('front_size')}")
print(f"  front candidates count    : {len(pareto_data.get('front', []))}")

# Check Mass Accounting section
mass_sec = data.get("mass_accounting_audit", {})
print("\nMass Accounting Audit in JSON:")
print(f"  summed_mass_kg            : {mass_sec.get('summed_mass_kg')}")
print(f"  reported_mtow_kg          : {mass_sec.get('reported_mtow_kg')}")
print(f"  delta_kg                  : {mass_sec.get('delta_kg')}")
print(f"  is_consistent             : {mass_sec.get('is_consistent')}")
assert mass_sec.get('is_consistent') is True, "Mass accounting should be consistent!"

print("\nJSON AUDIT RESULT: 100% COMPLETE AND VALID")
