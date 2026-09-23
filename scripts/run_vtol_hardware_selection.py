#!/usr/bin/env python3
"""
Torq Wings Studio v2 - VTOL Phase 8 Commercial Hardware Selection CLI.

Purpose:
    Dedicated CLI entry point for commercial COTS component selection, verification,
    interface compatibility evaluation, Bill of Materials (BOM) synthesis,
    and mass/power closure.

Supports:
    - Interactive and non-interactive execution (--non-interactive)
    - Mission parameter overrides (--payload, --range, --endurance, --speed)
    - Category filtering (--category-filter)
    - Structured monospace terminal summaries
    - JSON and Markdown report export to reports/
"""

import argparse
import datetime
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.design.vtol.commercial import (
    HardwareMatcher,
    HardwareCategory,
    VerificationStatus,
    CompatibilityStatus,
    SelectionStatus,
    CATALOG,
)


def print_banner() -> None:
    print("=" * 86)
    print("      TORQ WINGS STUDIO v2 — VTOL COMMERCIAL HARDWARE SELECTION & BOM MAPPING      ")
    print("                    Phase 8 Authoritative Hardware Verification                    ")
    print("=" * 86)


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Formats a clean monospace table for terminal output without non-ASCII characters."""
    if not rows:
        return "No rows to display."
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_str = "| " + " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers)) + " |"
    row_strs = [
        "| " + " | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(r)) + " |"
        for r in rows
    ]
    return "\n".join([sep, header_str, sep] + row_strs + [sep])


def run_hardware_selection_cli(args: argparse.Namespace) -> int:
    print_banner()

    print("\n[1] INITIALIZING HARDWARE SIZING REQUIREMENTS")
    overrides = {
        "payload_mass_kg": args.payload,
        "target_range_km": args.range,
        "target_flight_time_min": args.endurance,
        "cruise_speed_kmh": args.speed,
    }
    print(f"  * Mission Payload: {args.payload:.2f} kg")
    print(f"  * Forward Cruise Range: {args.range:.1f} km")
    print(f"  * Flight Endurance: {args.endurance:.1f} min")
    print(f"  * Cruise Airspeed: {args.speed:.1f} km/h")

    # Initialize matcher and execute
    print("\n[2] EVALUATING COMMERCIAL PRODUCT CATALOG AGAINST ENVELOPES")
    matcher = HardwareMatcher(CATALOG)
    result = matcher.match_hardware(overrides=overrides)

    print(f"  * Selection Status: {result.selection_status.value}")
    print(f"  * Total Engineering Requirements Evaluated: {len(result.engineering_requirements)}")
    print(f"  * Verified Candidate Matches: {len(result.verified_reports)}")
    print(f"  * Rejected / Out-of-Spec Candidates: {len(result.rejected_reports)}")

    # 1. Engineering Requirements Table
    print("\n[3] AUTHORITATIVE ENGINEERING REQUIREMENTS")
    req_headers = ["ID", "Category", "Parameter", "Target Envelope", "Units", "Provenance"]
    req_rows = []
    for r in result.engineering_requirements:
        if args.category_filter and args.category_filter.upper() not in r.category.value:
            continue
        env_str = f">= {r.minimum_value}" if r.minimum_value is not None else f"<= {r.maximum_value}"
        req_rows.append([
            r.requirement_id,
            r.category.value,
            r.parameter,
            env_str,
            r.units,
            r.provenance.value,
        ])
    print(format_table(req_headers, req_rows))

    # 2. Selected Commercial Products Table
    print("\n[4] SELECTED VERIFIED COMMERCIAL HARDWARE")
    sel_headers = ["Category", "Manufacturer", "Product Model", "Key Specification", "Mass (kg)", "Price ($)"]
    sel_rows = []
    for cat, prod in result.selected_products.items():
        if args.category_filter and args.category_filter.upper() not in cat.value:
            continue
        key_spec = ""
        if prod.thrust_n:
            key_spec = f"Thrust: {prod.thrust_n:.1f}N"
        elif prod.get_spec("energy_nominal_wh"):
            key_spec = f"Energy: {prod.get_spec('energy_nominal_wh'):.1f}Wh"
        elif prod.continuous_current_a:
            key_spec = f"Current: {prod.continuous_current_a:.1f}A"
        elif prod.get_spec("pwm_channels"):
            key_spec = f"PWM Ch: {prod.get_spec('pwm_channels')}"
        else:
            key_spec = "Datasheet verified"

        sel_rows.append([
            cat.value,
            prod.manufacturer,
            prod.model_number or prod.product_name,
            key_spec,
            f"{prod.mass_kg:.3f}" if prod.mass_kg else "N/A",
            f"${prod.price_usd:.2f}" if prod.price_usd else "UNKNOWN",
        ])
    print(format_table(sel_headers, sel_rows))

    # 3. System Compatibility Table
    print("\n[5] SYSTEM-LEVEL INTERFACE COMPATIBILITY (14 Pairs)")
    compat_headers = ["Subsystem Interface", "Component A", "Component B", "Status", "Technical Notes"]
    compat_rows = []
    for rec in result.compatibility_matrix.records:
        compat_rows.append([
            rec.interface_name,
            rec.component_a_name[:20],
            rec.component_b_name[:20],
            rec.status.value,
            rec.technical_reason[:45] + "..." if len(rec.technical_reason) > 45 else rec.technical_reason,
        ])
    print(format_table(compat_headers, compat_rows))

    # 4. Bill of Materials Table
    print("\n[6] COMMERCIAL BILL OF MATERIALS (BOM)")
    bom_headers = ["BOM ID", "Item Description", "Qty", "Unit Mass", "Total Mass", "Unit Cost", "Total Cost"]
    bom_rows = []
    for item in result.selected_bom.items:
        if args.category_filter and args.category_filter.upper() not in item.category.value:
            continue
        bom_rows.append([
            item.bom_id,
            item.description[:35],
            str(item.quantity),
            f"{item.unit_mass_kg:.3f} kg",
            f"{item.total_mass_kg:.3f} kg",
            f"${item.unit_price_usd:.2f}" if item.unit_price_usd else "N/A",
            f"${item.total_price_usd:.2f}" if item.total_price_usd else "N/A",
        ])
    print(format_table(bom_headers, bom_rows))
    print(f"  * Total Parts Count: {result.selected_bom.total_parts_count}")
    print(f"  * Total Commercial BOM Mass: {result.selected_bom.total_commercial_mass_kg:.3f} kg")
    print(f"  * Total Commercial BOM Cost: ${result.selected_bom.total_commercial_cost_usd:.2f} USD")

    # 5. Mass & Power Closure Summary
    print("\n[7] SYSTEM CLOSURE & ENGINEERING RE-EVALUATION AUDIT")
    mc = result.mass_closure
    pc = result.power_closure
    print(f"  * Phase 5 Baseline Assumed Hardware Mass: {mc.baseline_assumed_hardware_mass_kg:.3f} kg")
    print(f"  * Selected Commercial Hardware Mass:     {mc.selected_commercial_hardware_mass_kg:.3f} kg")
    print(f"  * Hardware Mass Delta:                   {mc.hardware_mass_delta_kg:+.3f} kg ({mc.hardware_mass_delta_pct:+.2f}% MTOW)")
    print(f"  * Projected Vehicle MTOW:                {mc.mtow_projected_kg:.3f} kg")
    print(f"  * Projected Hover Thrust-to-Weight:      {mc.hover_tw_projected:.2f}")
    print(f"  * Engineering Re-evaluation Required:    {'YES' if mc.requires_reevaluation else 'NO'}")
    print(f"  * Electrical Power Closed:               {'YES' if pc.is_power_closed else 'NO'}")
    print(f"  * Battery Continuous Current Margin:     {pc.battery_current_margin_a:+.1f} A")
    print(f"  * PDB Continuous Current Margin:         {pc.pdb_current_margin_a:+.1f} A")
    print(f"  * 5V BEC Avionics & Servo Margin:        {pc.bec_current_margin_a:+.1f} A")

    if result.unresolved_requirements:
        print("\n[8] DEFERRED / UNRESOLVED SPECIFICATIONS")
        for u in result.unresolved_requirements:
            print(f"  * {u}")

    # Export Reports
    os.makedirs(args.output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(args.output_dir, f"vtol_hardware_selection_{timestamp}.json")
    md_path = os.path.join(args.output_dir, f"vtol_hardware_selection_{timestamp}.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"\n[9] EXPORTED JSON REPORT: {json_path}")

    # Generate Markdown Report
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Torq Wings VTOL Commercial Hardware Selection Report\n\n")
        f.write(f"**Generated**: {datetime.datetime.now().isoformat()}\n")
        f.write(f"**Selection Status**: {result.selection_status.value}\n")
        f.write(f"**Total Commercial Hardware Mass**: {result.selected_bom.total_commercial_mass_kg:.3f} kg\n")
        f.write(f"**Total Commercial Hardware Cost**: ${result.selected_bom.total_commercial_cost_usd:.2f} USD\n\n")
        f.write("## Bill of Materials\n\n")
        f.write("| BOM ID | Category | Manufacturer | Model | Qty | Unit Mass | Total Mass | Unit Price | Total Price |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for item in result.selected_bom.items:
            f.write(f"| {item.bom_id} | {item.category.value} | {item.manufacturer} | {item.model} | {item.quantity} | {item.unit_mass_kg:.3f} kg | {item.total_mass_kg:.3f} kg | ${item.unit_price_usd or 0.0:.2f} | ${item.total_price_usd or 0.0:.2f} |\n")
    print(f"[10] EXPORTED MARKDOWN REPORT: {md_path}")

    print("\n" + "=" * 86)
    print("                      PHASE 8 HARDWARE SELECTION COMPLETE                      ")
    print("=" * 86 + "\n")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Torq Wings Studio v2 - VTOL Phase 8 Commercial Hardware Selection & Verification"
    )
    parser.add_argument("--non-interactive", action="store_true", help="Run without user interaction prompts")
    parser.add_argument("--payload", type=float, default=1.5, help="Payload mass in kg (default: 1.5)")
    parser.add_argument("--range", type=float, default=50.0, help="Target range in km (default: 50.0)")
    parser.add_argument("--endurance", type=float, default=60.0, help="Target endurance in min (default: 60.0)")
    parser.add_argument("--speed", type=float, default=75.0, help="Cruise speed in km/h (default: 75.0)")
    parser.add_argument("--category-filter", type=str, default=None, help="Filter output by category substring")
    parser.add_argument("--output-dir", type=str, default="reports", help="Directory for exported reports")

    args = parser.parse_args()
    exit_code = run_hardware_selection_cli(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
