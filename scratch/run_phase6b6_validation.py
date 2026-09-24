"""
Phase 6B-6 Forensic Validation and Representative Case Analysis Script.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

import json
import time
import dataclasses
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.fixed_wing.optimization.pareto import (
    self_check_pareto_front,
    ParetoFrontResult,
)

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


def run_validation():
    # Load Phase 6B-4 baseline
    with open("scratch/phase6b4_representative_results.json", "r") as f:
        b4_baseline = json.load(f)

    pipeline = FixedWingDesignPipeline()
    output = {
        "baseline_comparison": {},
        "pareto_results": {},
        "runtime_metrics": {},
    }

    print("=" * 80)
    print("PHASE 6B-6 FORENSIC VALIDATION: 7 REPRESENTATIVE AIRCRAFT CASES")
    print("=" * 80)

    for case_name, req in CASES:
        print(f"\nEvaluating: {case_name}")

        # 1. Baseline Run (pareto=False)
        t0 = time.perf_counter()
        res_baseline = pipeline.execute(req, pareto=False)
        t_base = time.perf_counter() - t0

        spec_b = res_baseline.final_specification
        mtow_b = round(spec_b.mass_properties.maximum_takeoff_weight_kg, 4) if spec_b else 0.0
        end_b = round(spec_b.performance.endurance_min, 2) if spec_b else 0.0
        rng_b = round(spec_b.performance.range_km, 2) if spec_b else 0.0

        # Compare with 6B-4 baseline
        b4_data = b4_baseline.get(case_name, {})
        mtow_b4 = b4_data.get("mtow_kg", 0.0)
        end_b4 = b4_data.get("endurance_min", 0.0)
        rng_b4 = b4_data.get("range_km", 0.0)

        delta_mtow = abs(mtow_b - mtow_b4)
        delta_end = abs(end_b - end_b4)
        delta_rng = abs(rng_b - rng_b4)

        match = (delta_mtow < 0.001 and delta_end < 0.1 and delta_rng < 0.1)
        print(f"  [Baseline] MTOW: {mtow_b} kg (B4: {mtow_b4}), End: {end_b} min (B4: {end_b4}), Rng: {rng_b} km (B4: {rng_b4}) -> Match: {match} ({t_base:.2f}s)")

        output["baseline_comparison"][case_name] = {
            "success": res_baseline.success,
            "pareto_front_is_none": res_baseline.pareto_front is None,
            "mtow_kg": mtow_b,
            "baseline_mtow_kg": mtow_b4,
            "delta_mtow": delta_mtow,
            "endurance_min": end_b,
            "baseline_endurance_min": end_b4,
            "range_km": rng_b,
            "baseline_range_km": rng_b4,
            "baseline_preserved": match,
            "runtime_s": round(t_base, 3),
        }

        # 2. Pareto Run (pareto=True)
        t0 = time.perf_counter()
        res_pareto = pipeline.execute(req, pareto=True)
        t_pareto = time.perf_counter() - t0

        pf: ParetoFrontResult = res_pareto.pareto_front
        valid_self_check, errors = self_check_pareto_front(pf)
        print(f"  [Pareto] Pool: {pf.candidate_count}, Feasible: {pf.feasible_candidate_count}, Dominated: {pf.dominated_candidate_count}, Front Size: {pf.front_size}, Self-Check Valid: {valid_self_check} ({t_pareto:.2f}s)")

        # Record front points
        front_points = []
        for cand in pf.front:
            front_points.append({
                "candidate_id": cand.candidate_id,
                "is_selected_design": cand.is_selected_design,
                "pareto_rank": cand.pareto_rank,
                "mtow_kg": cand.get_value("mtow"),
                "endurance_min": cand.get_value("endurance"),
                "range_km": cand.get_value("range"),
                "payload_kg": cand.get_value("payload_capability"),
                "efficiency_ld": cand.get_value("efficiency"),
                "motor": cand.technical_specifications.get("motor", {}).get("propeller_compatibility"),
                "battery": cand.technical_specifications.get("battery", {}).get("required_capacity_mah"),
                "battery_chem": cand.technical_specifications.get("battery", {}).get("chemistry"),
                "esc_a": cand.technical_specifications.get("esc", {}).get("continuous_current_rating_a"),
            })

        output["pareto_results"][case_name] = {
            "success": res_pareto.success,
            "candidate_count": pf.candidate_count,
            "feasible_candidate_count": pf.feasible_candidate_count,
            "dominated_candidate_count": pf.dominated_candidate_count,
            "deduplicated_count": pf.deduplicated_count,
            "front_size": pf.front_size,
            "self_check_passed": valid_self_check,
            "self_check_errors": errors,
            "front": front_points,
            "runtime_s": round(t_pareto, 3),
        }

        output["runtime_metrics"][case_name] = {
            "baseline_runtime_s": round(t_base, 3),
            "pareto_runtime_s": round(t_pareto, 3),
            "overhead_ratio": round(t_pareto / max(t_base, 0.001), 2),
        }

    with open("scratch/phase6b6_validation_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 80)
    print("Forensic validation complete! Results saved to scratch/phase6b6_validation_results.json")
    print("=" * 80)


if __name__ == "__main__":
    run_validation()
