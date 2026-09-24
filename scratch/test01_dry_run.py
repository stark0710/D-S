import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.validation.requirement_validator import RequirementValidator
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus

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

print("--- RequirementValidator Check ---")
val = RequirementValidator()
val_res = val.validate(req)
print(f"Valid: {val_res.is_valid}, Issues: {len(val_res.issues)}")
for issue in val_res.issues:
    print(f"  [{issue.severity}] {issue.code}: {issue.message}")

print("\n--- Running FixedWingDesignPipeline(raise_on_failure=False) ---")
pipeline = FixedWingDesignPipeline(raise_on_failure=False)
result = pipeline.execute(req)

print(f"Pipeline Success: {result.success}")
print(f"Pipeline Status: {result.status}")
print(f"Iterations: {result.iterations}")
print(f"Converged: {result.converged}")
print(f"Warnings: {len(result.warnings)}")
for w in result.warnings:
    print(f"  [WARN] {w}")
print(f"Errors: {len(result.errors)}")
for e in result.errors:
    print(f"  [ERR] {e}")

if result.wing_result:
    print("\n--- Wing Result ---")
    wg = getattr(result.wing_result, "wing_geometry", None) or getattr(result.wing_result, "geometry", None)
    if wg:
        print(f"Span: {wg.span_m:.4f} m, Area: {wg.area_m2:.4f} m2, AR: {wg.aspect_ratio:.4f}")
        print(f"Root chord: {wg.root_chord_m:.4f} m, Tip chord: {wg.tip_chord_m:.4f} m, MAC: {wg.mean_aerodynamic_chord_m:.4f} m")

if result.mass_properties_result:
    print("\n--- Mass Properties Result ---")
    mp = result.mass_properties_result
    print(f"Total mass (MTOW): {mp.total_mass_kg if hasattr(mp, 'total_mass_kg') else getattr(mp, 'maximum_takeoff_weight_kg', 'N/A')}")
    if hasattr(mp, 'weight_breakdown'):
        wb = mp.weight_breakdown
        print(f"Breakdown: struct={wb.structural_weight_kg:.4f}, prop={wb.propulsion_weight_kg:.4f}, av={wb.avionics_weight_kg:.4f}, payload={wb.payload_weight_kg:.4f}, battery={wb.battery_fuel_weight_kg:.4f}")
        print(f"MTOW Sum = {wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.payload_weight_kg + wb.battery_fuel_weight_kg:.4f} kg")
    if hasattr(mp, 'center_of_gravity'):
        print(f"CG position: {mp.center_of_gravity}")
    if hasattr(mp, 'metadata') and 'structural_breakdown' in mp.metadata:
        sb = mp.metadata['structural_breakdown']
        print("\n--- Physical Structural Weight Breakdown ---")
        print(f"Wing: {sb['wing_structural_mass_kg']:.4f} kg")
        print(f"Fuselage: {sb['fuselage_structural_mass_kg']:.4f} kg")
        print(f"Tail: {sb['tail_structural_mass_kg']:.4f} kg")
        print(f"Landing Gear: {sb['landing_gear_mass_kg']:.4f} kg")
        print(f"Controls: {sb['controls_mechanism_mass_kg']:.4f} kg")
        print(f"Fasteners: {sb['fasteners_mass_kg']:.4f} kg")
        print(f"Adhesive: {sb['adhesive_mass_kg']:.4f} kg")
        print(f"Paint: {sb['paint_finish_mass_kg']:.4f} kg")
        print(f"Manufacturing Allowance: {sb['manufacturing_allowance_kg']:.4f} kg")
        print(f"Calculated Material Mass: {sb['calculated_material_mass_kg']:.4f} kg")
        print(f"Estimated Finished Structural Mass: {sb['estimated_finished_structural_mass_kg']:.4f} kg")

if result.propulsion_result:
    print("\n--- Propulsion Result ---")
    prop = result.propulsion_result
    print(f"Motor: {getattr(prop, 'selected_motor', getattr(prop, 'motor_name', 'N/A'))}")
    print(f"Propeller: {getattr(prop, 'selected_propeller', getattr(prop, 'propeller_name', 'N/A'))}")
    print(f"Thrust: {getattr(prop, 'thrust_max_n', getattr(prop, 'max_thrust_n', 'N/A'))}")

if result.performance_result:
    print("\n--- Performance Result ---")
    perf = result.performance_result
    print(f"Cruise speed: {getattr(perf, 'cruise_speed_kmh', 'N/A')}")
    print(f"Stall speed: {getattr(perf, 'stall_speed_kmh', 'N/A')}")
    print(f"Range: {getattr(perf, 'range_km', 'N/A')}")
    print(f"Endurance: {getattr(perf, 'endurance_min', 'N/A')}")

if result.verification_result:
    print("\n--- Verification Result ---")
    ver = result.verification_result
    print(f"Status: {getattr(ver, 'verification_status', 'N/A')}")
    if hasattr(ver, 'compliance_report') and ver.compliance_report:
        print(f"Compliant: {ver.compliance_report.is_fully_compliant}")
