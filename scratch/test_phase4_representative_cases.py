#!/usr/bin/env python3
"""
TorqWings Studio v2 - Phase 4 Representative Cases & Consistency Verification Script.
Executes the 8 representative cases + 1 failure test case,
runs print_terminal_summary, save_json_artifact, save_markdown_report,
and verifies Terminal / JSON / Markdown data consistency.
"""

import os
import sys
import json
import re

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from scripts.run_fixed_wing_pipeline import (
    audit_mass_accounting,
    print_terminal_summary,
    save_json_artifact,
    save_markdown_report,
)


def run_case(name: str, req: RequirementModel):
    print("\n" + "#" * 80)
    print(f"  RUNNING REPRESENTATIVE CASE: {name}")
    print("#" * 80)

    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)
    mass_audit = audit_mass_accounting(res)

    # 1. Terminal Output
    print_terminal_summary(req, res, mass_audit)

    # 2. JSON Artifact
    timestamp_str = f"phase4_{name.lower().replace(' ', '_')}"
    json_path = save_json_artifact(req, res, mass_audit, timestamp_str)

    # 3. Markdown Report
    md_path = save_markdown_report(req, res, mass_audit, timestamp_str)

    # Read back JSON and Markdown
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Verify consistency
    status_str = res.status.value if hasattr(res.status, "value") else str(res.status)
    mtow_reported = mass_audit["reported_mtow_kg"]

    print(f"\n--- CONSISTENCY VERIFICATION FOR {name} ---")
    print(f"Pipeline Success : {res.success}")
    print(f"Pipeline Status  : {status_str}")
    print(f"Reported MTOW    : {mtow_reported:.3f} kg")
    print(f"Iterations       : {res.iterations}")

    # Verify JSON consistency
    assert json_data["run_metadata"]["success"] == res.success, "JSON success mismatch"
    assert json_data["run_metadata"]["status"] == status_str, "JSON status mismatch"
    assert json_data["run_metadata"]["converged"] == res.converged, "JSON converged mismatch"
    assert json_data["run_metadata"]["iterations"] == res.iterations, "JSON iterations mismatch"
    assert abs(json_data["mass_accounting_audit"]["reported_mtow_kg"] - mtow_reported) < 1e-4, "JSON MTOW mismatch"

    # Verify Markdown consistency
    assert f"`{status_str}`" in md_text, "Markdown status mismatch"
    assert f"`{res.iterations}`" in md_text, "Markdown iterations mismatch"
    if res.success:
        assert f"`{mtow_reported:.3f} kg`" in md_text, "Markdown MTOW mismatch"

    # Check propulsion values consistency
    if res.propulsion_result:
        pr = res.propulsion_result
        ta = getattr(pr, "thrust_analysis", None)
        pa = getattr(pr, "power_analysis", None)
        static_thrust = getattr(ta, "estimated_static_thrust_n", 0.0) if ta else 0.0
        tw = getattr(ta, "thrust_to_weight_ratio", 0.0) if ta else 0.0
        cruise_pwr = getattr(pa, "required_cruise_power_w", 0.0) if pa else 0.0

        print(f"Static Thrust    : {static_thrust:.2f} N")
        print(f"Thrust-to-Weight : {tw:.2f}")
        print(f"Cruise Power     : {cruise_pwr:.1f} W")

        # Confirm non-zero static thrust and T/W for successful runs
        if res.success:
            assert static_thrust > 0, "Static thrust must be > 0 in successful run"
            assert tw > 0, "T/W ratio must be > 0 in successful run"
            assert f"{static_thrust:.2f} N" in md_text, "Markdown must contain correct static thrust"
            assert f"{tw:.2f}" in md_text, "Markdown must contain correct T/W ratio"

    # Check configuration consistency
    if res.configuration_result:
        cfg = res.configuration_result
        sel_cfg = getattr(cfg, "selected_configuration", {}) or {}
        arch = sel_cfg.get("architecture") or getattr(cfg, "wing_configuration", "")
        print(f"Architecture     : {arch}")
        if res.success and arch:
            assert arch in md_text, f"Markdown must contain architecture '{arch}'"

    # Check multi-variable convergence
    if res.convergence_result:
        print(f"Convergence Msg  : {res.convergence_result.message}")
        if hasattr(res.convergence_result, "diagnostics"):
            history = res.convergence_result.diagnostics.get("iteration_history", [])
            print(f"History records  : {len(history)} multidisciplinary iterations recorded")

    print(f"Result files:\n  JSON: {json_path}\n  MD:   {md_path}")
    print(f">>> {name}: PASSED CONSISTENCY CHECKS")

    return {
        "name": name,
        "success": res.success,
        "status": status_str,
        "mtow": mtow_reported,
        "iterations": res.iterations,
        "converged": res.converged,
        "json_path": json_path,
        "md_path": md_path,
    }


def main():
    results = []

    # 1. SURVEY payload = 0.5 kg
    req1 = RequirementModel(
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
    )
    results.append(run_case("Case 1 - SURVEY 0.5kg", req1))

    # 2. SURVEY payload = 1.0 kg
    req2 = RequirementModel(
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
    )
    results.append(run_case("Case 2 - SURVEY 1.0kg", req2))

    # 3. AGRICULTURE payload = 2.0 kg
    req3 = RequirementModel(
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
    )
    results.append(run_case("Case 3 - AGRICULTURE 2.0kg", req3))

    # 4. SECURITY payload = 0.5 kg
    req4 = RequirementModel(
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
    )
    results.append(run_case("Case 4 - SECURITY 0.5kg", req4))

    # 5. INSPECTION payload = 0.5 kg
    req5 = RequirementModel(
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
    )
    results.append(run_case("Case 5 - INSPECTION 0.5kg", req5))

    # 6. MILITARY payload = 1.5 kg
    req6 = RequirementModel(
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
    )
    results.append(run_case("Case 6 - MILITARY 1.5kg", req6))

    # 7. DELIVERY payload = 1.0 kg
    req7 = RequirementModel(
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
    )
    results.append(run_case("Case 7 - DELIVERY 1.0kg", req7))

    # 8. Explicit MTOW Limit Case (Feasible limit = 8.0 kg)
    req8 = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        maximum_takeoff_weight_kg=8.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )
    results.append(run_case("Case 8 - SURVEY MTOW Limit 8.0kg", req8))

    # 9. Failure Case: Intentionally Infeasible Explicit MTOW Limit (MTOW limit = 1.0 kg for 2.0 kg payload)
    req9 = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=60.0,
        target_range_km=40.0,
        cruise_speed_kmh=65.0,
        maximum_takeoff_weight_kg=1.0,  # Physically impossible since payload alone is 2.0 kg!
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )
    results.append(run_case("Case 9 - FAILURE TEST MTOW Limit Infeasible", req9))

    print("\n" + "=" * 80)
    print("                    PHASE 4 REPRESENTATIVE CASES SUMMARY")
    print("=" * 80)
    for r in results:
        status_tag = "PASS" if r["success"] else "EXPECTED FAILURE" if "FAILURE" in r["name"] else "FAIL"
        print(f"{r['name']:<42} | Status: {r['status']:<25} | MTOW: {r['mtow']:>6.3f} kg | Iter: {r['iterations']} | [{status_tag}]")
    print("=" * 80)


if __name__ == "__main__":
    main()
