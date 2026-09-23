#!/usr/bin/env python3
"""
TorqWings Studio v2 - VTOL Interactive Design Pipeline Runner.

Purpose:
    Dedicated CLI entry point for the VTOL design pipeline.
    Accepts VTOL requirements interactively or via CLI arguments,
    invokes the production VTOLDesignPipeline orchestrator, displays a comprehensive
    terminal summary, and exports structured JSON and Markdown reports.

Architecture Rule:
    The runner MUST NOT contain engineering calculations or physics equations.
    All sizing, aerodynamics, and optimization logic reside strictly within
    `backend/design/vtol/` and locked Fixed-Wing interfaces.
"""

import os
import sys
import json
import argparse
import datetime
from typing import Any, Dict, List, Optional

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel
from backend.design.vtol.pipeline.vtol_design_pipeline import VTOLDesignPipeline
from backend.design.vtol.pipeline.pipeline_result import (
    VTOLDesignResult,
    PipelineStatus,
    to_dict_recursive,
)


def print_banner() -> None:
    """Prints TorqWings VTOL Studio banner."""
    print("=" * 78)
    print("      TORQWINGS STUDIO v2 — VTOL AIRCRAFT DESIGN & SYNTHESIS RUNNER     ")
    print("                 Phase 1 Architecture & Foundation Mode                 ")
    print("=" * 78)


def prompt_float(prompt: str, default: float, min_val: float = 0.0) -> float:
    """Safely prompts for a floating point number with default."""
    while True:
        try:
            val_str = input(f"{prompt} [{default}]: ").strip()
            if not val_str:
                return default
            val = float(val_str)
            if val <= min_val:
                print(f"  [!] Value must be greater than {min_val}. Please re-enter.")
                continue
            return val
        except ValueError:
            print("  [!] Invalid number. Please enter a valid decimal.")


def prompt_selection(prompt: str, options: List[str], default_idx: int = 0) -> str:
    """Prompts user to select from a list of options."""
    print(f"\n{prompt}")
    for idx, opt in enumerate(options):
        marker = "*" if idx == default_idx else " "
        print(f"  [{idx + 1}]{marker} {opt}")
    while True:
        choice = input(f"Enter choice [1-{len(options)}] (Default: {default_idx + 1}): ").strip()
        if not choice:
            return options[default_idx]
        if choice.isdigit():
            i = int(choice) - 1
            if 0 <= i < len(options):
                return options[i]
        print(f"  [!] Invalid selection. Enter 1 to {len(options)}.")


def collect_requirements_interactive() -> VTOLRequirementModel:
    """Collects VTOL requirements interactively from the terminal."""
    print_banner()
    print("\n--- 1. MISSION & PERFORMANCE TARGETS ---")
    payload = prompt_float("Payload mass (kg)", 2.0, min_val=0.0)
    range_km = prompt_float("Target cruise range (km)", 40.0, min_val=0.0)
    endurance_min = prompt_float("Target flight time (minutes)", 30.0, min_val=0.0)
    cruise_speed = prompt_float("Cruise speed (km/h)", 90.0, min_val=0.0)

    print("\n--- 2. VTOL OPERATIONAL PARAMETERS ---")
    hover_endurance = prompt_float("Target hover duration (minutes)", 5.0, min_val=0.0)
    transition_speed = prompt_float("Transition stall/forward speed (km/h)", 65.0, min_val=0.0)
    lift_motors = int(prompt_float("Number of dedicated VTOL lift motors", 4.0, min_val=1.0))

    configs = ["LIFT_CRUISE (QuadPlane / Dedicated Lift + Push/Pull)"]
    prompt_selection("Supported VTOL Configurations:", configs, 0)

    return VTOLRequirementModel.create(
        mission_type=MissionType.SURVEY,
        payload_mass=payload,
        target_range=range_km,
        target_flight_time=endurance_min,
        cruise_speed=cruise_speed,
        vtol_type=VTOLType.LIFT_CRUISE,
        hover_duration_min=hover_endurance,
        transition_speed_kmh=transition_speed,
        lift_motor_count=lift_motors,
        takeoff_type=TakeoffType.VERTICAL,
        landing_type=LandingType.VERTICAL,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.MANUAL,
    )


def display_results_terminal(result: VTOLDesignResult, req: VTOLRequirementModel) -> None:
    """Displays structured summary of pipeline execution in the terminal."""
    print("\n" + "=" * 78)
    print("                     VTOL PIPELINE EXECUTION SUMMARY                    ")
    print("=" * 78)

    status_str = result.status.value if isinstance(result.status, PipelineStatus) else str(result.status)
    success_badge = "[OK] SUCCESS" if result.is_success else f"[!] {status_str}"
    print(f"Overall Pipeline Status  : {success_badge}")
    print(f"Sizing Iterations        : {result.iterations}")
    print(f"Convergence Achieved     : {result.converged}")

    spec = result.final_specification
    if spec:
        print("\n--- AIRCRAFT SIZING SYNTHESIS ---")
        print(f"  Configuration Type     : {spec.configuration_type or 'LIFT_CRUISE'}")
        print(f"  Takeoff Mass (MTOW)    : {spec.mtow_kg:.3f} kg")
        print(f"  Empty Weight           : {spec.empty_weight_kg:.3f} kg")
        print(f"  Payload Capacity       : {spec.payload_weight_kg:.2f} kg")
        print(f"  Calculated Endurance   : {spec.estimated_endurance_min:.1f} min")
        print(f"  Calculated Range       : {spec.estimated_range_km:.2f} km")

        if spec.vtol_configuration:
            cfg = spec.vtol_configuration
            print("\n--- VTOL CONFIGURATION ARCHITECTURE ---")
            print(f"  Lift Motor Count       : {cfg.lift_motor_count}")
            print(f"  Lift Rotor Count       : {cfg.lift_rotor_count}")
            print(f"  Cruise Propulsion Count: {cfg.cruise_propulsion_count}")
            print(f"  Arrangement            : {cfg.propulsion_arrangement}")
            print(f"  Wing Configuration     : {cfg.wing_configuration}")
            print(f"  Tail Configuration     : {cfg.tail_configuration}")

        if spec.stage_statuses:
            print("\n--- SUBSYSTEM IMPLEMENTATION STATUS (PHASE 1 ARCHITECTURE) ---")
            for stage, st in spec.stage_statuses.items():
                marker = "[IMPLEMENTED]" if st in ("IMPLEMENTED", "SUCCESS") else f"[{st}]"
                print(f"  {stage:<28} : {marker}")

        if spec.fixed_wing_subsystems:
            fw = spec.fixed_wing_subsystems
            print("\n--- FIXED-WING CRUISE BOUNDARY RESULTS ---")
            print(f"  Interface Status       : {fw.status}")
            if fw.wing:
                w_geom = getattr(fw.wing, "wing_geometry", None)
                span = getattr(w_geom, "span_m", 0.0) if w_geom else 0.0
                area = getattr(w_geom, "area_m2", getattr(w_geom, "reference_area_m2", 0.0)) if w_geom else 0.0
                print(f"  Cruise Wing Span       : {span:.2f} m (Area: {area:.3f} m²)")
            if fw.tail:
                t_geom = getattr(fw.tail, "tail_geometry", None)
                h_area = getattr(t_geom, "horizontal_area_m2", 0.0) if t_geom else 0.0
                print(f"  Cruise Tail Horiz Area : {h_area:.3f} m²")
            if fw.fuselage:
                f_geom = getattr(fw.fuselage, "fuselage_geometry", None)
                vol = getattr(f_geom, "volume_m3", 0.0) if f_geom else 0.0
                print(f"  Fuselage Volume        : {vol:.3f} m³")

        if spec.electrical:
            elec = spec.electrical
            print("\n--- PHASE 4 ELECTRICAL & BATTERY SIZING ---")
            if elec.battery_sizing:
                bs = elec.battery_sizing
                print(f"  Mission Energy         : {bs.mission_energy_wh:.1f} Wh")
                print(f"  Reserve Energy ({(bs.reserve_fraction*100.0):.0f}%)   : {bs.reserve_energy_wh:.1f} Wh")
                print(f"  Required Usable Energy : {bs.required_usable_energy_wh:.1f} Wh")
                print(f"  Nominal Battery Energy : {bs.required_nominal_battery_energy_wh:.1f} Wh")
                if bs.nominal_voltage_v:
                    print(f"  Nominal System Voltage : {bs.nominal_voltage_v:.1f} V")
                if bs.required_nominal_capacity_ah:
                    print(f"  Required Ah Capacity   : {bs.required_nominal_capacity_ah:.2f} Ah")
            if elec.electrical_envelope:
                env = elec.electrical_envelope
                print(f"  Max Continuous Power   : {env.maximum_continuous_power_w:.1f} W")
                print(f"  Max Peak Power (Trans) : {env.maximum_peak_power_w:.1f} W")
                if env.continuous_current_a:
                    print(f"  Continuous Current     : {env.continuous_current_a:.1f} A")
                if env.peak_current_a:
                    print(f"  Peak Current           : {env.peak_current_a:.1f} A")
                if env.peak_c_rate:
                    print(f"  Peak C-Rate            : {env.peak_c_rate:.2f} C")
            if elec.mission_energy_ledger:
                print(f"  Mission Energy Ledger  : {len(elec.mission_energy_ledger.segments)} phases (Double counting: {elec.mission_energy_ledger.has_double_counting})")
            if getattr(elec, "authoritative_energy_result", None) and getattr(elec.authoritative_energy_result, "parameter_provenance", None):
                prov = elec.authoritative_energy_result.parameter_provenance
                print("  Parameter Provenance Breakdown:")
                for param, info in prov.items():
                    val_str = f"{info['value']}" if info['value'] is not None else "N/A"
                    print(f"    - {param:<26}: {val_str:<8} [{info['classification']}] ({info['provenance_source']})")

        if spec.mass_properties and getattr(spec.mass_properties, "authoritative_mass_result", None):
            auth_m = spec.mass_properties.authoritative_mass_result
            print("\n--- 8. MASS, CG & MTOW CONVERGENCE (PHASE 5) ---")
            print(f"  Converged MTOW         : {auth_m.converged_mtow_kg:.3f} kg")
            print(f"  Empty Weight           : {auth_m.empty_weight_kg:.3f} kg")
            print(f"  Payload Weight         : {auth_m.payload_weight_kg:.2f} kg")
            print(f"  Battery Weight         : {auth_m.battery_weight_kg:.3f} kg")
            print(f"  Convergence Status     : {auth_m.convergence_status.value}")
            print(f"  Convergence Iterations : {auth_m.convergence_iterations}")
            print(f"  Final Residual         : {auth_m.convergence_residual_kg:.6f} kg (tolerance: {auth_m.convergence_tolerance_kg} kg)")
            print(f"  Under-relaxation Alpha : {auth_m.relaxation_alpha:.2f}")
            cg = auth_m.center_of_gravity
            if cg.x_cg_pct_mac is not None:
                print(f"  Center of Gravity (CG) : x_cg = {cg.x_cg_m:.4f} m ({cg.x_cg_pct_mac:.1f}% MAC, datum: {cg.datum_reference})")
            else:
                print(f"  Center of Gravity (CG) : x_cg = {cg.x_cg_m:.4f} m (datum: {cg.datum_reference})")
            
            ledger = auth_m.mass_ledger
            print(f"  Mass Ledger Components : {len(ledger.components)} items")
            bd = ledger.category_breakdown
            print(f"    - Structure          : {bd.structure_mass_kg:.3f} kg ({bd.structure_mass_kg/ledger.total_mass_kg*100:.1f}%)")
            print(f"    - Propulsion         : {bd.propulsion_mass_kg:.3f} kg ({bd.propulsion_mass_kg/ledger.total_mass_kg*100:.1f}%)")
            print(f"    - Electrical         : {bd.electrical_mass_kg:.3f} kg ({bd.electrical_mass_kg/ledger.total_mass_kg*100:.1f}%)")
            print(f"    - Avionics           : {bd.avionics_mass_kg:.3f} kg ({bd.avionics_mass_kg/ledger.total_mass_kg*100:.1f}%)")
            print(f"    - Payload            : {bd.payload_mass_kg:.3f} kg ({bd.payload_mass_kg/ledger.total_mass_kg*100:.1f}%)")
            if bd.other_mass_kg > 0:
                print(f"    - Other              : {bd.other_mass_kg:.3f} kg ({bd.other_mass_kg/ledger.total_mass_kg*100:.1f}%)")
            print(f"  Conservation Residual  : {ledger.conservation_residual_kg:.6f} kg")
            if ledger.unresolved_components:
                print(f"  Unresolved Inputs      : {', '.join(ledger.unresolved_components)}")

        if spec.tail and getattr(spec.tail, "authoritative_stability_result", None):
            auth_s = spec.tail.authoritative_stability_result
            long_s = auth_s.longitudinal_stability
            dir_s = auth_s.directional_stability
            vtail = auth_s.vtail_panel_geometry
            vproj = auth_s.vtail_projections
            rv = auth_s.ruddervator_geometry
            ail = auth_s.aileron_geometry
            c_auth = auth_s.control_authority
            trim = auth_s.trim_analysis
            env = auth_s.cg_envelope

            print("\n--- 9. STABILITY DERIVATIVES & CONTROL-SURFACE SIZING (PHASE 6) ---")
            print(f"  Converged MTOW         : {long_s.mtow_kg:.3f} kg")
            print(f"  Center of Gravity (CG) : x_cg = {long_s.x_cg_m:.4f} m ({long_s.cg_mac_pct:.1f}% MAC)")
            print(f"  Wing Mean Aero Chord   : MAC = {long_s.mac_m:.4f} m (LE: {long_s.wing_le_x_m:.4f} m)")
            print(f"  Wing Aerodynamic Center: x_AC = {long_s.x_ac_w_m:.4f} m ({long_s.x_ac_w_mac_pct:.1f}% MAC)")
            print(f"  Neutral Point (NP)     : x_NP = {long_s.x_np_m:.4f} m ({long_s.neutral_point_mac_pct:.1f}% MAC)")
            print(f"  Static Margin          : {long_s.static_margin_mac_pct:.2f}% MAC ({long_s.static_margin_m:.4f} m) [{long_s.stability_margin_status.value}]")
            print(f"  Tail Volume Coeffs     : V_H = {long_s.v_h:.4f}, V_V = {dir_s.v_v:.4f}")
            print(f"  Inverted V-Tail Geom   : Total Planform = {vtail.total_vtail_planform_area_m2:.4f} m² (2 panels x {vtail.panel_area_m2:.4f} m²)")
            print(f"                           Dihedral = {vtail.v_tail_angle_deg:.1f}° | Aspect Ratio = {vtail.aspect_ratio:.2f}")
            print(f"  V-Tail Projections     : S_H_geom = {vproj.horizontal_projected_area_geom_m2:.4f} m², S_V_geom = {vproj.vertical_projected_area_geom_m2:.4f} m²")
            print(f"                           S_H_eff  = {vproj.horizontal_effective_area_m2:.4f} m², S_V_eff  = {vproj.vertical_effective_area_m2:.4f} m²")
            print(f"  Ruddervator Sizing     : Area = {rv.total_ruddervator_area_m2:.4f} m² ({rv.ruddervator_to_tail_ratio*100:.1f}% tail, chord ratio = {rv.chord_ratio:.2f})")
            print(f"                           Mixer: Left = de - dr, Right = de + dr (Limits: ±{rv.max_deflection_deg:.0f}°)")
            print(f"  Aileron Sizing         : Total Area = {ail.total_aileron_area_m2:.4f} m² ({ail.aileron_to_wing_ratio*100:.2f}% wing, span = 2 x {ail.span_per_side_m:.3f} m)")
            print(f"                           Semispan = {ail.inner_semispan_fraction*100:.0f}%-{ail.outer_semispan_fraction*100:.0f}% b/2 (Chord: {ail.chord_m:.4f} m)")
            print(f"  Stability Derivatives  : C_m_alpha = {long_s.c_m_alpha:.4f} 1/rad (Pitch stiff: {long_s.is_pitch_stiff})")
            print(f"                           C_n_beta  = {dir_s.c_n_beta:.4f} 1/rad (Weathercock: {dir_s.is_directionally_stable})")
            print(f"  Control Derivatives    : C_m_delta_e = {auth_s.control_derivatives.c_m_delta_e:.4f} 1/rad, C_n_delta_r = {auth_s.control_derivatives.c_n_delta_r:.4f} 1/rad, C_l_delta_a = {auth_s.control_derivatives.c_l_delta_a:.4f} 1/rad")
            print(f"  Quasi-Steady Trim      : Status = {trim.trim_status.value} (Cruise: de = {trim.cruise_trim.elevator_trim_deg:.2f}°, Margin: {trim.cruise_trim.trim_margin_deg:.1f}°)")
            print(f"  Control Authority      : Status = {c_auth.pitch_authority_status.value} (Pitch Max = {c_auth.max_pitch_moment_nm:.2f} N·m, Yaw Max = {c_auth.max_yaw_moment_nm:.2f} N·m, Roll Max = {c_auth.max_roll_moment_nm:.2f} N·m)")
            print(f"  Longitudinal CG Env    : [{env.forward_cg_x_m:.4f} m .. {env.aft_cg_x_m:.4f} m] (Width: {env.envelope_width_pct_mac:.1f}% MAC) [{getattr(env.cg_envelope_status, 'value', str(env.cg_envelope_status))}]")
            print(f"  Phase 6 Verification   : {'PASS' if len(auth_s.errors) == 0 else 'FAIL'} ({len(auth_s.warnings)} warnings)")

    if result.warnings:
        print("\n--- WARNINGS ---")
        for w in result.warnings[:10]:
            print(f"  [!] {w}")

    if result.errors:
        print("\n--- ERRORS ---")
        for e in result.errors[:10]:
            print(f"  [X] {e}")

    print("=" * 78 + "\n")


def export_reports(
    result: VTOLDesignResult,
    req: VTOLRequirementModel,
    output_dir: str,
) -> None:
    """Exports structured JSON and Markdown design reports."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Structured JSON export
    json_path = os.path.join(output_dir, "vtol_specification.json")
    dict_payload = result.to_dict()
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dict_payload, f, indent=2)
    print(f"[+] Exported JSON specification: {json_path}")

    # 2. Markdown engineering report
    spec = result.final_specification
    md_path = os.path.join(output_dir, "vtol_engineering_report.md")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# VTOL Sizing Synthesis & Engineering Architecture Report\n\n")
        f.write(f"*Generated on: {timestamp}*\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write(f"- **Overall Status**: `{result.status.value if hasattr(result.status, 'value') else result.status}`\n")
        f.write(f"- **Converged**: `{result.converged}`\n")
        f.write(f"- **Iterations**: `{result.iterations}`\n\n")

        if spec:
            f.write("## 2. Aircraft Specifications\n\n")
            f.write(f"- **MTOW**: `{spec.mtow_kg:.3f} kg`\n")
            f.write(f"- **Empty Weight**: `{spec.empty_weight_kg:.3f} kg`\n")
            f.write(f"- **Payload Weight**: `{spec.payload_weight_kg:.2f} kg`\n")
            f.write(f"- **Estimated Endurance**: `{spec.estimated_endurance_min:.1f} min`\n")
            f.write(f"- **Estimated Range**: `{spec.estimated_range_km:.2f} km`\n\n")

            if spec.vtol_configuration:
                cfg = spec.vtol_configuration
                f.write("## 3. Configuration & Propulsion Architecture\n\n")
                f.write(f"- **Architecture Type**: `{cfg.configuration_type.value}`\n")
                f.write(f"- **Lift Motors**: `{cfg.lift_motor_count}`\n")
                f.write(f"- **Lift Rotors**: `{cfg.lift_rotor_count}`\n")
                f.write(f"- **Cruise Motors**: `{cfg.cruise_propulsion_count}`\n")
                f.write(f"- **Propulsion Arrangement**: `{cfg.propulsion_arrangement}`\n")
                f.write(f"- **Wing Configuration**: `{cfg.wing_configuration}`\n")
                f.write(f"- **Tail Configuration**: `{cfg.tail_configuration}`\n\n")

            if spec.stage_statuses:
                f.write("## 4. Phase 1 Architecture Stage Inventory\n\n")
                f.write("| Subsystem / Stage | Architectural Status | Scope Classification |\n")
                f.write("|:---|:---:|:---|\n")
                for stage, st in spec.stage_statuses.items():
                    f.write(f"| `{stage}` | `{st}` | {'Phase 1 Core' if 'NOT' not in st else 'Phase 2+ Deferred Physics'} |\n")
                f.write("\n")

            if spec.fixed_wing_subsystems:
                fw = spec.fixed_wing_subsystems
                f.write("## 5. Fixed-Wing Integration Boundary\n\n")
                f.write(f"- **Adapter Status**: `{fw.status}`\n")
                f.write(f"- **Delegated Subsystems**: Wing, Tail, Fuselage, Cruise Propulsion, Forward Aerodynamics\n\n")

            if spec.mass_properties and getattr(spec.mass_properties, "authoritative_mass_result", None):
                auth_m = spec.mass_properties.authoritative_mass_result
                cg = auth_m.center_of_gravity
                ledger = auth_m.mass_ledger
                f.write("## 6. Mass Properties, CG & Multidisciplinary Convergence (Phase 5)\n\n")
                f.write(f"- **Converged MTOW**: `{auth_m.converged_mtow_kg:.3f} kg`\n")
                f.write(f"- **Empty Weight**: `{auth_m.empty_weight_kg:.3f} kg`\n")
                f.write(f"- **Battery Weight**: `{auth_m.battery_weight_kg:.3f} kg`\n")
                f.write(f"- **Payload Weight**: `{auth_m.payload_weight_kg:.2f} kg`\n")
                f.write(f"- **Convergence Status**: `{auth_m.convergence_status.value}` ({auth_m.convergence_iterations} iterations, residual `{auth_m.convergence_residual_kg:.6f} kg`)\n")
                cg_mac_str = f"{cg.x_cg_pct_mac:.1f}% MAC" if cg.x_cg_pct_mac is not None else "N/A"
                f.write(f"- **Longitudinal CG**: `x_cg = {cg.x_cg_m:.4f} m` ({cg_mac_str}, datum: `{cg.datum_reference}`)\n")
                f.write(f"- **Mass Conservation Residual**: `{ledger.conservation_residual_kg:.6f} kg`\n\n")
                f.write("### Component Mass Ledger\n\n")
                f.write("| Category | Component | Mass (kg) | x_arm (m) | Moment (kg*m) | Classification |\n")
                f.write("|:---|:---|:---:|:---:|:---:|:---:|\n")
                for c in ledger.components:
                    f.write(f"| `{c.category.value}` | {c.name} | {c.mass_kg:.4f} | {c.x_arm_m:.3f} | {c.moment_kg_m:.4f} | `{c.classification.value}` |\n")
                f.write("\n")

            if spec.tail and getattr(spec.tail, "authoritative_stability_result", None):
                auth_s = spec.tail.authoritative_stability_result
                long_s = auth_s.longitudinal_stability
                dir_s = auth_s.directional_stability
                lat_s = auth_s.lateral_stability
                vtail = auth_s.vtail_panel_geometry
                vproj = auth_s.vtail_projections
                rv = auth_s.ruddervator_geometry
                ail = auth_s.aileron_geometry
                c_auth = auth_s.control_authority
                trim = auth_s.trim_analysis
                env = auth_s.cg_envelope

                f.write("## 7. Aerodynamic Stability Derivatives & Control-Surface Sizing (Phase 6)\n\n")
                f.write(f"- **Wing MAC**: `{long_s.mac_m:.4f} m` (LE: `{long_s.wing_le_x_m:.4f} m`)\n")
                f.write(f"- **Wing Aerodynamic Center**: `x_AC = {long_s.x_ac_w_m:.4f} m` ({long_s.x_ac_w_mac_pct:.1f}% MAC)\n")
                f.write(f"- **Neutral Point**: `x_NP = {long_s.x_np_m:.4f} m` ({long_s.neutral_point_mac_pct:.1f}% MAC)\n")
                f.write(f"- **Static Margin**: `{long_s.static_margin_mac_pct:.2f}% MAC` ({long_s.static_margin_m:.4f} m) [`{long_s.stability_margin_status.value}`]\n")
                f.write(f"- **Tail Volume Coefficients**: `V_H = {long_s.v_h:.4f}`, `V_V = {dir_s.v_v:.4f}`\n\n")

                f.write("### Inverted V-Tail & Control Surfaces\n\n")
                f.write(f"- **Inverted V-Tail Area**: `{vtail.total_vtail_planform_area_m2:.4f} m²` (2 panels x `{vtail.panel_area_m2:.4f} m²`, dihedral: `{vtail.v_tail_angle_deg:.1f}°`)\n")
                f.write(f"- **Projected Areas**: Horizontal = `{vproj.horizontal_projected_area_geom_m2:.4f} m²`, Vertical = `{vproj.vertical_projected_area_geom_m2:.4f} m²`\n")
                f.write(f"- **Effective Lift Areas**: S_H_eff = `{vproj.horizontal_effective_area_m2:.4f} m²`, S_V_eff = `{vproj.vertical_effective_area_m2:.4f} m²`\n")
                f.write(f"- **Ruddervator Area**: `{rv.total_ruddervator_area_m2:.4f} m²` ({rv.ruddervator_to_tail_ratio*100:.1f}% tail, chord ratio `{rv.chord_ratio:.2f}`)\n")
                f.write(f"- **Ruddervator Mixing**: `{rv.mixer_convention}` (Limits: `±{rv.max_deflection_deg:.0f}°`)\n")
                f.write(f"- **Wing Aileron Area**: `{ail.total_aileron_area_m2:.4f} m²` ({ail.aileron_to_wing_ratio*100:.2f}% wing, span: 2 x `{ail.span_per_side_m:.3f} m`)\n\n")

                f.write("### Stability & Control Derivatives\n\n")
                f.write(f"- `C_m_alpha`: `{long_s.c_m_alpha:.4f} 1/rad` (Pitch Stiff: `{long_s.is_pitch_stiff}`)\n")
                f.write(f"- `C_n_beta`: `{dir_s.c_n_beta:.4f} 1/rad` (Weathercock Stable: `{dir_s.is_directionally_stable}`)\n")
                f.write(f"- `C_l_beta`: `{lat_s.c_l_beta_per_rad:.4f} 1/rad` (Dihedral Effect: `{lat_s.is_laterally_stable}`)\n")
                f.write(f"- `C_m_delta_e`: `{auth_s.control_derivatives.c_m_delta_e:.4f} 1/rad`\n")
                f.write(f"- `C_n_delta_r`: `{auth_s.control_derivatives.c_n_delta_r:.4f} 1/rad`\n")
                f.write(f"- `C_l_delta_a`: `{auth_s.control_derivatives.c_l_delta_a:.4f} 1/rad`\n\n")

                f.write("### Trim Feasibility & CG Envelope\n\n")
                f.write(f"- **Overall Trim Status**: `{trim.trim_status.value}`\n")
                f.write(f"- **Longitudinal CG Envelope**: `[{env.forward_cg_x_m:.4f} m .. {env.aft_cg_x_m:.4f} m]` (Width: `{env.envelope_width_pct_mac:.1f}% MAC`, Status: `{getattr(env.cg_envelope_status, 'value', str(env.cg_envelope_status))}`)\n")
                f.write(f"- **Control Authority Status**: `{c_auth.pitch_authority_status.value}` (Pitch Max: `{c_auth.max_pitch_moment_nm:.2f} N·m`, Yaw Max: `{c_auth.max_yaw_moment_nm:.2f} N·m`, Roll Max: `{c_auth.max_roll_moment_nm:.2f} N·m`)\n\n")

    print(f"[+] Exported Markdown report   : {md_path}")


def main() -> int:
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="TorqWings Studio v2 - VTOL Design Pipeline Runner (Phase 1)"
    )
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive batch mode")
    parser.add_argument("--payload", type=float, default=2.0, help="Payload mass in kg (default: 2.0)")
    parser.add_argument("--range", type=float, default=40.0, help="Target range in km (default: 40.0)")
    parser.add_argument("--endurance", type=float, default=30.0, help="Target endurance in minutes (default: 30.0)")
    parser.add_argument("--speed", type=float, default=90.0, help="Cruise speed in km/h (default: 90.0)")
    parser.add_argument("--hover-time", type=float, default=5.0, help="Hover duration in minutes (default: 5.0)")
    parser.add_argument("--lift-motors", type=int, default=4, help="Number of lift motors (default: 4)")
    parser.add_argument("--output-dir", type=str, default="reports", help="Output directory for reports")

    args = parser.parse_args()

    if args.non_interactive:
        req = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=args.payload,
            target_range=args.range,
            target_flight_time=args.endurance,
            cruise_speed=args.speed,
            vtol_type=VTOLType.LIFT_CRUISE,
            hover_duration_min=args.hover_time,
            transition_speed_kmh=65.0,
            lift_motor_count=args.lift_motors,
            takeoff_type=TakeoffType.VERTICAL,
            landing_type=LandingType.VERTICAL,
            environment=OperatingEnvironment.RURAL,
            optimization_priority=OptimizationPriority.BALANCED,
            design_mode=DesignMode.MANUAL,
        )
    else:
        req = collect_requirements_interactive()

    # Instantiate pipeline and execute
    pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, relaxation_alpha=0.70, raise_on_failure=False)
    result = pipeline.execute(req)

    # Terminal summary
    display_results_terminal(result, req)

    # Export reports
    export_reports(result, req, args.output_dir)

    return 0 if result.is_success or result.status == PipelineStatus.PARTIAL else 1


if __name__ == "__main__":
    sys.exit(main())
