#!/usr/bin/env python3
"""
Phase 2 Validation Script.
Executes:
- TEST A: SECURITY (0.5 kg, 30 min, 30 km, 80 km/h, RUNWAY, RUNWAY, RURAL, BALANCED)
- TEST B: INSPECTION (0.5 kg, 20 min, 20 km, 60 km/h, RUNWAY, RUNWAY, URBAN, LOWEST_WEIGHT)
- TEST C: MILITARY (2.0 kg, 45 min, 10 km, 80 km/h, RUNWAY, RUNWAY, COASTAL, BALANCED)
- REGRESSION 1: SURVEY 0.5 kg
- REGRESSION 2: SURVEY 1.0 kg
- REGRESSION 3: AGRICULTURE 2.0 kg
Performs all 12 engineering sanity checks.
"""

import os
import sys
import math

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
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

def validate_case(name: str, req: RequirementModel):
    print(f"\n{'='*75}\nRUNNING {name}\n{'='*75}")
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    res = pipeline.execute(req)
    
    print(f"Pipeline Status  : {res.status}")
    print(f"Success          : {res.success}")
    print(f"Converged        : {res.converged}")
    print(f"Iterations       : {res.iterations}")
    
    # Mission Category
    if res.mission_result:
        m_cat = getattr(res.mission_result.mission_profile, "mission_category", None)
        req_env = req.environment.value
        prof_env = getattr(res.mission_result.mission_profile, "environment", None)
        print(f"Mission Category : {m_cat} | Req Env: {req_env} | Profile Env: {prof_env}")
    
    # Configuration
    if res.configuration_result:
        cfg = res.configuration_result
        print(f"Config Wing Pos  : {getattr(cfg, 'wing_position', None)}")
        print(f"Config Prop      : {getattr(cfg, 'propulsion_configuration', None)}")
        print(f"Config Tail      : {getattr(cfg, 'tail_configuration', None)}")
        
    # Wing Geometry
    wing_geom = None
    if res.wing_result:
        wing_geom = getattr(res.wing_result, "wing_geometry", res.wing_result)
        span = getattr(wing_geom, "span_m", 0.0)
        area = getattr(wing_geom, "area_m2", 0.0)
        ar = getattr(wing_geom, "aspect_ratio", 0.0)
        root_c = getattr(wing_geom, "root_chord_m", 0.0)
        tip_c = getattr(wing_geom, "tip_chord_m", 0.0)
        mac = getattr(wing_geom, "mean_aerodynamic_chord_m", 0.0)
        print(f"Wing Span        : {span:.4f} m")
        print(f"Wing Area        : {area:.4f} m²")
        print(f"Aspect Ratio     : {ar:.4f}")
        print(f"Root Chord       : {root_c:.4f} m")
        print(f"Tip Chord        : {tip_c:.4f} m")
        print(f"MAC              : {mac:.4f} m")
        
    # Fuselage Geometry
    fuse_geom = None
    if res.fuselage_result:
        fuse_geom = getattr(res.fuselage_result, "fuselage_geometry", res.fuselage_result)
        f_len = getattr(fuse_geom, "length_m", 0.0)
        f_wid = getattr(fuse_geom, "width_m", 0.0)
        f_hgt = getattr(fuse_geom, "height_m", 0.0)
        print(f"Fuselage Length  : {f_len:.4f} m")
        print(f"Fuselage Width   : {f_wid:.4f} m")
        print(f"Fuselage Height  : {f_hgt:.4f} m")
        
        # Check root chord vs fuselage width
        if wing_geom:
            clearance_margin = root_c - f_wid
            print(f"Root Chord - Fuselage Width Delta: {clearance_margin:+.4f} m ({clearance_margin/f_wid*100:+.1f}%)")
            assert root_c > f_wid, f"Root chord {root_c} must exceed fuselage width {f_wid}!"
            
    # Mass Properties
    mtow = 0.0
    cg = None
    sm = None
    if res.mass_properties_result:
        mp = res.mass_properties_result
        if hasattr(mp, "weight_breakdown") and mp.weight_breakdown:
            wb = mp.weight_breakdown
            mtow = getattr(wb, "useful_load_kg", 0.0) + getattr(wb, "structural_weight_kg", 0.0) + getattr(wb, "propulsion_weight_kg", 0.0) + getattr(wb, "avionics_weight_kg", 0.0)
        elif hasattr(mp, "total_takeoff_weight_kg"):
            mtow = mp.total_takeoff_weight_kg
        elif hasattr(mp, "mtow_kg"):
            mtow = mp.mtow_kg

        cg = getattr(mp, "center_of_gravity", None)
        sm = getattr(mp, "static_margin", None)
        print(f"Reported MTOW    : {mtow:.4f} kg")
        print(f"Center of Gravity: {cg}")
        print(f"Static Margin    : {sm:.2%}" if sm is not None else "Static Margin: None")
        
    # Performance
    v_stall = 0.0
    if res.performance_result:
        perf = res.performance_result
        if hasattr(perf, "stall_analysis"):
            v_stall = getattr(perf.stall_analysis, "stall_speed_clean_kmh", 0.0)
            print(f"Clean Stall Speed: {v_stall:.2f} km/h")
        if hasattr(perf, "endurance_analysis"):
            endur = getattr(perf.endurance_analysis, "cruise_endurance_min", 0.0)
            print(f"Cruise Endurance : {endur:.2f} min (Target: {req.target_flight_time_min} min)")
        if hasattr(perf, "range_analysis"):
            rng = getattr(perf.range_analysis, "cruise_range_km", 0.0)
            print(f"Cruise Range     : {rng:.2f} km (Target: {req.target_range_km} km)")
            
    if res.errors:
        print(f"Errors           : {res.errors}")
    if res.warnings:
        print(f"Warnings ({len(res.warnings)}): {res.warnings[:3]}")

    # 12 Engineering Sanity Checks
    print("\n--- 12 ENGINEERING SANITY CHECKS ---")
    checks = []
    # 1. wing area > 0
    c1 = area > 0.0 and math.isfinite(area)
    checks.append(("1. Wing Area > 0", c1, f"{area:.4f} m²"))

    # 2. wingspan > 0
    c2 = span > 0.0 and math.isfinite(span)
    checks.append(("2. Wingspan > 0", c2, f"{span:.4f} m"))

    # 3. root chord > fuselage width
    c3 = root_c > f_wid and (root_c - f_wid) > 0.0
    checks.append(("3. Root Chord > Fuselage Width", c3, f"{root_c:.4f} m > {f_wid:.4f} m (delta: {root_c - f_wid:+.4f} m)"))

    # 4. aspect ratio is physically consistent with span² / area
    calc_ar = (span ** 2) / area if area > 0 else 0.0
    c4 = abs(ar - calc_ar) < 0.05
    checks.append(("4. AR physically consistent (b²/S)", c4, f"Reported: {ar:.2f}, Calc: {calc_ar:.2f}"))

    # 5. fuselage dimensions are positive
    c5 = f_len > 0.0 and f_wid > 0.0 and f_hgt > 0.0 and math.isfinite(f_len * f_wid * f_hgt)
    checks.append(("5. Fuselage Dimensions Positive", c5, f"L={f_len:.3f}, W={f_wid:.3f}, H={f_hgt:.3f}"))

    # 6. CG is valid
    c6 = cg is not None and len(cg) == 3 and not any(math.isnan(x) for x in cg) and (0.0 < cg[0] < f_len)
    checks.append(("6. CG Valid", c6, f"CG={cg}"))

    # 7. static margin is valid
    c7 = sm is not None and not math.isnan(sm) and 0.0 < sm < 0.50
    checks.append(("7. Static Margin Valid", c7, f"SM={sm:.2%}" if sm is not None else "None"))

    # 8. stall speed is finite and positive
    c8 = v_stall > 0.0 and math.isfinite(v_stall)
    checks.append(("8. Stall Speed Finite and Positive", c8, f"{v_stall:.2f} km/h"))

    # 9. propulsion sizing succeeds
    c9 = res.propulsion_result is not None
    checks.append(("9. Propulsion Sizing Succeeds", c9, "PropulsionResult Present" if c9 else "Missing"))

    # 10. mass conservation remains valid
    comp_sum = 0.0
    if res.mass_properties_result and hasattr(mp, "component_masses") and mp.component_masses:
        if isinstance(mp.component_masses, list):
            comp_sum = sum(getattr(c, "mass_kg", 0.0) for c in mp.component_masses)
        elif isinstance(mp.component_masses, dict):
            comp_sum = sum(mp.component_masses.values())
    c10 = (abs(mtow - comp_sum) < 0.10) if comp_sum > 0 else (mtow > 0.0)
    checks.append(("10. Mass Conservation Valid", c10, f"MTOW={mtow:.3f} kg, Sum(Components)={comp_sum:.3f} kg"))

    # 11. no hidden validation errors are suppressed
    c11 = len(res.errors) == 0 and res.success is True
    checks.append(("11. No Hidden Validation Errors", c11, f"Errors: {res.errors}"))

    # 12. no NaN/None/zero substitution is masking a missing calculation
    c12 = all([c1, c2, c3, c4, c5, c8, c9])
    checks.append(("12. No NaN/Zero Substitution", c12, "All Primary Fields Verified"))

    all_passed = True
    for cname, passed, detail in checks:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"  [{status_str}] {cname:35}: {detail}")
    print(f"Overall Sanity Check: {'ALL PASSED' if all_passed else 'SOME CHECKS FAILED'}\n")
    assert all_passed, f"Engineering sanity checks failed for {name}!"
        
    return res

def main():
    results = {}
    
    # TEST A: SECURITY
    req_sec = RequirementModel(
        mission_type=MissionType.SECURITY,
        payload_weight_kg=0.5,
        target_flight_time_min=30.0,
        target_range_km=30.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    results["SECURITY"] = validate_case("TEST A: SECURITY (0.5 kg)", req_sec)
    
    # TEST B: INSPECTION
    req_insp = RequirementModel(
        mission_type=MissionType.INSPECTION,
        payload_weight_kg=0.5,
        target_flight_time_min=20.0,
        target_range_km=20.0,
        cruise_speed_kmh=60.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.URBAN,
        optimization_priority=OptimizationPriority.LOWEST_WEIGHT,
    )
    results["INSPECTION"] = validate_case("TEST B: INSPECTION (0.5 kg)", req_insp)
    
    # TEST C: MILITARY
    req_mil = RequirementModel(
        mission_type=MissionType.MILITARY,
        payload_weight_kg=2.0,
        target_flight_time_min=45.0,
        target_range_km=10.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.COASTAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    results["MILITARY"] = validate_case("TEST C: MILITARY (2.0 kg, COASTAL)", req_mil)
    
    # REGRESSION 1: SURVEY 0.5 kg
    req_s05 = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    results["SURVEY_05"] = validate_case("REGRESSION 1: SURVEY (0.5 kg)", req_s05)
    
    # REGRESSION 2: SURVEY 1.0 kg
    req_s10 = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=60.0,
        target_range_km=50.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    results["SURVEY_10"] = validate_case("REGRESSION 2: SURVEY (1.0 kg)", req_s10)
    
    # REGRESSION 3: AGRICULTURE 2.0 kg
    req_agri = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=25.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    results["AGRICULTURE"] = validate_case("REGRESSION 3: AGRICULTURE (2.0 kg)", req_agri)
    
    print("\n" + "="*75)
    print("PHASE 2 VALIDATION SUMMARY:")
    for name, r in results.items():
        w_res = getattr(r, "wing_result", None)
        f_res = getattr(r, "fuselage_result", None)
        c_root = getattr(w_res.wing_geometry, "root_chord_m", 0.0) if (w_res and hasattr(w_res, "wing_geometry")) else 0.0
        f_wid = getattr(f_res.fuselage_geometry, "width_m", 0.0) if (f_res and hasattr(f_res, "fuselage_geometry")) else 0.0
        print(f"{name:15}: Status={r.status.value:10} Converged={str(r.converged):5} Iter={r.iterations} | RootChord={c_root:.3f}m FuseWidth={f_wid:.3f}m Delta={c_root - f_wid:+.3f}m")
    print("="*75)

if __name__ == "__main__":
    main()
