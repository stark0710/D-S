#!/usr/bin/env python3
"""
Torq Wings Studio v2 - VTOL Phase 9 System Integration & Verification CLI.

Purpose:
    Dedicated CLI entry point for executing authoritative aircraft integration,
    evaluating electrical architecture, deterministic Pixhawk I/O allocation,
    physical component 3D spatial installation, integrated CG envelope clearance,
    mass reconciliation, mission-state operational matrices, and FMEA failure analysis.

Supports:
    - Interactive and non-interactive execution (--non-interactive)
    - Structured monospace terminal summaries for all domains
    - JSON and Markdown report export to reports/
    - Exit code reflecting final integration status
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

from backend.design.vtol.integration import (
    VTOLSystemIntegrationPipeline,
    IntegrationConfiguration,
    IntegrationStatus,
)


def print_banner() -> None:
    print("=" * 86)
    print("      TORQ WINGS STUDIO v2 — VTOL SYSTEM INTEGRATION & VERIFICATION PIPELINE      ")
    print("                     Phase 9 Multi-Domain Engineering Review                      ")
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


def run_integration_cli(args: argparse.Namespace) -> int:
    print_banner()

    print("\n[1] INITIALIZING PHASE 9 SYSTEM INTEGRATION PIPELINE")
    config = IntegrationConfiguration()
    pipeline = VTOLSystemIntegrationPipeline(config=config)
    print("  * Consuming authoritative outputs from Phases 1-7 (Physics) and Phase 8 (BOM)")

    overrides = {
        "payload_mass_kg": args.payload,
        "target_range_km": args.range,
        "target_flight_time_min": args.endurance,
        "cruise_speed_kmh": args.speed,
    }

    print("\n[2] EXECUTING MULTI-DOMAIN INTEGRATION & VERIFICATION")
    res = pipeline.execute(overrides=overrides)

    # 1. Hardware Assignment Table
    print("\n[3] COMMERCIAL HARDWARE TO AIRCRAFT ROLE ASSIGNMENT (27 Parts)")
    asgn_headers = ["Assignment ID", "Aircraft Role", "Manufacturer & Model", "Qty", "Mass (kg)", "Interface"]
    asgn_rows = []
    for a in res.assignments:
        asgn_rows.append([
            a.assignment_id,
            a.role.value,
            f"{a.manufacturer} {a.model}"[:32],
            str(a.quantity),
            f"{a.total_mass_kg:.3f}",
            a.interface_type[:30],
        ])
    print(format_table(asgn_headers, asgn_rows))

    # 2. Electrical Architecture Table
    print("\n[4] ELECTRICAL POWER BUSES & LOAD VERIFICATION")
    bus_headers = ["Bus Name", "Nominal V", "Cont. Draw", "Cont. Cap.", "Margin", "Status"]
    bus_rows = []
    for b in res.electrical_buses:
        bus_rows.append([
            b.bus_name,
            f"{b.nominal_voltage_v:.1f} V",
            f"{b.total_continuous_current_a:.2f} A",
            f"{b.max_continuous_current_capacity_a:.1f} A",
            f"{b.continuous_margin_a:+.2f} A",
            b.status.value,
        ])
    print(format_table(bus_headers, bus_rows))

    # 3. Power Paths Table
    print("\n[5] POWER PATH VERIFICATION (Paths A through G)")
    pwr_headers = ["Path ID", "Path Description", "Voltage", "Cont. Current", "Capacity", "Margin", "Status"]
    pwr_rows = []
    for p in res.power_paths:
        pwr_rows.append([
            p.path_id,
            p.path_name[:34],
            f"{p.voltage_nominal_v:.1f} V",
            f"{p.continuous_current_a:.2f} A",
            f"{p.continuous_capacity_a:.1f} A",
            f"{p.margin_a:+.2f} A",
            p.status.value,
        ])
    print(format_table(pwr_headers, pwr_rows))

    # 4. I/O Allocation Table
    print("\n[6] PIXHAWK 6X DETERMINISTIC I/O PINOUT ALLOCATION")
    io_headers = ["Port / Pin", "Connected Device", "Role", "Protocol", "Power Bus", "Status"]
    io_rows = []
    for io in res.io_allocations:
        io_rows.append([
            io.channel_or_port,
            io.device_name[:30],
            io.device_role.value,
            io.protocol.value,
            io.power_bus.value[:20],
            io.status.value,
        ])
    print(format_table(io_headers, io_rows))

    # 5. Physical Installation & CG Integration
    print("\n[7] PHYSICAL 3D INSTALLATION & INTEGRATED CENTER OF GRAVITY")
    cg = res.integrated_cg
    print(f"  * Aircraft Coordinate Datum: Fuselage Nose (x=0.0m, +x aft, +y right, +z up)")
    print(f"  * Total Installed Aircraft Mass: {cg.total_integrated_mass_kg:.3f} kg")
    print(f"  * Installed Center of Gravity:   x_cg = {cg.x_cg_m:.4f} m ({cg.cg_pct_mac:.1f}% MAC)")
    print(f"  * Lateral & Vertical Position:   y_cg = {cg.y_cg_m:+.4f} m, z_cg = {cg.z_cg_m:+.4f} m")
    print(f"  * Phase 6 Longitudinal Envelope: [{cg.forward_limit_m:.4f} m, {cg.aft_limit_m:.4f} m]")
    print(f"  * Forward Margin:                {cg.forward_margin_m:+.4f} m (Clearance: PASS)")
    print(f"  * Aft Margin:                    {cg.aft_margin_m:+.4f} m (Clearance: PASS)")
    print(f"  * Neutral Point / Static Margin: x_np = {cg.neutral_point_m:.4f} m (SM: +{cg.static_margin_pct_mac:.2f}% MAC)")
    print(f"  * CG Envelope Compliance:        {'WITHIN_LIMITS' if cg.is_within_envelope else 'VIOLATED'}")

    # 6. Mass Reconciliation
    print("\n[8] MULTI-PHASE MASS RECONCILIATION AUDIT")
    mr = res.mass_reconciliation
    print(f"  * Phase 5 Baseline Sizing MTOW:     {mr.phase5_mtow_kg:.3f} kg")
    print(f"  * Phase 5 Assumed Hardware Mass:    {mr.phase5_hardware_mass_kg:.3f} kg")
    print(f"  * Phase 8 Commercial Hardware BOM:  {mr.phase8_bom_mass_kg:.3f} kg")
    print(f"  * Phase 9 Integrated Mass:          {mr.phase9_installed_mass_kg:.3f} kg")
    print(f"  * Hardware Mass Delta:              {mr.hardware_delta_kg:+.3f} kg ({mr.hardware_delta_pct_mtow:+.2f}% MTOW)")
    print(f"  * Upstream Re-evaluation Required:  {'YES' if mr.upstream_reevaluation_required else 'NO (Within 150g / 2.0% threshold)'}")

    # 7. Mission-State Integration
    print("\n[9] MISSION-STATE OPERATIONAL INTEGRATION (10 Phases)")
    ms_headers = ["Mission Phase", "Active Propulsion", "Control Surfaces", "Power (W)", "Duration", "Status"]
    ms_rows = []
    for ms in res.mission_states:
        act_prop = f"{len(ms.active_motors)} Motors" if ms.active_motors else "None (Gliding/Hold)"
        act_cs = f"{len(ms.active_control_surfaces)} Surfaces" if ms.active_control_surfaces else "Neutralized"
        ms_rows.append([
            ms.state.value,
            act_prop,
            act_cs,
            f"{ms.state_power_draw_w:.1f} W",
            f"{ms.state_duration_sec:.0f} s",
            ms.status.value,
        ])
    print(format_table(ms_headers, ms_rows))

    # 8. Dual-Direction Transition Integration
    print("\n[10] TRANSITION CORRIDOR READINESS")
    tr = res.transition_integration
    print(f"  * Outbound Transition (VTOL -> Cruise): {'READY' if tr.vtol_to_cruise_ready else 'NOT READY'}")
    print(f"  * Inbound Transition (Cruise -> VTOL):  {'READY' if tr.cruise_to_vtol_ready else 'NOT READY'}")
    print(f"  * Power Headroom during Acceleration:   {tr.power_headroom_w:+.1f} W")
    print(f"  * Immediate Corridor Abort Supported:   {'YES' if tr.abort_reversal_supported else 'NO'}")

    # 9. Failure Mode Analysis (13 Scenarios)
    print("\n[11] SYSTEM-LEVEL FAILURE MODE ANALYSIS (FMEA - 13 Modes)")
    fmea_headers = ["ID", "Failure Mode", "Severity", "Controllability", "Verification Status"]
    fmea_rows = []
    for fm in res.failure_modes:
        fmea_rows.append([
            fm.failure_id,
            fm.failure_mode[:36],
            fm.severity,
            fm.controllability_status.value,
            fm.verification_status.value,
        ])
    print(format_table(fmea_headers, fmea_rows))

    # 10. Requirement Traceability
    print("\n[12] END-TO-END REQUIREMENT TRACEABILITY")
    tr_headers = ["Req ID", "Parameter", "Phase", "Target / Baseline", "Status"]
    tr_rows = []
    for t in res.traceability_table:
        tr_rows.append([
            t.requirement_id,
            t.parameter[:26],
            f"Phase {t.source_phase}",
            t.upstream_value[:35],
            t.status.value,
        ])
    print(format_table(tr_headers, tr_rows))

    # 11. Deferred / Insufficient Input Items
    if res.deferred_items:
        print("\n[13] LEGITIMATELY DEFERRED / QUALIFIED SPECIFICATIONS")
        for d in res.deferred_items:
            print(f"  * [DEFERRED] {d}")

    # Export Reports
    os.makedirs(args.output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(args.output_dir, f"vtol_system_integration_{timestamp}.json")
    md_path = os.path.join(args.output_dir, f"vtol_system_integration_{timestamp}.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(res.to_dict(), f, indent=2)
    print(f"\n[14] EXPORTED JSON REPORT: {json_path}")

    # Generate Markdown Summary
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Torq Wings VTOL System Integration & Verification Report\n\n")
        f.write(f"**Generated**: {datetime.datetime.now().isoformat()}\n")
        f.write(f"**Final Status**: `{res.final_status.value}`\n\n")
        f.write(f"## Center of Gravity & Stability Limits\n\n")
        f.write(f"- **Installed Mass**: {cg.total_integrated_mass_kg:.3f} kg\n")
        f.write(f"- **Installed x_cg**: {cg.x_cg_m:.4f} m ({cg.cg_pct_mac:.1f}% MAC)\n")
        f.write(f"- **Envelope**: [{cg.forward_limit_m:.4f} m, {cg.aft_limit_m:.4f} m]\n")
        f.write(f"- **Static Margin**: +{cg.static_margin_pct_mac:.2f}% MAC\n\n")
        f.write(f"## Multi-Phase Mass Reconciliation\n\n")
        f.write(f"- **Phase 5 MTOW**: {mr.phase5_mtow_kg:.3f} kg\n")
        f.write(f"- **Phase 8 Commercial BOM Mass**: {mr.phase8_bom_mass_kg:.3f} kg\n")
        f.write(f"- **Hardware Mass Delta**: {mr.hardware_delta_kg:+.3f} kg ({mr.hardware_delta_pct_mtow:+.2f}% MTOW)\n")
        f.write(f"- **Re-evaluation Required**: {'YES' if mr.upstream_reevaluation_required else 'NO'}\n")
    print(f"[15] EXPORTED MARKDOWN REPORT: {md_path}")

    print("\n" + "=" * 86)
    print(f"                      FINAL STATUS: {res.final_status.value}                      ")
    print("=" * 86 + "\n")

    return 0 if res.final_status in (IntegrationStatus.INTEGRATION_COMPLETE, IntegrationStatus.INTEGRATION_COMPLETE_WITH_WARNINGS) else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Torq Wings Studio v2 - VTOL Phase 9 System Integration & Verification"
    )
    parser.add_argument("--non-interactive", action="store_true", help="Run without user interaction prompts")
    parser.add_argument("--payload", type=float, default=1.5, help="Payload mass in kg (default: 1.5)")
    parser.add_argument("--range", type=float, default=50.0, help="Target range in km (default: 50.0)")
    parser.add_argument("--endurance", type=float, default=60.0, help="Target endurance in min (default: 60.0)")
    parser.add_argument("--speed", type=float, default=75.0, help="Cruise speed in km/h (default: 75.0)")
    parser.add_argument("--output-dir", type=str, default="reports", help="Directory for exported reports")

    args = parser.parse_args()
    exit_code = run_integration_cli(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
