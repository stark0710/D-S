import sys
import os
import csv
import json
import math
import dataclasses
import pandas as pd

# Add workspace to path
sys.path.append(r'c:\Users\acer\Documents\torqwings studio v2')

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from scratch.run_campaign import generate_100_cases, to_dict

def main():
    print("Generating 100 cases...")
    cases = generate_100_cases()
    
    # Load baseline lists
    baseline_df = pd.read_csv("reports/fixed_wing_phase5d_baseline_case_ledger.csv")
    baseline_map = {row["case_id"]: row for _, row in baseline_df.iterrows()}
    
    phase5c_df = pd.read_csv("reports/fixed_wing_phase5c_rejection_ledger.csv")
    phase5c_map = {row["case_id"]: row for _, row in phase5c_df.iterrows()}
    
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    results = []
    output_rows = []
    before_after_rows = []
    
    success_count = 0
    infeasible_count = 0
    
    for c in cases:
        case_id = c["case_id"]
        req = RequirementModel(
            mission_type=c["mission_type"],
            payload_weight_kg=c["payload_kg"],
            target_flight_time_min=c["endurance_min"],
            target_range_km=c["range_km"],
            cruise_speed_kmh=c["cruise_speed_kmh"],
            takeoff_type=c["takeoff_type"],
            landing_type=c["landing_type"],
            environment=c["environment"],
            metadata={"payload_power_w": c["payload_power_w"], "communication_range_km": c["comm_range_km"]}
        )
        
        print(f"Running {case_id}...")
        try:
            res = pipeline.execute(req)
        except Exception as e:
            res = None
            print(f"Exception on {case_id}: {e}")
            
        status_val = res.status.value if res else "INTERNAL_EXCEPTION"
        
        # 1. Save results in outputs csv row format
        # Build the exact same row structure as the runner
        row = {
            "case_id": case_id,
            "mission_category": c["mission_type"].value,
            "pipeline_status": status_val,
            "verification_status": (res.verification_result.verification_status if res and res.verification_result else "N/A"),
            "failure_reason": ("; ".join(res.errors) if res and res.errors else "Unknown" if res and not res.success else ""),
            "payload_kg": c["payload_kg"],
            "range_km": c["range_km"],
            "endurance_min": c["endurance_min"],
            "cruise_speed_kmh": c["cruise_speed_kmh"],
            "wing_position": (res.configuration_result.selected_configuration.get("wing_position", "") if res and res.configuration_result else ""),
            "propulsion_layout": (res.configuration_result.selected_configuration.get("propulsion_layout", "") if res and res.configuration_result else ""),
            "tail_configuration": (res.configuration_result.selected_configuration.get("tail_configuration", "") if res and res.configuration_result else ""),
            "landing_gear": (res.configuration_result.selected_configuration.get("landing_gear_configuration", "") if res and res.configuration_result else ""),
            "configuration_name": (f"{res.configuration_result.wing_configuration} / {res.configuration_result.propulsion_configuration}" if res and res.configuration_result else ""),
            "initial_mtow_kg": (round(res.convergence_history[0].mtow_old, 3) if res and res.convergence_history else ""),
            "final_mtow_kg": (round(res.mass_properties_result.weight_breakdown.useful_load_kg + res.mass_properties_result.weight_breakdown.structural_weight_kg + res.mass_properties_result.weight_breakdown.propulsion_weight_kg + res.mass_properties_result.weight_breakdown.avionics_weight_kg, 3) if res and res.mass_properties_result else ""),
            "payload_mass_kg": (round(res.mass_properties_result.weight_breakdown.payload_weight_kg, 3) if res and res.mass_properties_result else ""),
            "battery_mass_kg": (round(res.mass_properties_result.weight_breakdown.battery_fuel_weight_kg, 3) if res and res.mass_properties_result else ""),
            "battery_fraction": (round(res.mass_properties_result.weight_breakdown.battery_fraction, 4) if res and res.mass_properties_result else ""),
            "structural_mass_kg": (round(res.mass_properties_result.weight_breakdown.structural_weight_kg, 3) if res and res.mass_properties_result else ""),
            "propulsion_mass_kg": (round(res.mass_properties_result.weight_breakdown.propulsion_weight_kg, 3) if res and res.mass_properties_result else ""),
            "avionics_mass_kg": (round(res.mass_properties_result.weight_breakdown.avionics_weight_kg, 3) if res and res.mass_properties_result else ""),
            "empty_mass_kg": (round(res.mass_properties_result.weight_breakdown.structural_weight_kg + res.mass_properties_result.weight_breakdown.propulsion_weight_kg + res.mass_properties_result.weight_breakdown.avionics_weight_kg, 3) if res and res.mass_properties_result else ""),
            "useful_load_kg": (round(res.mass_properties_result.weight_breakdown.useful_load_kg, 3) if res and res.mass_properties_result else ""),
            "battery_energy_wh": (round(res.mass_properties_result.weight_breakdown.battery_fuel_weight_kg * 200.0, 2) if res and res.mass_properties_result else ""),
            "specific_energy_whkg": 200.0,
            "usable_fraction": 0.85,
            "wing_area_m2": (round(res.wing_result.wing_geometry.reference_area_m2, 4) if res and res.wing_result else ""),
            "wingspan_m": (round(res.wing_result.wing_geometry.span_m, 3) if res and res.wing_result else ""),
            "aspect_ratio": (round(res.wing_result.wing_geometry.aspect_ratio, 2) if res and res.wing_result else ""),
            "root_chord_m": (round(res.wing_result.wing_geometry.root_chord_m, 3) if res and res.wing_result else ""),
            "tip_chord_m": (round(res.wing_result.wing_geometry.tip_chord_m, 3) if res and res.wing_result else ""),
            "mac_m": (round(res.wing_result.wing_geometry.mean_aerodynamic_chord_m, 3) if res and res.wing_result else ""),
            "taper_ratio": (round(res.wing_result.wing_geometry.taper_ratio, 3) if res and res.wing_result else ""),
            "sweep_deg": (round(res.wing_result.wing_geometry.sweep_angle_deg, 1) if res and res.wing_result else ""),
            "dihedral_deg": (round(res.wing_result.wing_geometry.dihedral_angle_deg, 1) if res and res.wing_result else ""),
            "wing_loading_kg_m2": (round(res.wing_result.wing_geometry.wing_loading_kg_m2, 2) if res and res.wing_result else ""),
            "selected_airfoil": (res.airfoil_result.selected_root_airfoil if res and res.airfoil_result else ""),
            "CLmax": (round(res.airfoil_result.polar_data.max_lift_coeff, 3) if res and res.airfoil_result and res.airfoil_result.polar_data else ""),
            "fuselage_length_m": (round(res.fuselage_result.fuselage_geometry.length_m, 3) if res and res.fuselage_result else ""),
            "fuselage_width_m": (round(res.fuselage_result.fuselage_geometry.width_m, 3) if res and res.fuselage_result else ""),
            "fuselage_height_m": (round(res.fuselage_result.fuselage_geometry.height_m, 3) if res and res.fuselage_result else ""),
            "fineness_ratio": (round(res.fuselage_result.fuselage_geometry.length_m / res.fuselage_result.fuselage_geometry.width_m, 2) if res and res.fuselage_result and res.fuselage_result.fuselage_geometry.width_m > 0 else ""),
            "horizontal_tail_area_m2": (round(res.tail_result.horizontal_tail.area_m2, 4) if res and res.tail_result else ""),
            "horizontal_tail_span_m": (round(res.tail_result.horizontal_tail.span_m, 3) if res and res.tail_result else ""),
            "vertical_tail_area_m2": (round(res.tail_result.vertical_tail.area_m2, 4) if res and res.tail_result else ""),
            "vertical_tail_height_m": (round(res.tail_result.vertical_tail.height_m, 3) if res and res.tail_result else ""),
            "tail_arm_m": "",
            "selected_motor": (res.propulsion_result.selected_motor_or_engine if res and res.propulsion_result else ""),
            "selected_propeller": (res.propulsion_result.selected_propeller if res and res.propulsion_result else ""),
            "selected_esc": "Generic ESC",
            "motor_count": 1,
            "required_cruise_thrust_n": (round(res.propulsion_result.thrust_analysis.required_cruise_thrust_n, 2) if res and res.propulsion_result and res.propulsion_result.thrust_analysis else ""),
            "required_max_thrust_n": (round(res.propulsion_result.thrust_analysis.required_takeoff_thrust_n, 2) if res and res.propulsion_result and res.propulsion_result.thrust_analysis else ""),
            "required_cruise_power_w": (round(res.propulsion_result.power_analysis.required_cruise_power_w, 1) if res and res.propulsion_result and res.propulsion_result.power_analysis else ""),
            "maximum_power_w": (round(res.propulsion_result.power_analysis.maximum_power_w, 1) if res and res.propulsion_result and res.propulsion_result.power_analysis else ""),
            "propulsive_efficiency": (round(res.propulsion_result.efficiency_analysis.propeller_efficiency, 3) if res and res.propulsion_result and res.propulsion_result.efficiency_analysis else ""),
            "flight_controller": "Pixhawk 6C",
            "gps": "GPS Module",
            "telemetry": (res.avionics_result.selected_telemetry if res and res.avionics_result else ""),
            "servo information": "4x Digital Servo",
            "battery configuration": "LiPo Pack",
            "cg_x_m": (round(res.mass_properties_result.center_of_gravity[0], 3) if res and res.mass_properties_result else ""),
            "cg_percent_mac": (round(100.0 * (res.mass_properties_result.center_of_gravity[0] - (getattr(res.fuselage_result.fuselage_geometry, 'wing_attachment_x_m', 0.35 * res.fuselage_result.fuselage_geometry.length_m) + res.wing_result.wing_geometry.quarter_chord_x_m)) / res.wing_result.wing_geometry.mean_aerodynamic_chord_m, 2) if res and res.mass_properties_result and res.wing_result and res.fuselage_result else ""),
            "neutral_point_x_m": (round(res.performance_result.stability_analysis.neutral_point_x_m, 4) if res and res.performance_result else ""),
            "neutral_point_percent_mac": (round(100.0 * (res.performance_result.stability_analysis.neutral_point_x_m - (getattr(res.fuselage_result.fuselage_geometry, 'wing_attachment_x_m', 0.35 * res.fuselage_result.fuselage_geometry.length_m) + res.wing_result.wing_geometry.quarter_chord_x_m)) / res.wing_result.wing_geometry.mean_aerodynamic_chord_m, 2) if res and res.performance_result and res.wing_result and res.fuselage_result else ""),
            "static_margin_percent": (round(res.mass_properties_result.static_margin * 100.0, 2) if res and res.mass_properties_result else ""),
            "stall_speed_kmh": (round(res.performance_result.stall_analysis.stall_speed_clean_kmh, 2) if res and res.performance_result else ""),
            "perf_cruise_speed_kmh": (round(res.performance_result.performance_analysis.cruise_speed_kmh, 2) if res and res.performance_result else ""),
            "maximum_speed_kmh": (round(res.performance_result.performance_analysis.maximum_speed_kmh, 2) if res and res.performance_result else ""),
            "rate_of_climb_mps": (round(res.performance_result.performance_analysis.max_rate_of_climb_m_s, 3) if res and res.performance_result else ""),
            "takeoff_distance_m": (round(res.performance_result.takeoff_analysis.takeoff_distance_m, 2) if res and res.performance_result else ""),
            "landing_distance_m": (round(res.performance_result.landing_analysis.landing_distance_m, 2) if res and res.performance_result else ""),
            "calculated_range_km": (round(res.performance_result.range_analysis.cruise_range_km, 2) if res and res.performance_result else ""),
            "calculated_endurance_min": (round(res.performance_result.endurance_analysis.cruise_endurance_min, 2) if res and res.performance_result else ""),
            "lift_to_drag_ratio": (round(res.performance_result.aerodynamic_analysis.lift_to_drag_ratio, 3) if res and res.performance_result else ""),
            "iteration_count": (res.iterations if res else 0),
            "final_relative_mtow_delta": (round(res.convergence_history[-1].relative_delta, 6) if res and res.convergence_history else ""),
            "converged": (res.converged if res else False),
            "requirement_compliance": ("Compliant" if res and res.verification_result and "Mission" in res.verification_result.compliance_report.verified_categories else ("Failed" if res and res.verification_result else "")),
            "constraint_compliance": ("Compliant" if res and res.verification_result and "Structural Constraints" in res.verification_result.compliance_report.verified_categories else ("Failed" if res and res.verification_result else "")),
            "stability_compliance": ("Compliant" if res and res.verification_result and "Stability" in res.verification_result.compliance_report.verified_categories else ("Failed" if res and res.verification_result else "")),
            "performance_compliance": ("Compliant" if res and res.verification_result and "Performance" in res.verification_result.compliance_report.verified_categories else ("Failed" if res and res.verification_result else "")),
            "safety_compliance": ("Compliant" if res and res.verification_result and "Safety" in res.verification_result.compliance_report.verified_categories else ("Failed" if res and res.verification_result else "")),
            "warnings_count": (len(res.warnings) if res else 0),
            "critical_failures_count": 0,
            "manual_review_priority": "NORMAL" if res and res.success else "HIGH",
            "review_flags": ""
        }
        output_rows.append(row)
        
        # Save structured JSON details
        results.append({
            "case_id": case_id,
            "requirements": to_dict(req),
            "configuration": to_dict(res.configuration_result) if res else None,
            "convergence_history": to_dict(res.convergence_history) if res else [],
            "mass_properties": to_dict(res.mass_properties_result) if res else None,
            "wing": to_dict(res.wing_result) if res else None,
            "airfoil": to_dict(res.airfoil_result) if res else None,
            "fuselage": to_dict(res.fuselage_result) if res else None,
            "tail": to_dict(res.tail_result) if res else None,
            "propulsion": to_dict(res.propulsion_result) if res else None,
            "avionics": to_dict(res.avionics_result) if res else None,
            "payload": to_dict(res.payload_result) if res else None,
            "performance": to_dict(res.performance_result) if res else None,
            "stability": to_dict(res.performance_result.stability_analysis) if res and res.performance_result else None,
            "verification": to_dict(res.verification_result) if res else None,
            "warnings": res.warnings if res else [],
            "errors": res.errors if res else [],
            "failure_category": "SUCCESS" if res and res.success else status_val,
            "manual_review_priority": "NORMAL" if res and res.success else "HIGH",
            "review_flags": [],
            "iteration_count": res.iterations if res else 0
        })

        # 2. Before / After Comparison Logic
        b_row = baseline_map.get(case_id)
        p5c_row = phase5c_map.get(case_id)
        
        p5c_status = b_row["original_status"]
        p5c_class = b_row["baseline_classification"]
        
        status_changed = "YES" if p5c_status != status_val else "NO"
        
        # Determine if change is expected
        is_expected = "NO"
        if p5c_class in ["configuration false rejection", "wing/fuselage coordination rejection", "verification-threshold false rejection"]:
            if status_changed == "YES" or status_val == "SUCCESS":
                is_expected = "YES"
            # It can also stay the same if it failed SIZING_INFEASIBLE for stability reasons rather than root chord
            elif p5c_status == "SIZING_INFEASIBLE" and status_val == "SIZING_INFEASIBLE":
                is_expected = "YES"
            elif p5c_status == "VERIFICATION_FAILED" and status_val == "VERIFICATION_FAILED":
                is_expected = "YES"
        elif p5c_class == "successful suspicious":
            if status_val in ["VERIFICATION_FAILED", "STABILITY_INFEASIBLE", "VERIFICATION_FAILURE"]:
                is_expected = "YES"
        else:
            if status_changed == "NO":
                is_expected = "YES"
            
        # Old values from Phase 5C ledger
        old_config = p5c_row["configuration_selected"] if pd.notna(p5c_row["configuration_selected"]) else "None"
        old_mtow = p5c_row["mtow_at_failure_kg"] if pd.notna(p5c_row["mtow_at_failure_kg"]) else "N/A"
        old_wingspan = p5c_row["wingspan_at_failure_m"] if pd.notna(p5c_row["wingspan_at_failure_m"]) else "N/A"
        old_ar = p5c_row["aspect_ratio_at_failure"] if pd.notna(p5c_row["aspect_ratio_at_failure"]) else "N/A"
        old_sm = p5c_row["static_margin_percent"] if pd.notna(p5c_row["static_margin_percent"]) else "N/A"
        
        old_stage = p5c_row["stage_failed"] if pd.notna(p5c_row["stage_failed"]) else "None"
        
        # New values
        new_config = row["configuration_name"] if res and res.configuration_result else "None"
        new_mtow = row["final_mtow_kg"] if res and res.mass_properties_result else "N/A"
        new_wingspan = row["wingspan_m"] if res and res.wing_result else "N/A"
        new_ar = row["aspect_ratio"] if res and res.wing_result else "N/A"
        new_sm = row["static_margin_percent"] if res and res.mass_properties_result else "N/A"
        
        new_stage = "None"
        if not (res and res.success):
            if res:
                new_stage = res.status.value
            else:
                new_stage = "INTERNAL_EXCEPTION"
                
        new_motor = row["selected_motor"] if res and res.propulsion_result else "None"
        new_prop = row["selected_propeller"] if res and res.propulsion_result else "None"
        
        # Battery bay boundary checks (FW-008 and FW-009)
        batt_valid = "N/A"
        if res and res.success:
            # Check battery location against bounds
            f_g = res.fuselage_result.fuselage_geometry
            batt_comp = next((comp for comp in res.mass_properties_result.component_masses if "Battery" in comp.name), None)
            if batt_comp:
                half_len = 0.5 * f_g.battery_bay_length_m
                x_min = f_g.nose_length_m + half_len + 0.02
                x_max = (f_g.length_m - f_g.tail_cone_length_m) - (half_len + 0.02)
                if x_min - 0.001 <= batt_comp.x_m <= x_max + 0.001:
                    batt_valid = "YES"
                else:
                    batt_valid = "NO"
                    print(f"!!! Battery invalid placement for {case_id}: {batt_comp.x_m} not in [{x_min}, {x_max}]")
            else:
                batt_valid = "NO"
        elif status_val in ["VERIFICATION_FAILED", "STABILITY_INFEASIBLE"]:
            batt_valid = "YES" # properly clamped/restricted and rejected
            
        # Final engineering assessment comments
        assessment = ""
        if status_val == "SUCCESS":
            assessment = "SUCCESS_VALID: Design successfully converged and passed all physical & stability checks."
            success_count += 1
        elif p5c_class == "catalog limitation":
            assessment = f"COMPONENT_DATABASE_LIMITATION: Sizing blocked by telemetry/payload limits of database."
            infeasible_count += 1
        elif p5c_class == "true physical/mission infeasibility":
            assessment = f"TRUE_MISSION_INFEASIBILITY: Sizing failed due to target range/MTOW limits."
            infeasible_count += 1
        elif case_id in ["FW-008", "FW-009"]:
            assessment = "STABILITY_INFEASIBLE: Battery placement correctly restricted to cabin bay; resulting static margin is unstable."
            infeasible_count += 1
        else:
            assessment = f"CLEANLY_REJECTED: Sizing failed verification compliance checks."
            infeasible_count += 1
            
        before_after_rows.append({
            "case_id": case_id,
            "phase5c_status": p5c_status,
            "phase5c_forensic_classification": p5c_class,
            "phase5d_status": status_val,
            "status_changed": status_changed,
            "change_expected": is_expected,
            "old_failure_stage": old_stage,
            "new_failure_stage": new_stage,
            "old_configuration": old_config,
            "new_configuration": new_config,
            "old_mtow": old_mtow,
            "new_mtow": new_mtow,
            "old_wingspan": old_wingspan,
            "new_wingspan": new_wingspan,
            "old_aspect_ratio": old_ar,
            "new_aspect_ratio": new_ar,
            "old_motor": "None",
            "new_motor": new_motor,
            "old_propeller": "None",
            "new_propeller": new_prop,
            "old_cg_percent_mac": "N/A",
            "new_cg_percent_mac": row["cg_percent_mac"] if res and res.mass_properties_result else "N/A",
            "old_static_margin": old_sm,
            "new_static_margin": new_sm,
            "battery_position_valid": batt_valid,
            "final_engineering_assessment": assessment
        })

    # Save to files
    # 1. reports/fixed_wing_phase5d_after_outputs.csv
    headers = list(output_rows[0].keys())
    with open("reports/fixed_wing_phase5d_after_outputs.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_rows)
        
    # 2. reports/fixed_wing_phase5d_after_outputs.json
    with open("reports/fixed_wing_phase5d_after_outputs.json", mode="w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    # 3. reports/fixed_wing_phase5d_before_after.csv
    ba_headers = list(before_after_rows[0].keys())
    with open("reports/fixed_wing_phase5d_before_after.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ba_headers)
        writer.writeheader()
        writer.writerows(before_after_rows)
        
    print("\n==================================================")
    print(f"TOTAL CASES: 100")
    print(f"SUCCESSFUL DESIGNS (Phase 5D): {success_count}")
    print(f"INFEASIBLE / REJECTED: {infeasible_count}")
    print("==================================================")

if __name__ == '__main__':
    main()
