"""
Fixed-Wing Design Pipeline Phase 2 End-to-End Diagnostic Script.
Runs a synthesis execution for a nominal 2.0 kg payload mapping UAV mission
and prints an engineering diagnostic trace.
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus


def run_diagnostic():
    print("=" * 80)
    print("TORQ WINGS DESIGN STUDIO V3 - FIXED-WING PIPELINE PHASE 2 DIAGNOSTIC")
    print("=" * 80)

    # Define Nominal Mission Requirements
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=2.0,
        target_flight_time_min=90.0,
        target_range_km=60.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )

    print("\n--- 1. INPUT MISSION REQUIREMENTS ---")
    print(f"Mission Type      : {req.mission_type.value}")
    print(f"Payload Weight    : {req.payload_weight_kg:.2f} kg")
    print(f"Target Endurance  : {req.target_flight_time_min:.1f} min")
    print(f"Target Range      : {req.target_range_km:.1f} km")
    print(f"Target Cruise Spd : {req.cruise_speed_kmh:.1f} km/h")
    print(f"Takeoff / Landing : {req.takeoff_type.value} / {req.landing_type.value}")
    print(f"Environment       : {req.environment.value}")

    # Instantiate and execute pipeline
    pipeline = FixedWingDesignPipeline(tolerance=0.01, max_iterations=20)
    print("\nExecuting Multidisciplinary Fixed-Wing Design Pipeline...")
    res = pipeline.execute(req)

    print("\n--- 2. PIPELINE EXECUTION STATUS ---")
    print(f"Success Status    : {res.success}")
    print(f"Pipeline Status   : {res.status.value}")
    print(f"Total Iterations  : {res.iterations}")
    print(f"Converged         : {res.converged}")

    if res.configuration_result:
        cfg = res.configuration_result
        print("\n--- 3. FROZEN ARCHITECTURAL CONFIGURATION ---")
        print(f"Wing Configuration      : {cfg.wing_configuration}")
        print(f"Propulsion Layout       : {cfg.propulsion_configuration}")
        print(f"Tail Configuration      : {cfg.tail_configuration}")
        print(f"Landing Gear Layout     : {cfg.landing_gear_configuration}")
        print(f"Overall Config Score    : {cfg.configuration_score:.2f}")

    print("\n--- 4. ITERATION CONVERGENCE HISTORY ---")
    print(f"{'Iter':<5} | {'Old MTOW (kg)':<14} | {'New MTOW (kg)':<14} | {'Abs Delta (kg)':<14} | {'Rel Delta (%)':<14} | {'Status':<10}")
    print("-" * 80)
    for record in res.convergence_history:
        status_str = "CONVERGED" if record.converged else "SEARCHING"
        print(
            f"{record.iteration:<5} | "
            f"{record.mtow_old:<14.4f} | "
            f"{record.mtow_new:<14.4f} | "
            f"{record.absolute_delta_kg:<14.4f} | "
            f"{record.relative_delta * 100.0:<14.2f} | "
            f"{status_str:<10}"
        )

    if res.success and res.mass_properties_result:
        wb = res.mass_properties_result.weight_breakdown
        total_mtow = wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg
        print("\n--- 5. CONVERGED MASS BREAKDOWN ---")
        print(f"Structural Mass   : {wb.structural_weight_kg:.3f} kg ({wb.structural_weight_kg / total_mtow * 100.0:.1f}%)")
        print(f"Propulsion Mass   : {wb.propulsion_weight_kg:.3f} kg ({wb.propulsion_weight_kg / total_mtow * 100.0:.1f}%)")
        print(f"Avionics Mass     : {wb.avionics_weight_kg:.3f} kg ({wb.avionics_weight_kg / total_mtow * 100.0:.1f}%)")
        print(f"Useful Load Mass  : {wb.useful_load_kg:.3f} kg ({wb.useful_load_kg / total_mtow * 100.0:.1f}%)")
        print(f"Total MTOW        : {total_mtow:.3f} kg (100.0%)")
        print(f"Static Margin     : {res.mass_properties_result.static_margin:.1%}")

    if res.success:
        print("\n--- 6. SUBSYSTEM SYNTHESIS SUMMARY ---")
        w_geom = res.wing_result.wing_geometry
        print(f"Wing Planform     : Area = {w_geom.reference_area_m2:.3f} m2, Span = {w_geom.span_m:.3f} m, AR = {w_geom.aspect_ratio:.2f}, W/S = {w_geom.wing_loading_kg_m2:.2f} kg/m2")
        print(f"Airfoil Selected  : Root = {res.airfoil_result.selected_root_airfoil}, Tip = {res.airfoil_result.selected_tip_airfoil}")
        print(f"Tail Geometry     : Horiz Area = {res.tail_result.horizontal_tail.area_m2:.3f} m2, Vert Area = {res.tail_result.vertical_tail.area_m2:.3f} m2")
        print(f"Fuselage Geometry : Length = {res.fuselage_result.fuselage_geometry.length_m:.3f} m, Height = {res.fuselage_result.fuselage_geometry.height_m:.3f} m, Width = {res.fuselage_result.fuselage_geometry.width_m:.3f} m")
        print(f"Propulsion System : Motor = {res.propulsion_result.selected_motor_or_engine}, Propeller = {res.propulsion_result.selected_propeller}")
        print(f"Flight Envelope   : L/D = {res.performance_result.aerodynamic_analysis.lift_to_drag_ratio:.1f}, Clean Stall Speed = {res.performance_result.stall_analysis.stall_speed_clean_kmh:.1f} km/h")
        print(f"Verification      : Mission Status = {res.verification_result.mission_status}, Verification Status = {res.verification_result.verification_status}")

    print("=" * 80)
    return res


if __name__ == "__main__":
    run_diagnostic()
