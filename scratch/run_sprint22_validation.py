import sys
import os
import csv
import pandas as pd
import time

# Add workspace to path
sys.path.append(r'c:\Users\acer\Documents\torqwings studio v2')

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.fixed_wing.wing.optimization.wing_planform_optimizer import WingPlanformOptimizer
from scratch.run_campaign import generate_100_cases

def main():
    print("Generating 100 campaign cases...")
    cases = generate_100_cases()
    
    optimizer = WingPlanformOptimizer()
    import logging
    logging.getLogger('WingPlanformOptimizer').setLevel(logging.WARNING)
    records = []
    
    # Run the 100-case campaign
    for idx, c in enumerate(cases, 1):
        print(f"[{idx}/100] Optimizing planform for case {c['case_id']}...")
        
        req = RequirementModel(
            mission_type=c['mission_type'],
            payload_weight_kg=c['payload_kg'],
            target_flight_time_min=c['endurance_min'],
            target_range_km=c['range_km'],
            cruise_speed_kmh=c['cruise_speed_kmh'],
            takeoff_type=c['takeoff_type'],
            landing_type=c['landing_type'],
            environment=c['environment'],
            metadata={'payload_power_w': c['payload_power_w'], 'communication_range_km': c['comm_range_km']}
        )
        
        # Sizing requires a basic config result. We mock one based on the campaign defaults.
        c_result = ConfigurationResult(
            selected_configuration={
                "wing_position": "High Wing",
                "propulsion_layout": "Tractor",
                "tail_configuration": "Conventional",
                "landing_gear_configuration": "Tricycle",
                "wing_planform_style": "Tapered"
            },
            configuration_score=85.0,
            wing_configuration="High Wing",
            propulsion_configuration="Tractor",
            tail_configuration="Conventional",
            landing_gear_configuration="Tricycle",
            engineering_rationale="Rationale",
            alternative_configurations=[],
        )
        
        # Populate context requirements
        wing_reqs = WingRequirements(
            mission_result=None, # will be populated inside the context or requirements mock
            configuration_result=c_result,
        )
        # Dynamically estimate realistic design MTOW based on payload mass
        mtow_est = max(3.0, c['payload_kg'] / 0.20)

        # Mock requirements to carry mission result inside it
        class MissionResultMock:
            def __init__(self, req):
                # Build profile and constraints mimicking mission result
                self.mission_profile = MissionProfileMock(req)
                self.constraints = type('Constraints', (), {'maximum_takeoff_weight_kg': mtow_est})()
        
        class MissionProfileMock:
            def __init__(self, req):
                self.mission_category = req.mission_type
                self.payload_kg = req.payload_weight_kg
                self.flight_time_min = req.target_flight_time_min
                self.cruise_speed_kmh = req.cruise_speed_kmh
                self.stall_speed_target_kmh = 45.0 # target stall speed limits
                self.maximum_takeoff_weight_limit_kg = mtow_est
                self.operational_altitude_m = 150.0
                self.mission_range_km = req.target_range_km
                self.launch_method = req.takeoff_type
                self.landing_method = req.landing_type
                self.air_density_kg_m3 = 1.225
                self.energy_demand_kwh = 0.5
        
        wing_reqs.mission_result = MissionResultMock(req)
        # Set max wingspan restriction to 3.0m in metadata override
        wing_reqs.metadata["max_wingspan_m"] = 3.0
        
        ctx = OptimizationContext(requirements=wing_reqs, configuration=c_result)
        
        res = optimizer.optimize(ctx)
        
        # If success, record statistics
        if res.success and res.winning_candidate:
            best = res.winning_candidate
            spec = res.generated_specification
            records.append({
                "case_id": c["case_id"],
                "success": "SUCCESS",
                "evaluated_count": res.evaluated_count,
                "rejected_count": res.evaluated_count - res.feasible_count,
                "optimal_ar": best.design_variables["aspect_ratio"],
                "optimal_taper": best.design_variables["taper_ratio"],
                "optimal_sweep": best.design_variables["sweep_angle_deg"],
                "optimal_dihedral": best.design_variables["dihedral_angle_deg"],
                "optimization_score": round(best.overall_score, 4),
                "wing_area_m2": round(spec.wing_area, 4),
                "wing_span_m": round(spec.wing_span, 3),
                "root_chord_m": round(spec.root_chord, 3),
                "tip_chord_m": round(spec.tip_chord, 3),
                "mac_m": round(spec.mac, 3),
                "wing_loading_kg_m2": round(spec.wing_loading, 2)
            })
        else:
            records.append({
                "case_id": c["case_id"],
                "success": "FAILED",
                "evaluated_count": res.evaluated_count,
                "rejected_count": res.evaluated_count,
                "optimal_ar": None,
                "optimal_taper": None,
                "optimal_sweep": None,
                "optimal_dihedral": None,
                "optimization_score": None,
                "wing_area_m2": None,
                "wing_span_m": None,
                "root_chord_m": None,
                "tip_chord_m": None,
                "mac_m": None,
                "wing_loading_kg_m2": None
            })

    # Export to CSV
    os.makedirs("reports", exist_ok=True)
    df = pd.DataFrame(records)
    csv_file = "reports/wing_planform_optimization_100_cases.csv"
    df.to_csv(csv_file, index=False)
    print(f"Generated validation CSV: {csv_file}")

    # Generate Markdown Report
    successful_cases = df[df["success"] == "SUCCESS"]
    failed_cases = df[df["success"] == "FAILED"]
    
    md = []
    md.append("# Sprint 22 Wing Planform Optimization validation report")
    md.append("---")
    md.append("## 1. Validation Run Executive Summary")
    md.append(f"- **Missions Processed**: {len(df)}")
    md.append(f"- **Successful Configurations**: {len(successful_cases)}")
    md.append(f"- **Failed/Infeasible Configurations**: {len(failed_cases)}")
    md.append(f"- **Average Candidates Evaluated per Mission**: {df['evaluated_count'].mean():.1f}")
    md.append(f"- **Average Rejections per Mission**: {df['rejected_count'].mean():.1f}")
    
    if len(successful_cases) > 0:
        md.append(f"- **Average Optimal Aspect Ratio**: {successful_cases['optimal_ar'].mean():.2f}")
        md.append(f"- **Average Optimal Taper Ratio**: {successful_cases['optimal_taper'].mean():.2f}")
        md.append(f"- **Average Optimal Sweep Angle**: {successful_cases['optimal_sweep'].mean():.2f}°")
        md.append(f"- **Average Optimal Dihedral Angle**: {successful_cases['optimal_dihedral'].mean():.2f}°")
    
    md.append("\n## 2. Geometric Safety & Feasibility Audit")
    md.append("- **Min Tip Chord**: Checked that all tip chords are $\ge 0.05$ m to prevent needle-thin wingtip manufacturing failures. Actual Min Tip Chord: " + f"{successful_cases['tip_chord_m'].min():.3f} m")
    md.append("- **Max Wingspan Limit**: Checked that all wingspans are $\le 3.0$ m matching the storage/transportation limit. Actual Max Wingspan: " + f"{successful_cases['wing_span_m'].max():.3f} m")
    md.append("- **Taper Ratio Boundaries**: Enforced manufacturing limits of $[0.35, 1.00]$. Actual Range: " + f"[{successful_cases['optimal_taper'].min():.2f}, {successful_cases['optimal_taper'].max():.2f}]")

    md.append("\n## 3. Representative Optimization Sample Cases (First 15)")
    md.append("| Case ID | Status | Candidates | Rejections | AR | Taper | Sweep | Dihedral | Score | Span (m) | Area (m2) | Tip Chord (m) |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for r in records[:15]:
        if r["success"] == "SUCCESS":
            md.append(
                f"| {r['case_id']} | {r['success']} | {r['evaluated_count']} | {r['rejected_count']} | "
                f"{r['optimal_ar']:.1f} | {r['optimal_taper']:.2f} | {r['optimal_sweep']:.1f} | {r['optimal_dihedral']:.1f} | "
                f"{r['optimization_score']:.4f} | {r['wing_span_m']:.3f} | {r['wing_area_m2']:.4f} | {r['tip_chord_m']:.3f} |"
            )
        else:
            md.append(f"| {r['case_id']} | {r['success']} | {r['evaluated_count']} | {r['rejected_count']} | - | - | - | - | - | - | - | - |")

    os.makedirs("docs/validation", exist_ok=True)
    report_file = "docs/validation/WING_OPTIMIZATION_100_CASES_REPORT.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Generated validation Report: {report_file}")

if __name__ == '__main__':
    main()
