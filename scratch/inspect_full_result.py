import sys, os, pprint
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

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

print("=== PIPELINE EXECUTION SUMMARY ===")
print(f"Success: {result.success}")
print(f"Status: {result.status}")
print(f"Iterations: {result.iterations}")
print(f"Converged: {result.converged}")
print(f"Convergence history length: {len(result.convergence_history)}")
for i, rec in enumerate(result.convergence_history):
    print(f"  Iter {i+1}: {rec}")

print("\n=== RESULT ATTRIBUTES ===")
for attr in dir(result):
    if not attr.startswith("__"):
        val = getattr(result, attr)
        val_type = type(val).__name__
        print(f"  {attr} ({val_type})")

def dump_obj(name, obj):
    print(f"\n--- {name} ({type(obj).__name__}) ---")
    if obj is None:
        print("  None")
        return
    for k in dir(obj):
        if not k.startswith("_"):
            try:
                v = getattr(obj, k)
                if not callable(v):
                    print(f"  {k}: {repr(v)[:120]}")
            except Exception as e:
                print(f"  {k}: <Error: {e}>")

dump_obj("Mission Result", result.mission_result)
dump_obj("Configuration Result", result.configuration_result)
dump_obj("Wing Result", result.wing_result)
if result.wing_result and hasattr(result.wing_result, "wing_geometry"):
    dump_obj("Wing Geometry", result.wing_result.wing_geometry)
if result.wing_result and hasattr(result.wing_result, "analysis"):
    dump_obj("Wing Analysis", result.wing_result.analysis)

dump_obj("Airfoil Result", result.airfoil_result)
dump_obj("Tail Result", result.tail_result)
if result.tail_result:
    dump_obj("Horizontal Tail", getattr(result.tail_result, "horizontal_tail", None))
    dump_obj("Vertical Tail", getattr(result.tail_result, "vertical_tail", None))
    dump_obj("Control Surfaces", getattr(result.tail_result, "control_surfaces", None))

dump_obj("Fuselage Result", result.fuselage_result)
if result.fuselage_result and hasattr(result.fuselage_result, "fuselage_geometry"):
    dump_obj("Fuselage Geometry", result.fuselage_result.fuselage_geometry)

dump_obj("Payload Result", result.payload_result)
dump_obj("Propulsion Result", result.propulsion_result)
dump_obj("Avionics Result", result.avionics_result)
dump_obj("Mass Properties Result", result.mass_properties_result)
if result.mass_properties_result and hasattr(result.mass_properties_result, "weight_breakdown"):
    dump_obj("Weight Breakdown", result.mass_properties_result.weight_breakdown)
if result.mass_properties_result and hasattr(result.mass_properties_result, "cg_analysis"):
    dump_obj("CG Analysis", result.mass_properties_result.cg_analysis)

dump_obj("Performance Result", result.performance_result)
if result.performance_result and hasattr(result.performance_result, "flight_envelope"):
    dump_obj("Flight Envelope", result.performance_result.flight_envelope)

dump_obj("Verification Result", result.verification_result)
if result.verification_result and hasattr(result.verification_result, "compliance_report"):
    dump_obj("Compliance Report", result.verification_result.compliance_report)
