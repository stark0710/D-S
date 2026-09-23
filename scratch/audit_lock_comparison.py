import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
import math

from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

CASES = [
    ("Survey 0.5kg", RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Survey 1.0kg", RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=60.0,
        target_range_km=45.0,
        cruise_speed_kmh=75.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Agriculture 2.0kg", RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=65.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Delivery 1.0kg", RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=1.0,
        target_flight_time_min=40.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Security 0.5kg", RequirementModel(
        mission_type=MissionType.SECURITY,
        payload_weight_kg=0.5,
        target_flight_time_min=60.0,
        target_range_km=40.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Inspection 0.5kg", RequirementModel(
        mission_type=MissionType.INSPECTION,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=25.0,
        cruise_speed_kmh=60.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Military 1.5kg", RequirementModel(
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
    )),
]

def run_audit():
    with open("scratch/phase6b4_representative_results.json", "r") as f:
        baseline_b4 = json.load(f)

    pipeline = FixedWingDesignPipeline()
    current_results = {}

    print("=" * 80)
    print("PHASE 6B FINAL INTEGRATION LOCK AUDIT: BASELINE VERIFICATION")
    print("=" * 80)

    for name, req in CASES:
        res = pipeline.execute(req)
        spec = res.final_specification
        b4_case = baseline_b4.get(name, {})

        mtow = round(spec.mass_properties.maximum_takeoff_weight_kg, 3) if spec else None
        wing_area = round(spec.wing.wing_area, 4) if spec else None
        wingspan = round(spec.wing.wing_span, 4) if spec else None
        ar = getattr(spec.wing, "aspect_ratio", None) if spec else None
        endurance = round(spec.performance.endurance_min, 1) if spec else None
        range_km = round(spec.performance.range_km, 1) if spec else None
        cruise_power = round(spec.propulsion.cruise_power_w, 1) if spec else None
        battery_name = getattr(spec.propulsion, "battery_name", None)
        batt_mass = round(spec.mass_properties.weight_breakdown.get("battery", 0.0), 3) if spec else None
        prop_mass = round(spec.mass_properties.weight_breakdown.get("motor", 0.0) + spec.mass_properties.weight_breakdown.get("propeller", 0.0) + spec.mass_properties.weight_breakdown.get("esc", 0.0), 3) if spec else None
        
        comps = res.mass_properties_result.component_masses if res.mass_properties_result else []
        sum_m = sum(c.mass_kg for c in comps)
        mass_diff = abs(sum_m - (mtow or 0.0))
        
        pa = res.propulsion_result.power_analysis if res.propulsion_result else None
        engine_count = pa.metadata.get("engine_count", 1) if pa else 1
        static_thrust = res.propulsion_result.thrust_analysis.estimated_static_thrust_n if res.propulsion_result else 0.0
        tw = res.propulsion_result.thrust_analysis.thrust_to_weight_ratio if res.propulsion_result else 0.0
        
        current_results[name] = {
            "success": res.success,
            "status": res.status.name,
            "iterations": res.iterations,
            "mtow_kg": mtow,
            "wing_area_m2": wing_area,
            "wingspan_m": wingspan,
            "aspect_ratio": ar,
            "endurance_min": endurance,
            "range_km": range_km,
            "cruise_power_w": cruise_power,
            "battery_name": battery_name,
            "battery_mass_kg": batt_mass,
            "propulsion_mass_kg": prop_mass,
            "engine_count": engine_count,
            "static_thrust_n": static_thrust,
            "tw_ratio": tw,
            "mass_diff": mass_diff,
            "verification_status": res.verification_result.verification_status if res.verification_result else None,
        }

        # Check equivalence for single-engine cases
        is_delivery = (name == "Delivery 1.0kg")
        print(f"\n--- {name} (Engine Count: {engine_count}) ---")
        print(f"Status: {res.status.name}, Iterations: {res.iterations}")
        print(f"MTOW: {mtow} kg (B4 baseline: {b4_case.get('mtow_kg')} kg)")
        print(f"Wing: S={wing_area} m2, b={wingspan} m, AR={ar}")
        print(f"Propulsion: {engine_count}x engine(s), mass={prop_mass} kg, T_static={static_thrust:.2f} N, T/W={tw:.2f}")
        print(f"Electrical: P_cruise={cruise_power} W, Batt={battery_name} ({batt_mass} kg)")
        print(f"Performance: Endurance={endurance} min, Range={range_km} km")
        print(f"Mass Conservation: sum(components)={sum_m:.3f} kg, MTOW={mtow:.3f} kg, delta={mass_diff:.4f} kg")

        if is_delivery:
            print(">> NOTE: Delivery 1.0kg intentionally changed from N=1 inconsistent baseline to N=2 physical twin.")
            assert engine_count == 2, "Delivery should be twin-engine"
            assert prop_mass == 0.910, "Delivery propulsion mass should be 0.910 kg"
            assert math.isclose(static_thrust, 71.10, rel_tol=1e-2), "Delivery static thrust should be 71.10 N"
        else:
            # Must strictly match B4 baseline
            diffs = []
            for k in ["mtow_kg", "wing_area_m2", "wingspan_m", "aspect_ratio", "endurance_min", "cruise_power_w", "iterations"]:
                b4_v = b4_case.get(k)
                curr_v = current_results[name].get(k)
                if b4_v != curr_v:
                    diffs.append(f"{k}: {b4_v} -> {curr_v}")
            if diffs:
                print(f">> DRIFT DETECTED: {', '.join(diffs)}")
            else:
                print(">> EXACT MATCH: 100% numerical identity with locked Phase 6B-4 baseline.")

    with open("scratch/audit_lock_comparison_results.json", "w") as f:
        json.dump(current_results, f, indent=2)

if __name__ == "__main__":
    run_audit()
