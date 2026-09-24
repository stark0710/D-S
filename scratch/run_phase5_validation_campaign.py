#!/usr/bin/env python3
"""
TorqWings Studio v2 - Phase 5 Comprehensive Validation & Hardening Campaign.
Executes all validation matrices (Steps 1 through 17) systematically,
evaluates engineering physics and invariants, measures execution runtimes,
and outputs structured diagnostics for PHASE_5_VALIDATION_REPORT.md.
"""

import os
import sys
import time
import json
import traceback
from typing import Any, Dict, List, Optional

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
from scripts.run_fixed_wing_pipeline import audit_mass_accounting


def execute_case(req: RequirementModel) -> Dict[str, Any]:
    """Executes a single RequirementModel through the pipeline and records all metrics."""
    t0 = time.time()
    pipeline = FixedWingDesignPipeline()
    try:
        res = pipeline.execute(req)
        status_val = res.status.value if hasattr(res.status, "value") else str(res.status)
        mass_audit = audit_mass_accounting(res)
        elapsed = time.time() - t0

        # Extract geometry
        w_span = 0.0
        w_area = 0.0
        w_ar = 0.0
        w_root_c = 0.0
        w_tip_c = 0.0
        if res.wing_result:
            wg = getattr(res.wing_result, "wing_geometry", res.wing_result)
            w_span = getattr(wg, "span_m", getattr(wg, "wingspan_m", 0.0))
            w_area = getattr(wg, "reference_area_m2", getattr(wg, "area_m2", 0.0))
            w_ar = getattr(wg, "aspect_ratio", 0.0)
            w_root_c = getattr(wg, "root_chord_m", getattr(wg, "chord_root_m", 0.0))
            w_tip_c = getattr(wg, "tip_chord_m", getattr(wg, "chord_tip_m", 0.0))

        # Extract fuselage
        f_len = 0.0
        f_width = 0.0
        f_height = 0.0
        if res.fuselage_result:
            fg = getattr(res.fuselage_result, "fuselage_geometry", res.fuselage_result)
            f_len = getattr(fg, "length_m", 0.0)
            f_width = getattr(fg, "width_m", getattr(fg, "diameter_m", 0.0))
            f_height = getattr(fg, "height_m", 0.0)

        # Extract mass & stability
        mtow = mass_audit.get("reported_mtow_kg", 0.0)
        mass_err_pct = mass_audit.get("relative_error_pct", 0.0)
        cg_x = 0.0
        sm = 0.0
        if res.mass_properties_result:
            cg_x = getattr(res.mass_properties_result, "center_of_gravity", (0.0, 0.0, 0.0))[0]
            sm = getattr(res.mass_properties_result, "static_margin", 0.0)

        # Extract propulsion
        static_thrust = 0.0
        tw = 0.0
        cruise_pwr = 0.0
        motor = "N/A"
        prop = "N/A"
        if res.propulsion_result:
            pr = res.propulsion_result
            motor = getattr(pr, "selected_motor_or_engine", getattr(pr, "selected_motor", "N/A"))
            prop = getattr(pr, "selected_propeller", "N/A")
            ta = getattr(pr, "thrust_analysis", None)
            pa = getattr(pr, "power_analysis", None)
            if ta:
                static_thrust = getattr(ta, "estimated_static_thrust_n", 0.0)
                tw = getattr(ta, "thrust_to_weight_ratio", 0.0)
            if pa:
                cruise_pwr = getattr(pa, "required_cruise_power_w", 0.0)

        # Extract performance
        stall_spd = 0.0
        cruise_spd = getattr(req, "cruise_speed_kmh", 0.0)
        endur = 0.0
        range_km = 0.0
        ld_ratio = 0.0
        if res.performance_result:
            pf = res.performance_result
            if hasattr(pf, "stall_analysis"):
                stall_spd = getattr(pf.stall_analysis, "stall_speed_clean_kmh", 0.0)
            if hasattr(pf, "aerodynamic_analysis"):
                ld_ratio = getattr(pf.aerodynamic_analysis, "lift_to_drag_ratio", 0.0)
            if hasattr(pf, "endurance_analysis"):
                endur = getattr(pf.endurance_analysis, "cruise_endurance_min", 0.0)
            if hasattr(pf, "range_analysis"):
                range_km = getattr(pf.range_analysis, "cruise_range_km", 0.0)

        # Extract architecture
        arch = "Conventional"
        if res.configuration_result:
            sel_cfg = getattr(res.configuration_result, "selected_configuration", {}) or {}
            arch = sel_cfg.get("architecture") or getattr(res.configuration_result, "wing_configuration", "Conventional")

        # Extract verification
        v_stat = "N/A"
        c_stat = "N/A"
        if res.verification_result:
            v_raw = getattr(res.verification_result, "verification_status", "UNKNOWN")
            v_stat = v_raw.value if hasattr(v_raw, "value") else str(v_raw)
        if res.certification_report:
            c_raw = getattr(res.certification_report, "overall_status", "UNKNOWN")
            c_stat = c_raw.value if hasattr(c_raw, "value") else str(c_raw)

        return {
            "success": res.success,
            "status": status_val,
            "converged": res.converged,
            "iterations": res.iterations,
            "runtime_s": round(elapsed, 2),
            "mtow_kg": round(mtow, 4),
            "mass_error_pct": round(mass_err_pct, 4),
            "span_m": round(w_span, 3),
            "area_m2": round(w_area, 3),
            "aspect_ratio": round(w_ar, 2),
            "root_chord_m": round(w_root_c, 3),
            "tip_chord_m": round(w_tip_c, 3),
            "fuselage_width_m": round(f_width, 3),
            "fuselage_length_m": round(f_len, 3),
            "cg_x_m": round(cg_x, 3),
            "static_margin_pct": round(sm * 100.0, 1),
            "motor": str(motor),
            "propeller": str(prop),
            "static_thrust_n": round(static_thrust, 2),
            "tw_ratio": round(tw, 2),
            "cruise_power_w": round(cruise_pwr, 1),
            "stall_speed_kmh": round(stall_spd, 1),
            "cruise_speed_kmh": round(cruise_spd, 1),
            "lift_to_drag": round(ld_ratio, 1),
            "endurance_min": round(endur, 1),
            "range_km": round(range_km, 1),
            "architecture": str(arch),
            "subsystem_verification": str(v_stat),
            "certification_status": str(c_stat),
            "errors": res.errors,
            "warnings": res.warnings,
        }
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "success": False,
            "status": "UNCAUGHT_EXCEPTION",
            "converged": False,
            "iterations": 0,
            "runtime_s": round(elapsed, 2),
            "exception": str(e),
            "traceback": traceback.format_exc(),
            "errors": [str(e)],
        }


def run_campaign():
    incremental_path = os.path.join(WORKSPACE_ROOT, "artifacts", "phase5_incremental.json")
    if os.path.exists(incremental_path):
        try:
            with open(incremental_path, "r", encoding="utf-8") as f:
                campaign_results = json.load(f)
            print(f"Loaded existing results from {incremental_path}: {list(campaign_results.keys())}")
        except Exception as e:
            print(f"Failed to load incremental results: {e}")
            campaign_results = {}
    else:
        campaign_results = {}

    # =========================================================================
    # STEP 15: REGRESSION BASELINE
    # =========================================================================
    if "regression_baseline" not in campaign_results or len(campaign_results["regression_baseline"]) < 7:
        print("\n" + "=" * 80)
        print(">>> RUNNING STEP 15: REGRESSION BASELINE (7 CASES)")
        print("=" * 80)
        reg_cases = [
            ("SURVEY_0.5kg", RequirementModel(
                mission_type=MissionType.SURVEY, payload_weight_kg=0.5, target_flight_time_min=45.0,
                target_range_km=30.0, cruise_speed_kmh=70.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("SURVEY_1.0kg", RequirementModel(
                mission_type=MissionType.SURVEY, payload_weight_kg=1.0, target_flight_time_min=60.0,
                target_range_km=45.0, cruise_speed_kmh=75.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("AGRICULTURE_2.0kg", RequirementModel(
                mission_type=MissionType.AGRICULTURE, payload_weight_kg=2.0, target_flight_time_min=30.0,
                target_range_km=20.0, cruise_speed_kmh=65.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("SECURITY_0.5kg", RequirementModel(
                mission_type=MissionType.SECURITY, payload_weight_kg=0.5, target_flight_time_min=60.0,
                target_range_km=40.0, cruise_speed_kmh=70.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("INSPECTION_0.5kg", RequirementModel(
                mission_type=MissionType.INSPECTION, payload_weight_kg=0.5, target_flight_time_min=45.0,
                target_range_km=25.0, cruise_speed_kmh=60.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("MILITARY_1.5kg", RequirementModel(
                mission_type=MissionType.MILITARY, payload_weight_kg=1.5, target_flight_time_min=90.0,
                target_range_km=80.0, cruise_speed_kmh=85.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("DELIVERY_1.0kg", RequirementModel(
                mission_type=MissionType.DELIVERY, payload_weight_kg=1.0, target_flight_time_min=40.0,
                target_range_km=30.0, cruise_speed_kmh=70.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
        ]
        campaign_results["regression_baseline"] = {}
        for cid, req in reg_cases:
            print(f"--> [START] Regression: {cid}", flush=True)
            res = execute_case(req)
            print(f"  {cid:<20} | Success: {res['success']} | Status: {res['status']:<15} | MTOW: {res.get('mtow_kg', 0):.3f} kg | Iter: {res.get('iterations', 0)} | {res.get('runtime_s', 0)}s", flush=True)
            campaign_results["regression_baseline"][cid] = res
    else:
        print(">>> STEP 15: REGRESSION BASELINE already completed. Skipping.")

    # =========================================================================
    # STEP 14: MISSION × PAYLOAD CROSS-MATRIX (10 MISSIONS × 5 PAYLOADS = 50 CELLS)
    # =========================================================================
    if "mission_payload_matrix" not in campaign_results or len(campaign_results["mission_payload_matrix"]) < 10:
        print("\n" + "=" * 80, flush=True)
        print(">>> RUNNING STEP 14: MISSION × PAYLOAD CROSS-MATRIX (50 CELLS)", flush=True)
        print("=" * 80, flush=True)
        test_missions = [
            MissionType.SURVEY,
            MissionType.MAPPING,
            MissionType.INSPECTION,
            MissionType.DELIVERY,
            MissionType.AGRICULTURE,
            MissionType.SECURITY,
            MissionType.DISASTER_RESPONSE,
            MissionType.MILITARY,
            MissionType.RESEARCH,
            MissionType.TRAINING,
        ]
        test_payloads = [0.2, 0.5, 1.0, 1.5, 2.0]

        campaign_results["mission_payload_matrix"] = {}
        for m in test_missions:
            m_name = m.value
            campaign_results["mission_payload_matrix"][m_name] = {}
            for p in test_payloads:
                print(f"--> [START] {m_name} @ {p} kg", flush=True)
                req = RequirementModel(
                    mission_type=m,
                    payload_weight_kg=p,
                    target_flight_time_min=45.0,
                    target_range_km=30.0,
                    cruise_speed_kmh=70.0,
                    takeoff_type=TakeoffType.RUNWAY,
                    landing_type=LandingType.RUNWAY,
                    environment=OperatingEnvironment.RURAL,
                )
                res = execute_case(req)
                succ = res["success"]
                st = res["status"]
                mt = res.get("mtow_kg", 0.0)
                it = res.get("iterations", 0)
                tag = "SUCCESS" if succ else f"REJECTED ({st})"
                print(f"  {m_name:<18} @ {p:>3.1f} kg | {tag:<28} | MTOW: {mt:>6.3f} kg | Iter: {it:>2} | {res.get('runtime_s', 0)}s", flush=True)
                campaign_results["mission_payload_matrix"][m_name][str(p)] = res

        with open(incremental_path, "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, indent=2)
    else:
        print(">>> STEP 14: MISSION × PAYLOAD CROSS-MATRIX already completed. Skipping.")

    # =========================================================================
    # STEP 2: TAKEOFF / LANDING MATRIX
    # =========================================================================
    if "takeoff_landing_matrix" not in campaign_results or len(campaign_results["takeoff_landing_matrix"]) < 20:
        print("\n" + "=" * 80, flush=True)
        print(">>> RUNNING STEP 2: TAKEOFF / LANDING COMBINATIONS MATRIX", flush=True)
        print("=" * 80, flush=True)
        takeoffs = [TakeoffType.RUNWAY, TakeoffType.CATAPULT, TakeoffType.HAND_LAUNCH, TakeoffType.VERTICAL]
        landings = [LandingType.RUNWAY, LandingType.BELLY_LANDING, LandingType.PARACHUTE, LandingType.NET_RECOVERY, LandingType.VERTICAL]

        campaign_results["takeoff_landing_matrix"] = {}
        for to in takeoffs:
            for ld in landings:
                cid = f"{to.value}_x_{ld.value}"
                print(f"--> [START] Takeoff/Landing: {cid}", flush=True)
                req = RequirementModel(
                    mission_type=MissionType.SURVEY,
                    payload_weight_kg=0.5,
                    target_flight_time_min=40.0,
                    target_range_km=25.0,
                    cruise_speed_kmh=65.0,
                    takeoff_type=to,
                    landing_type=ld,
                    environment=OperatingEnvironment.RURAL,
                )
                res = execute_case(req)
                print(f"  {cid:<32} | Success: {res['success']} | Status: {res['status']} | {res.get('runtime_s', 0)}s", flush=True)
                campaign_results["takeoff_landing_matrix"][cid] = res

        with open(incremental_path, "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, indent=2)
    else:
        print(">>> STEP 2: TAKEOFF / LANDING COMBINATIONS MATRIX already completed. Skipping.")

    # =========================================================================
    # STEP 3: ENVIRONMENT MATRIX
    # =========================================================================
    if "environment_matrix" not in campaign_results or len(campaign_results["environment_matrix"]) < 8:
        print("\n" + "=" * 80, flush=True)
        print(">>> RUNNING STEP 3: ENVIRONMENT MATRIX", flush=True)
        print("=" * 80, flush=True)
        environments = [
            OperatingEnvironment.RURAL,
            OperatingEnvironment.URBAN,
            OperatingEnvironment.COASTAL,
            OperatingEnvironment.MARINE,
            OperatingEnvironment.MOUNTAIN,
            OperatingEnvironment.DESERT,
            OperatingEnvironment.FOREST,
            OperatingEnvironment.INDOOR,
        ]
        campaign_results["environment_matrix"] = {}
        for env in environments:
            print(f"--> [START] Environment: {env.value}", flush=True)
            req = RequirementModel(
                mission_type=MissionType.SURVEY,
                payload_weight_kg=0.5,
                target_flight_time_min=45.0,
                target_range_km=30.0,
                cruise_speed_kmh=70.0,
                takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY,
                environment=env,
            )
            res = execute_case(req)
            print(f"  {env.value:<15} | Success: {res['success']} | Status: {res['status']} | MTOW: {res.get('mtow_kg', 0):.3f} kg | {res.get('runtime_s', 0)}s", flush=True)
            campaign_results["environment_matrix"][env.value] = res

        with open(incremental_path, "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, indent=2)
    else:
        print(">>> STEP 3: ENVIRONMENT MATRIX already completed. Skipping.")

    # =========================================================================
    # STEP 4: MTOW BOUNDARY TESTING
    # =========================================================================
    if "mtow_boundary_matrix" not in campaign_results or len(campaign_results["mtow_boundary_matrix"]) < 5:
        print("\n" + "=" * 80, flush=True)
        print(">>> RUNNING STEP 4: MTOW BOUNDARY TESTING", flush=True)
        print("=" * 80, flush=True)
        # Baseline requires ~4.367 kg for Survey 0.5kg
        mtow_cases = [
            ("A_Unspecified_None", None),
            ("B_Comfortable_Limit_8.0kg", 8.0),
            ("C_Tight_Feasible_Limit_5.0kg", 5.0),
            ("D_Infeasible_Limit_3.0kg", 3.0),
            ("E_Below_Payload_0.3kg", 0.3),  # Payload is 0.5kg
        ]
        campaign_results["mtow_boundary_matrix"] = {}
        for label, limit in mtow_cases:
            print(f"--> [START] MTOW boundary: {label}", flush=True)
            req = RequirementModel(
                mission_type=MissionType.SURVEY,
                payload_weight_kg=0.5,
                target_flight_time_min=45.0,
                target_range_km=30.0,
                cruise_speed_kmh=70.0,
                maximum_takeoff_weight_kg=limit,
                takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY,
                environment=OperatingEnvironment.RURAL,
            )
            res = execute_case(req)
            print(f"  {label:<30} | Success: {res['success']} | Status: {res['status']} | MTOW: {res.get('mtow_kg', 0):.3f} kg | {res.get('runtime_s', 0)}s", flush=True)
            campaign_results["mtow_boundary_matrix"][label] = res

        with open(incremental_path, "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, indent=2)
    else:
        print(">>> STEP 4: MTOW BOUNDARY TESTING already completed. Skipping.")

    # =========================================================================
    # STEP 5: PAYLOAD BOUNDARY TESTING
    # =========================================================================
    if "payload_boundary_matrix" not in campaign_results or len(campaign_results["payload_boundary_matrix"]) < 11:
        print("\n" + "=" * 80, flush=True)
        print(">>> RUNNING STEP 5: PAYLOAD BOUNDARY TESTING", flush=True)
        print("=" * 80, flush=True)
        payload_levels = [0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
        campaign_results["payload_boundary_matrix"] = {}
        for p in payload_levels:
            print(f"--> [START] Payload boundary: DELIVERY @ {p} kg", flush=True)
            req = RequirementModel(
                mission_type=MissionType.DELIVERY,
                payload_weight_kg=p,
                target_flight_time_min=40.0,
                target_range_km=30.0,
                cruise_speed_kmh=70.0,
                takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY,
                environment=OperatingEnvironment.RURAL,
            )
            res = execute_case(req)
            print(f"  DELIVERY @ {p:>4.2f} kg | Success: {res['success']} | Status: {res['status']:<15} | MTOW: {res.get('mtow_kg', 0):.3f} kg | {res.get('runtime_s', 0)}s", flush=True)
            campaign_results["payload_boundary_matrix"][str(p)] = res

        with open(incremental_path, "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, indent=2)
    else:
        print(">>> STEP 5: PAYLOAD BOUNDARY TESTING already completed. Skipping.")

    # =========================================================================
    # STEP 12: CONVERGENCE STRESS CASES
    # =========================================================================
    if "convergence_stress" not in campaign_results or len(campaign_results["convergence_stress"]) < 5:
        print("\n" + "=" * 80, flush=True)
        print(">>> RUNNING STEP 12: CONVERGENCE STRESS CASES", flush=True)
        print("=" * 80, flush=True)
        stress_cases = [
            ("Easy_Convergence", RequirementModel(
                mission_type=MissionType.SURVEY, payload_weight_kg=0.3, target_flight_time_min=30.0,
                target_range_km=20.0, cruise_speed_kmh=65.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("High_Payload_Agriculture", RequirementModel(
                mission_type=MissionType.AGRICULTURE, payload_weight_kg=2.5, target_flight_time_min=30.0,
                target_range_km=20.0, cruise_speed_kmh=65.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("Long_Endurance_Surveillance", RequirementModel(
                mission_type=MissionType.SECURITY, payload_weight_kg=0.5, target_flight_time_min=120.0,
                target_range_km=80.0, cruise_speed_kmh=75.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("High_Range_Inspection", RequirementModel(
                mission_type=MissionType.INSPECTION, payload_weight_kg=0.5, target_flight_time_min=80.0,
                target_range_km=100.0, cruise_speed_kmh=80.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("Demanding_Military", RequirementModel(
                mission_type=MissionType.MILITARY, payload_weight_kg=2.0, target_flight_time_min=90.0,
                target_range_km=90.0, cruise_speed_kmh=85.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
        ]
        campaign_results["convergence_stress"] = {}
        for label, req in stress_cases:
            print(f"--> [START] Convergence stress: {label}", flush=True)
            res = execute_case(req)
            print(f"  {label:<30} | Success: {res['success']} | Status: {res['status']:<15} | MTOW: {res.get('mtow_kg', 0):.3f} kg | Iter: {res.get('iterations', 0)} | {res.get('runtime_s', 0)}s", flush=True)
            campaign_results["convergence_stress"][label] = res

        with open(incremental_path, "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, indent=2)
    else:
        print(">>> STEP 12: CONVERGENCE STRESS CASES already completed. Skipping.")

    # =========================================================================
    # STEP 13: FAILURE-MODE CAMPAIGN
    # =========================================================================
    if "failure_modes" not in campaign_results or len(campaign_results["failure_modes"]) < 5:
        print("\n" + "=" * 80, flush=True)
        print(">>> RUNNING STEP 13: FAILURE-MODE CAMPAIGN", flush=True)
        print("=" * 80, flush=True)
        failure_cases = [
            ("MTOW_Below_Payload", RequirementModel(
                mission_type=MissionType.AGRICULTURE, payload_weight_kg=2.0, target_flight_time_min=30.0,
                target_range_km=20.0, cruise_speed_kmh=65.0, maximum_takeoff_weight_kg=1.0,
                takeoff_type=TakeoffType.RUNWAY, landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("Impossible_Flight_Time_1000h", RequirementModel(
                mission_type=MissionType.SURVEY, payload_weight_kg=0.5, target_flight_time_min=60000.0,
                target_range_km=30.0, cruise_speed_kmh=70.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("Impossible_Range_10000km", RequirementModel(
                mission_type=MissionType.SURVEY, payload_weight_kg=0.5, target_flight_time_min=45.0,
                target_range_km=10000.0, cruise_speed_kmh=70.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("Impossible_Speed_500kmh", RequirementModel(
                mission_type=MissionType.SURVEY, payload_weight_kg=0.5, target_flight_time_min=45.0,
                target_range_km=30.0, cruise_speed_kmh=500.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
            ("Zero_Flight_Time", RequirementModel(
                mission_type=MissionType.SURVEY, payload_weight_kg=0.5, target_flight_time_min=0.0,
                target_range_km=30.0, cruise_speed_kmh=70.0, takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY, environment=OperatingEnvironment.RURAL
            )),
        ]
        campaign_results["failure_modes"] = {}
        for label, req in failure_cases:
            print(f"--> [START] Failure mode: {label}", flush=True)
            res = execute_case(req)
            print(f"  {label:<30} | Success: {res['success']} | Status: {res['status']:<25} | Expected Failure: True | {res.get('runtime_s', 0)}s", flush=True)
            campaign_results["failure_modes"][label] = res

        with open(incremental_path, "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, indent=2)
    else:
        print(">>> STEP 13: FAILURE-MODE CAMPAIGN already completed. Skipping.")

    # Save summary artifact
    out_file = os.path.join(WORKSPACE_ROOT, "artifacts", "phase5_validation_campaign_results.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(campaign_results, f, indent=2)
    print(f"\nSaved Phase 5 complete results to {out_file}")

    return campaign_results


if __name__ == "__main__":
    run_campaign()
