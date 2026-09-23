"""
Torq Wings Studio v2 — Phase 10 Flight Control Configuration & ArduPilot Integration CLI.

Usage:
    python scripts/run_vtol_flight_control.py

Outputs:
    - Formatted terminal report
    - JSON artifact: reports/vtol_flight_control_<timestamp>.json
    - Markdown report: reports/vtol_flight_control_<timestamp>.md
"""

from __future__ import annotations
import datetime
import json
import os
import sys

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.design.vtol.flight_control import (
    FinalVerdictStatus,
    FlightControlStatus,
    GroundTestReadiness,
    VTOLFlightControlPipeline,
)


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Formats ASCII table with clean column widths."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_str = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |"

    lines = [sep, header_str, sep]
    for row in rows:
        line = "| " + " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)) + " |"
        lines.append(line)
    lines.append(sep)
    return "\n".join(lines)


def main() -> int:
    print("=" * 86)
    print("      TORQ WINGS -- PHASE 10 VTOL FLIGHT CONTROL & ARDUPILOT INTEGRATION")
    print("=" * 86)

    pipeline = VTOLFlightControlPipeline()
    res = pipeline.execute()

    print(f"\n[1] PLATFORM ARCHITECTURE & CONTROLLER")
    print(f"  * Aircraft:          {res.aircraft_name}")
    print(f"  * Flight Controller: {res.flight_controller}")
    print(f"  * Autopilot:         {res.autopilot}")
    print(f"  * Propulsion Frame:  QuadPlane (4 Dedicated Lift Motors + 1 Forward Pusher)")
    print(f"  * Aerodynamics:      2 Outboard Ailerons + 2 Inverted V-Tail Ruddervator Surfaces")

    # 2. Output and Actuator Mapping Table
    print("\n[2] PIXHAWK 6X OUTPUT / ACTUATOR PINOUT MAPPING (Channels 1 - 10)")
    motor_headers = ["Out Ch", "Assigned Role", "Physical Location", "Protocol", "Hardware Model", "Direction Status"]
    motor_rows = []
    for m in res.motor_outputs:
        motor_rows.append([
            f"PWM_{m.output_channel}",
            m.assigned_role,
            m.physical_position[:30],
            m.protocol.value,
            m.hardware_motor[:22],
            m.direction_verification_status.value,
        ])
    for s in res.servo_outputs:
        motor_rows.append([
            f"PWM_{s.output_channel}",
            s.surface_name[:20],
            "Empennage / Wing",
            s.protocol.value,
            s.hardware_servo[:22],
            s.direction_verification_status.value,
        ])
    print(format_table(motor_headers, motor_rows))

    # 3. Hardware Identity Reconciliation
    print("\n[3] HARDWARE IDENTITY RECONCILIATION AUDIT (Phase 8 BOM vs Phase 9 References)")
    hw_headers = ["Role", "Phase 8 BOM Selection", "Phase 9 Reference", "Discrepancy / Status", "Verdict"]
    hw_rows = []
    for h in res.hardware_reconciliation:
        hw_rows.append([
            h.component_role,
            f"{h.phase8_bom_selection[:24]} ({h.phase8_bom_id})",
            f"{h.phase9_integration_reference[:24]} ({h.phase9_report_bom_id})",
            h.discrepancy_type[:24],
            h.reconciliation_verdict.value,
        ])
    print(format_table(hw_headers, hw_rows))

    # 4. Sensor Interface Table
    print("\n[4] SENSOR DRIVERS & BUS INTERFACES")
    sn_headers = ["Sensor Function", "Hardware Model", "Bus Interface", "ArduPilot Parameter", "Status"]
    sn_rows = []
    for sn in res.sensors:
        sn_rows.append([
            sn.sensor_name[:24],
            sn.hardware_component[:24],
            sn.bus_interface[:20],
            sn.ardupilot_driver_param[:24],
            sn.configuration_status.value,
        ])
    print(format_table(sn_headers, sn_rows))

    # 5. Flight Modes Table
    print("\n[5] ARDUPILOT QUADPLANE OPERATIONAL FLIGHT MODES")
    fm_headers = ["Mode Name", "Code", "Primary Propulsion Authority", "Control Surface Authority", "Status"]
    fm_rows = []
    for fm in res.flight_modes:
        fm_rows.append([
            fm.mode_name,
            str(fm.mode_code),
            fm.propulsion_authority[:30],
            fm.control_surface_authority[:30],
            fm.configuration_status.value,
        ])
    print(format_table(fm_headers, fm_rows))

    # 6. Failsafe Matrix Summary
    print("\n[6] FAILSAFE SCENARIOS (15 Mandatory Conditions)")
    fs_headers = ["Scenario ID", "Failure Mode Name", "Configured Action", "Fallback Mode", "Status"]
    fs_rows = []
    for fs in res.failsafes:
        fs_rows.append([
            fs.scenario_id,
            fs.failure_name[:28],
            fs.configured_response.value,
            fs.fallback_mode[:28],
            fs.controllability_status.value,
        ])
    print(format_table(fs_headers, fs_rows))

    # 7. Ground-Test Checklist
    print("\n[7] PRE-FLIGHT GROUND BENCH TEST CHECKLIST (Prompt Section 25)")
    gt_headers = ["Test ID", "Test Name", "Target Subsystem", "Execution Status"]
    gt_rows = []
    for gt in res.ground_test_checklist[:10]:  # Show first 10
        gt_rows.append([
            gt.test_id,
            gt.test_name[:36],
            gt.subsystem[:28],
            gt.execution_status.value,
        ])
    print(format_table(gt_headers, gt_rows))
    print(f"  * (Showing 10 of {len(res.ground_test_checklist)} ground-test checklist tasks; all marked NOT_EXECUTED)")

    # 8. Summary & Verdict
    print("\n" + "=" * 86)
    print("PHASE 10 — VTOL FLIGHT CONTROL SUMMARY")
    print("=" * 86)
    print(f"Architecture:          QuadPlane / Lift + Cruise")
    print(f"Flight Controller:     Holybro Pixhawk 6X")
    print(f"Autopilot:             ArduPilot Plane / QuadPlane")
    print(f"Lift Motors:           4 (Spedix GS40A ESCs / DShot600)")
    print(f"Cruise Motor:          1 (Skywalker 40A V2 / PWM)")
    print(f"Outputs:               {'VALIDATED' if res.verification.output_mapping_passed else 'CONFLICT'}")
    print(f"Sensors:               {'VALIDATED' if res.verification.sensor_mapping_passed else 'CONFLICT'}")
    print(f"Failsafes:             {'VALIDATED' if res.verification.failsafe_matrix_passed else 'CONFLICT'}")
    print(f"Transition:            CONFIGURED / DEFERRED (18s duration, 18.06 m/s stall threshold)")
    print(f"Hardware Identity:     {'CONSISTENT' if res.verification.hardware_reconciliation_passed else 'HARDWARE_IDENTITY_RECONCILIATION_REQUIRED'}")
    print(f"Ground-Test Readiness: {res.ground_test_readiness.value}")
    print(f"Flight-Test Status:    NOT_EXECUTED (Physical flight testing not established)")
    print(f"Overall Status:        {res.final_verdict.value}")
    print("=" * 86)

    # 9. Export Reports
    os.makedirs(os.path.join(PROJECT_ROOT, "reports"), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(PROJECT_ROOT, "reports", f"vtol_flight_control_{timestamp}.json")
    md_path = os.path.join(PROJECT_ROOT, "reports", f"vtol_flight_control_{timestamp}.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(res.to_dict(), f, indent=2)
    print(f"\n[+] Exported JSON report: {json_path}")

    # Generate Markdown summary
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Torq Wings Phase 10 Flight Control Configuration Report\n")
        f.write(f"Generated: {datetime.datetime.now().isoformat()}\n\n")
        f.write(f"- **Final Verdict**: `{res.final_verdict.value}`\n")
        f.write(f"- **Ground-Test Readiness**: `{res.ground_test_readiness.value}`\n")
        f.write(f"- **Total Parameters**: `{len(res.parameters)}`\n")
        f.write(f"- **Hardware Conflicts**: `{'Yes - Reconciliation Required' if not res.verification.hardware_reconciliation_passed else 'None'}`\n")
    print(f"[+] Exported Markdown report: {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
