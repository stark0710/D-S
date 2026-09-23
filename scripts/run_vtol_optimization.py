#!/usr/bin/env python3
"""
Torq Wings Studio v2 - VTOL Phase 7 Optimization CLI.

Purpose:
    Dedicated CLI entry point for Multidisciplinary Optimization & Pareto Analysis.
    Supports interactive and non-interactive execution, variable bounds, grid
    resolution, objective selection, terminal summaries, and JSON/Markdown report export.
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

from backend.design.vtol.optimization import (
    VTOLOptimizationPipeline,
    DesignCandidate,
    OptimizationVariable,
    STANDARD_VTOL_VARIABLES,
    STANDARD_OBJECTIVES,
    STANDARD_CONSTRAINTS,
    OptimizationStatus,
    EvaluationStatus,
    OptimizationProvenance,
)


def print_banner() -> None:
    print("=" * 82)
    print("       TORQ WINGS STUDIO v2 — VTOL MULTIDISCIPLINARY OPTIMIZATION & PARETO       ")
    print("               Phase 7 Authoritative Engineering Optimization Layer              ")
    print("=" * 82)


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Formats a clean monospace table for terminal output."""
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


def run_optimization_cli(args: argparse.Namespace) -> int:
    print_banner()

    print("\n[1] CONFIGURING SEARCH SPACE & VARIABLES")
    # Base mission parameters
    base_mission = {
        "payload_mass": args.payload,
        "target_range": args.range,
        "target_flight_time": args.endurance,
        "cruise_speed": args.speed,
    }

    # Define active variables
    var_payload = OptimizationVariable(
        name="payload_mass_kg",
        base_value=args.payload,
        min_bound=max(0.5, args.payload * 0.7),
        max_bound=args.payload * 1.3,
        units="kg",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
        is_active=True,
        description="Mission payload carrying capacity",
    )
    var_speed = OptimizationVariable(
        name="cruise_speed_kmh",
        base_value=args.speed,
        min_bound=max(60.0, args.speed * 0.85),
        max_bound=args.speed * 1.15,
        units="km/h",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
        is_active=True,
        description="Forward cruise aerodynamic airspeed",
    )

    active_vars = [var_payload, var_speed]
    print(f"  * Variable 1: {var_payload.name} [{var_payload.min_bound:.2f} .. {var_payload.max_bound:.2f} {var_payload.units}] (Provenance: {var_payload.provenance.value})")
    print(f"  * Variable 2: {var_speed.name} [{var_speed.min_bound:.1f} .. {var_speed.max_bound:.1f} {var_speed.units}] (Provenance: {var_speed.provenance.value})")
    print(f"  * Resolution: {args.grid_resolution} points per variable ({args.grid_resolution ** len(active_vars)} candidates total)")

    print("\n[2] OBJECTIVES")
    objectives = [
        STANDARD_OBJECTIVES["mtow_kg"],
        STANDARD_OBJECTIVES["endurance_min"],
        STANDARD_OBJECTIVES["total_mission_energy_wh"],
    ]
    for obj in objectives:
        print(f"  * {obj.direction.value:<8} : {obj.name:<25} [{obj.units}] (Provenance: {obj.provenance})")

    print("\n[3] HARD ENGINEERING CONSTRAINTS")
    constraints = list(STANDARD_CONSTRAINTS.values())
    for con in constraints:
        bound_str = ""
        if con.lower_bound is not None and con.upper_bound is not None:
            bound_str = f"[{con.lower_bound} .. {con.upper_bound} {con.units}]"
        elif con.lower_bound is not None:
            bound_str = f">= {con.lower_bound} {con.units}"
        prov_str = con.provenance.value if hasattr(con.provenance, "value") else str(con.provenance)
        print(f"  * {con.name:<28} : {bound_str:<22} (Provenance: {prov_str})")

    print("\n[4] EXECUTING DETERMINISTIC MULTIDISCIPLINARY SWEEP...")
    pipeline = VTOLOptimizationPipeline(
        variables=active_vars,
        objectives=objectives,
        constraints=constraints,
    )

    result = pipeline.run_optimization(
        active_variables=active_vars,
        objectives=objectives,
        constraints=constraints,
        search_method="CARTESIAN_GRID",
        resolution_per_var=args.grid_resolution,
        base_mission_overrides=base_mission,
    )

    print("\n" + "=" * 82)
    print("                           OPTIMIZATION SUMMARY                           ")
    print("=" * 82)
    print(f"  Optimization Status    : {result.optimization_status.value}")
    print(f"  Search Method          : {result.search_method}")
    print(f"  Total Candidates       : {result.total_candidates}")
    print(f"  Evaluated Unique       : {result.evaluated_candidates}")
    print(f"  Deduplication Hits     : {result.cached_evaluations}")
    print(f"  Feasible Candidates    : {result.feasible_count}")
    print(f"  Infeasible Candidates  : {result.infeasible_count}")
    print(f"  Calculation Errors     : {result.error_count}")
    print(f"  Dominated Candidates   : {result.dominated_count}")
    print(f"  Pareto-Optimal Front   : {result.pareto_count}")
    print(f"  Runtime Elapsed        : {result.evaluation_metadata.get('runtime_seconds', 0.0):.3f} s")

    if result.pareto_front:
        print("\n[5] PARETO FRONT CANDIDATES (Non-Dominated Feasible Designs)")
        table_headers = [
            "Candidate ID",
            "Payload (kg)",
            "Speed (km/h)",
            "MTOW (kg)",
            "Endurance (min)",
            "Energy (Wh)",
            "SM (% MAC)",
            "Trim (deg)",
        ]
        table_rows = []
        for cand in result.pareto_front:
            table_rows.append([
                cand.candidate_id,
                f"{cand.payload_mass_kg:.2f}",
                f"{cand.cruise_speed_kmh:.1f}",
                f"{cand.mtow_kg:.3f}",
                f"{cand.endurance_min:.1f}",
                f"{cand.total_mission_energy_wh:.1f}",
                f"{cand.static_margin_pct:+.2f}%",
                f"{cand.cruise_trim_elevator_deg:+.2f}°",
            ])
        print(format_table(table_headers, table_rows))

        print("\n[6] BEST-BY-OBJECTIVE DESCRIPTIVE VIEWS")
        for obj_name, cand in result.best_by_objective.items():
            val = cand.objectives.get(obj_name, 0.0)
            print(f"  * Best {obj_name:<25}: {val:.3f} (Candidate {cand.candidate_id}, MTOW={cand.mtow_kg:.3f} kg)")

    if result.warnings:
        print("\n[7] SYSTEM WARNINGS")
        for w in result.warnings:
            print(f"  ! {w}")

    print("\n[8] DEFERRED SCOPE BOUNDARIES")
    for d in result.deferred_items:
        print(f"  - {d}")

    # Export reports if requested
    out_dir = args.output_dir
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = os.path.join(out_dir, f"vtol_optimization_result_{ts}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"\n[OK] Exported JSON artifact: {json_path}")

    md_path = os.path.join(out_dir, f"vtol_optimization_summary_{ts}.md")
    md_content = f"""# Torq Wings VTOL Phase 7 Multidisciplinary Optimization Summary

- **Timestamp**: {datetime.datetime.now().isoformat()}
- **Status**: `{result.optimization_status.value}`
- **Search Method**: `{result.search_method}`
- **Total Candidates**: {result.total_candidates}
- **Evaluated**: {result.evaluated_candidates}
- **Deduplicated Cache Hits**: {result.cached_evaluations}
- **Feasible**: {result.feasible_count}
- **Infeasible**: {result.infeasible_count}
- **Pareto-Optimal Count**: {result.pareto_count}

## Non-Dominated Pareto Front
"""
    if result.pareto_front:
        md_content += "| Candidate ID | Payload (kg) | Speed (km/h) | MTOW (kg) | Endurance (min) | Energy (Wh) | Static Margin | Trim |\n"
        md_content += "|---|---|---|---|---|---|---|---|\n"
        for cand in result.pareto_front:
            md_content += f"| {cand.candidate_id} | {cand.payload_mass_kg:.2f} | {cand.cruise_speed_kmh:.1f} | {cand.mtow_kg:.3f} | {cand.endurance_min:.1f} | {cand.total_mission_energy_wh:.1f} | {cand.static_margin_pct:+.2f}% MAC | {cand.cruise_trim_elevator_deg:+.2f}° |\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[OK] Exported Markdown report: {md_path}")

    print("\n" + "=" * 82)
    print("                    PHASE 7 OPTIMIZATION EXECUTION COMPLETE               ")
    print("=" * 82)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Torq Wings VTOL Phase 7 Multidisciplinary Optimization & Pareto Analysis CLI"
    )
    parser.add_argument("--non-interactive", action="store_true", default=True, help="Run without terminal prompts")
    parser.add_argument("--payload", type=float, default=2.5, help="Payload mass (kg)")
    parser.add_argument("--range", type=float, default=35.0, help="Cruise range (km)")
    parser.add_argument("--endurance", type=float, default=25.0, help="Flight endurance (min)")
    parser.add_argument("--speed", type=float, default=85.0, help="Cruise speed (km/h)")
    parser.add_argument("--grid-resolution", type=int, default=3, help="Sampling resolution per active variable")
    parser.add_argument("--output-dir", type=str, default="reports", help="Output directory for reports")

    args = parser.parse_args()
    return run_optimization_cli(args)


if __name__ == "__main__":
    sys.exit(main())
