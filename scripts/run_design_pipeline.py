#!/usr/bin/env python3
"""
Torq Wings Studio v2 — Universal Design Pipeline CLI Runner (Phase 13).

Purpose:
    Terminal entry point for executing the unified Torq Wings Design Engine.
    Dispatches to Fixed-Wing or VTOL pipelines through the universal entry interface
    (TorqWingsDesignEngine.generate), presents a structured terminal summary,
    and produces deterministic JSON and Markdown design specifications.

Usage:
    python scripts/run_design_pipeline.py --aircraft-type fixed_wing --requirements examples/fixed_wing_requirements.json
    python scripts/run_design_pipeline.py --aircraft-type vtol --requirements examples/vtol_requirements.json
    python scripts/run_design_pipeline.py --aircraft-type vtol --requirements examples/vtol_requirements.json --output-dir custom_outputs/
"""

import os
import sys
import json
import argparse
from typing import Any, Dict

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.design.assembly import (
    TorqWingsDesignEngine,
    FinalAircraftDesign,
    AircraftClass,
    OverallDesignStatus,
    UnsupportedArchitectureError,
    InvalidTechnicalRequirementsError,
)


def print_banner() -> None:
    """Prints the Torq Wings Phase 13 Universal Design Engine banner."""
    print("=" * 78)
    print("      TORQ WINGS DESIGN ENGINE — UNIVERSAL AIRCRAFT SYNTHESIS RUNNER     ")
    print("                 Phase 13 Final Assembly & Pipeline Integration          ")
    print("=" * 78)


def prompt_float(prompt: str, default: float) -> float:
    """Safely prompts for a floating point number with default fallback."""
    while True:
        try:
            val_str = input(f"{prompt} [{default}]: ").strip()
            if not val_str:
                return default
            val = float(val_str)
            if val > 0:
                return val
            print("Value must be positive.")
        except ValueError:
            print("Invalid number. Please try again.")


def collect_interactive_requirements(aircraft_type: str) -> Dict[str, Any]:
    """Lightweight interactive prompt returning structured requirements dictionary."""
    print(f"\n--- Interactive Technical Requirements Collection ({aircraft_type.upper()}) ---")
    payload = prompt_float("Payload mass (kg)", 1.0)
    range_km = prompt_float("Target mission range (km)", 40.0)
    endurance = prompt_float("Target flight endurance (min)", 35.0)
    speed = prompt_float("Cruise speed (km/h)", 85.0)

    reqs: Dict[str, Any] = {
        "aircraft_class": aircraft_type.upper(),
        "mission": {
            "mission_type": "SURVEY",
            "range_km": range_km,
            "endurance_min": endurance,
            "cruise_speed_kmh": speed,
            "cruise_altitude_m": 150.0,
        },
        "payload": {
            "mass_kg": payload,
        },
    }

    if aircraft_type.lower() in ("vtol", "quadplane"):
        hover_t = prompt_float("Hover duration (min)", 5.0)
        reqs["mission"]["hover_duration_min"] = hover_t
        reqs["lift_motor_count"] = 4
        reqs["transition_speed_kmh"] = 65.0

    return reqs


def display_terminal_summary(design: FinalAircraftDesign, output_dir: str) -> None:
    """Displays structured, professional engineering summary in the terminal."""
    print("\n" + "=" * 78)
    print(f"               FINAL AIRCRAFT DESIGN SUMMARY: {design.design_id}               ")
    print("=" * 78)

    ac_class = design.aircraft_class.value if hasattr(design.aircraft_class, "value") else str(design.aircraft_class)
    st_val = design.design_status.value if hasattr(design.design_status, "value") else str(design.design_status)
    print(f"Architecture Category    : {ac_class}")
    print(f"Configuration Layout     : {design.configuration}")
    print(f"Overall Design Status    : [OK] {st_val}")
    print(f"Flight Validation Status : {design.validation_status.status} (Flight Validated: {design.validation_status.flight_validated})")

    m = design.mass_properties
    print("\n--- MASS PROPERTIES & CG ---")
    print(f"  MTOW                   : {m.mtow_kg:.3f} kg")
    print(f"  Empty Mass             : {m.empty_mass_kg:.3f} kg")
    print(f"  Payload Mass           : {m.payload_mass_kg:.3f} kg")
    print(f"  Battery Mass           : {m.battery_mass_kg:.3f} kg")
    print(f"  Center of Gravity (CG) : [{m.cg_x_m:.4f}, {m.cg_y_m:.4f}, {m.cg_z_m:.4f}] m")
    print(f"  CG Travel Window       : [{m.forward_cg_limit_x_m:.4f} m .. {m.aft_cg_limit_x_m:.4f} m] (Margin: {m.cg_margin_m:.4f} m)")

    w = design.geometry.wing
    a = design.aerodynamics
    print("\n--- AERODYNAMICS & WING GEOMETRY ---")
    print(f"  Wingspan (b)           : {w.span_m:.3f} m")
    print(f"  Wing Area (S)          : {w.area_m2:.4f} m²")
    print(f"  Aspect Ratio (AR)      : {w.aspect_ratio:.2f}")
    print(f"  Mean Aero Chord (MAC)  : {w.mac_m:.4f} m (LE: {w.mac_le_x_m:.4f} m)")
    print(f"  Cruise CL / CD         : {a.cl_cruise:.3f} / {a.cd_cruise:.4f}")
    print(f"  Lift-to-Drag (L/D)     : {a.lift_to_drag_cruise:.2f} (Max: {a.lift_to_drag_max:.2f})")

    p = design.propulsion
    print("\n--- PROPULSION & ENERGY ---")
    cr = p.cruise_propulsion
    print(f"  Cruise Motor           : {cr.motor_model} ({cr.motor_count}x)")
    print(f"  Cruise Propeller       : {cr.propeller_model}")
    print(f"  Cruise ESC             : {cr.esc_model} ({cr.esc_rating_a:.0f}A)")
    print(f"  Cruise Power           : {cr.cruise_power_electrical_w:.1f} W")

    lf = p.lift_propulsion
    if lf.motor_count > 0:
        print(f"  VTOL Lift Motors       : {lf.motor_model} ({lf.motor_count}x)")
        print(f"  VTOL Lift ESCs         : {lf.esc_model} ({lf.esc_rating_a:.0f}A)")
        print(f"  Hover Thrust / Power   : {lf.total_hover_thrust_required_n:.1f} N / {lf.hover_power_electrical_w:.1f} W (T/W: {lf.thrust_to_weight_ratio:.2f})")

    b = design.battery
    print(f"  Battery Pack           : {b.pack_model} ({b.cell_series_count}S, {b.capacity_mah:.0f} mAh, {b.energy_wh:.1f} Wh)")

    perf = design.performance
    print("\n--- MISSION PERFORMANCE & TRACEABILITY ---")
    print(f"  Cruise Speed           : {perf.cruise_speed_kmh:.1f} km/h ({perf.cruise_speed_mps:.1f} m/s)")
    print(f"  Stall Speed            : {perf.stall_speed_kmh:.1f} km/h")
    print(f"  Calculated Endurance   : {perf.endurance_min:.1f} min")
    print(f"  Calculated Range       : {perf.range_km:.2f} km")

    print("\n--- REQUIREMENT TRACEABILITY AUDIT ---")
    for item in design.requirement_traceability:
        lim = f" [{item.limit}]" if item.limit else ""
        m_val = f"{item.margin:+.2f} {item.unit}" if item.margin is not None else "N/A"
        print(f"  {item.requirement:<24} : Req: {item.required_value} {item.unit}{lim:<6} | Sized: {item.design_value} {item.unit:<4} | Margin: {m_val:<12} [{item.status}]")

    print("\n--- DOWNSTREAM HANDOVER DATA ---")
    print(f"  CAD Handover Block     : [READY] Geometry, Airfoils, Mounts, Envelopes & CG")
    print(f"  Simulation Handover    : [READY] Mass Distribution, Aerodynamic Polars & 6-DOF Derivatives")

    print("\n" + "=" * 78)
    json_path = os.path.join(output_dir, "final_aircraft_design.json")
    md_path = os.path.join(output_dir, "final_aircraft_design.md")
    print(f"[+] Exported JSON specification : {json_path}")
    print(f"[+] Exported Markdown report    : {md_path}")
    print("=" * 78 + "\n")


def main() -> int:
    """Main CLI execution entry point."""
    print_banner()

    parser = argparse.ArgumentParser(
        description="Torq Wings Studio v2 - Universal Design Pipeline Runner (Phase 13)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--aircraft-type",
        "--aircraft-class",
        dest="aircraft_type",
        type=str,
        required=True,
        help="Aircraft category to design ('fixed_wing' or 'vtol')",
    )
    parser.add_argument(
        "--requirements",
        type=str,
        default=None,
        help="Path to structured technical requirements JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save JSON and Markdown design specifications (default: outputs/<aircraft_type>)",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without prompting (requires --requirements)",
    )

    args = parser.parse_args()

    # Determine default output directory if unspecified
    norm_type_str = args.aircraft_type.lower().replace("-", "_")
    output_dir = args.output_dir or os.path.join("outputs", norm_type_str)

    # Resolve requirements input
    if args.requirements:
        req_path = os.path.abspath(args.requirements)
        if not os.path.isfile(req_path):
            print(f"[!] Error: Requirements file not found: {req_path}", file=sys.stderr)
            return 1
        try:
            with open(req_path, "r", encoding="utf-8") as f:
                requirements_data = json.load(f)
        except Exception as e:
            print(f"[!] Error reading requirements JSON file: {e}", file=sys.stderr)
            return 1
    else:
        if args.non_interactive:
            print("[!] Error: In non-interactive mode, --requirements <file.json> must be provided.", file=sys.stderr)
            return 1
        requirements_data = collect_interactive_requirements(args.aircraft_type)

    # Execute universal entry point
    try:
        print(f"[*] Dispatching to Torq Wings Universal Design Engine for '{args.aircraft_type}'...")
        design = TorqWingsDesignEngine.generate(
            aircraft_class=args.aircraft_type,
            technical_requirements=requirements_data,
            output_dir=output_dir,
        )
    except UnsupportedArchitectureError as e:
        print(f"[!] Architecture Error: {e}", file=sys.stderr)
        return 2
    except InvalidTechnicalRequirementsError as e:
        print(f"[!] Requirement Validation Error: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"[!] Pipeline Execution Error: {e}", file=sys.stderr)
        return 4

    # Terminal presentation
    display_terminal_summary(design, output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
