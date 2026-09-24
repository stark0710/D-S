import sys
import os
import json
import csv
import pandas as pd

# Add workspace to path
sys.path.append(r'c:\Users\acer\Documents\torqwings studio v2')

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from scratch.run_campaign import generate_100_cases, to_dict

def format_value(val, fmt=None):
    if val is None or val == "":
        return "N/A"
    if isinstance(val, float):
        if fmt:
            return fmt.format(val)
        return f"{val:.4f}"
    if isinstance(val, list):
        if not val:
            return "None"
        return ", ".join(str(x) for x in val)
    return str(val)

def dict_to_md_table(d, indent=""):
    if not d:
        return "N/A\n"
    lines = []
    lines.append(f"{indent}| Parameter | Value |")
    lines.append(f"{indent}| :--- | :--- |")
    for k, v in d.items():
        if isinstance(v, dict):
            # Inline nested dicts
            v_str = "<br>".join(f"**{nk}**: {format_value(nv)}" for nk, nv in v.items())
        elif isinstance(v, list):
            v_str = "<br>".join(format_value(x) for x in v)
        else:
            v_str = format_value(v)
        # Clean markdown characters
        v_str = v_str.replace("|", "\\|").replace("\n", "<br>")
        lines.append(f"{indent}| {k} | {v_str} |")
    return "\n".join(lines) + "\n"

def main():
    print("Generating cases...")
    cases = generate_100_cases()
    successful_ids = ["FW-004", "FW-007", "FW-012", "FW-013", "FW-016", "FW-023", "FW-037", "FW-040", "FW-097", "FW-100"]
    
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    summary_rows = []
    
    for case_id in successful_ids:
        c = next(x for x in cases if x["case_id"] == case_id)
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
        
        print(f"Rerunning and generating datasheet for {case_id}...")
        res = pipeline.execute(req)
        
        if not (res and res.success):
            print(f"!!! Error: Case {case_id} failed to size during datasheet generation!")
            if res:
                print(f"Status: {res.status.value}, Errors: {res.errors}")
            continue
            
        # Serialize all outputs to dict
        d_config = to_dict(res.configuration_result)
        d_mission = to_dict(res.mission_result)
        d_wing = to_dict(res.wing_result)
        d_airfoil = to_dict(res.airfoil_result)
        d_tail = to_dict(res.tail_result)
        d_fuselage = to_dict(res.fuselage_result)
        d_prop = to_dict(res.propulsion_result)
        d_av = to_dict(res.avionics_result)
        d_pay = to_dict(res.payload_result)
        d_mass = to_dict(res.mass_properties_result)
        d_perf = to_dict(res.performance_result)
        d_ver = to_dict(res.verification_result)
        
        wb = res.mass_properties_result.weight_breakdown
        final_mtow = wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg
        
        # Accumulate summary row
        summary_rows.append({
            "case_id": case_id,
            "mission_category": c["mission_type"].value,
            "required_payload_kg": c["payload_kg"],
            "required_range_km": c["range_km"],
            "required_endurance_min": c["endurance_min"],
            "required_cruise_speed_kmh": c["cruise_speed_kmh"],
            "configuration": f"{res.configuration_result.wing_configuration} / {res.configuration_result.propulsion_configuration}",
            "wing_position": res.configuration_result.selected_configuration.get("wing_position", ""),
            "propulsion_layout": res.configuration_result.selected_configuration.get("propulsion_layout", ""),
            "tail_config": res.configuration_result.selected_configuration.get("tail_configuration", ""),
            "landing_gear": res.configuration_result.selected_configuration.get("landing_gear_configuration", ""),
            "wingspan_m": round(res.wing_result.wing_geometry.span_m, 3),
            "wing_area_m2": round(res.wing_result.wing_geometry.reference_area_m2, 4),
            "aspect_ratio": round(res.wing_result.wing_geometry.aspect_ratio, 2),
            "root_chord_m": round(res.wing_result.wing_geometry.root_chord_m, 3),
            "selected_airfoil": res.airfoil_result.selected_root_airfoil,
            "fuselage_length_m": round(res.fuselage_result.fuselage_geometry.length_m, 3),
            "fuselage_width_m": round(res.fuselage_result.fuselage_geometry.width_m, 3),
            "selected_motor": res.propulsion_result.selected_motor_or_engine,
            "selected_propeller": res.propulsion_result.selected_propeller,
            "battery_mass_kg": round(wb.battery_fuel_weight_kg, 3),
            "battery_fraction": round(wb.battery_fraction, 4),
            "battery_energy_wh": round(wb.battery_fuel_weight_kg * 200.0, 2),
            "mtow_kg": round(final_mtow, 3),
            "cg_x_m": round(res.mass_properties_result.center_of_gravity[0], 3),
            "static_margin_percent": round(res.mass_properties_result.static_margin * 100.0, 2),
            "stall_speed_kmh": round(res.performance_result.stall_analysis.stall_speed_clean_kmh, 2),
            "calculated_range_km": round(res.performance_result.range_analysis.cruise_range_km, 2),
            "calculated_endurance_min": round(res.performance_result.endurance_analysis.cruise_endurance_min, 2),
            "lift_to_drag_ratio": round(res.performance_result.aerodynamic_analysis.lift_to_drag_ratio, 3)
        })
        
        # Build individual Markdown report
        md = []
        md.append(f"# ENGINEERING SPECIFICATION DATASHEET: {case_id}")
        md.append(f"**Aircraft Design Synthesis Handoff Report**")
        md.append(f"Generated at: 2026-08-01 (Torq Wings Studio V3 Phase 5D)")
        md.append(f"Status: **{res.status.value}**\n")
        
        md.append("---")
        md.append("## 1. Executive Summary Specification")
        exec_specs = {
            "Case ID": case_id,
            "Mission Category": c["mission_type"].value,
            "Target MTOW (kg)": f"{final_mtow:.3f} kg",
            "Wing Configuration": res.configuration_result.wing_configuration,
            "Propulsion Configuration": res.configuration_result.propulsion_configuration,
            "Wingspan": f"{res.wing_result.wing_geometry.span_m:.3f} m",
            "Wing Area": f"{res.wing_result.wing_geometry.reference_area_m2:.4f} m²",
            "Aspect Ratio": f"{res.wing_result.wing_geometry.aspect_ratio:.2f}",
            "Selected Root Airfoil": res.airfoil_result.selected_root_airfoil,
            "Selected Motor": res.propulsion_result.selected_motor_or_engine,
            "Selected Propeller": res.propulsion_result.selected_propeller,
            "Battery Capacity (Wh)": f"{wb.battery_fuel_weight_kg * 200.0:.2f} Wh",
            "Static Stability Margin": f"{res.mass_properties_result.static_margin * 100.0:.2f}%",
            "Stall Speed": f"{res.performance_result.stall_analysis.stall_speed_clean_kmh:.2f} km/h",
            "Cruise Speed": f"{res.performance_result.performance_analysis.cruise_speed_kmh:.2f} km/h",
            "Range (Calculated)": f"{res.performance_result.range_analysis.cruise_range_km:.2f} km",
            "Endurance (Calculated)": f"{res.performance_result.endurance_analysis.cruise_endurance_min:.2f} min"
        }
        md.append(dict_to_md_table(exec_specs))
        
        md.append("## 2. Mission Requirements")
        md.append(dict_to_md_table(d_mission.get("requirements", {})))
        
        md.append("## 3. Configuration Analysis")
        md.append(dict_to_md_table(d_config.get("selected_configuration", {})))
        if "rejection_history" in d_config and d_config["rejection_history"]:
            md.append("### Strategic Configuration Fallback Rejection History")
            md.append(dict_to_md_table(d_config["rejection_history"]))
            
        md.append("## 4. Wing Geometry & Sizing")
        md.append(dict_to_md_table(d_wing.get("wing_geometry", {})))
        if "engineering_notes" in d_wing and d_wing["engineering_notes"]:
            md.append("### Wing Sizing Notes")
            md.append("\n".join(f"- {note}" for note in d_wing["engineering_notes"]) + "\n")
            
        md.append("## 5. Airfoil Selection")
        md.append(dict_to_md_table({
            "Selected Root Airfoil": d_airfoil.get("selected_root_airfoil"),
            "Selected Tip Airfoil": d_airfoil.get("selected_tip_airfoil"),
            "Reynolds Number (Root)": d_airfoil.get("reynolds_analysis", {}).get("reynolds_number_cruise"),
            "Section drag coeff (Cd0)": d_airfoil.get("polar_data", {}).get("min_drag_coeff"),
            "Section max lift (Clmax)": d_airfoil.get("polar_data", {}).get("max_lift_coeff")
        }))
        
        md.append("## 6. Tail Geometry")
        md.append("### Horizontal Tail")
        md.append(dict_to_md_table(d_tail.get("horizontal_tail", {})))
        md.append("### Vertical Tail")
        md.append(dict_to_md_table(d_tail.get("vertical_tail", {})))
        md.append("### Volume Coefficients")
        md.append(dict_to_md_table(d_tail.get("tail_volume_coefficients", {})))
        
        md.append("## 7. Fuselage Sizing & Component Layout")
        md.append(dict_to_md_table(d_fuselage.get("fuselage_geometry", {})))
        md.append("### Component Placement Locations (m from nose)")
        md.append(dict_to_md_table(d_fuselage.get("component_placement", {})))
        
        md.append("## 8. Propulsion System Specification")
        md.append(dict_to_md_table({
            "Selected Motor": d_prop.get("selected_motor_or_engine"),
            "Selected Propeller": d_prop.get("selected_propeller"),
            "Propulsion Layout": d_prop.get("propulsion_layout"),
            "Propulsion Weight (kg)": wb.propulsion_weight_kg
        }))
        md.append("### Cruise Propulsion Analysis")
        md.append(dict_to_md_table(d_prop.get("cruise_analysis", {})))
        md.append("### Thrust & Climb Limits")
        md.append(dict_to_md_table(d_prop.get("thrust_analysis", {})))
        md.append("### System Electrical Power Analysis")
        md.append(dict_to_md_table(d_prop.get("power_analysis", {})))
        md.append("### Propulsive Efficiency")
        md.append(dict_to_md_table(d_prop.get("efficiency_analysis", {})))
        
        md.append("## 9. Electronics & Avionics")
        md.append(dict_to_md_table({
            "Flight Controller": d_av.get("selected_flight_controller"),
            "GPS Navigation System": d_av.get("selected_navigation_system"),
            "Telemetry Module": d_av.get("selected_telemetry"),
            "Companion Computer": d_av.get("selected_companion_computer"),
            "Receiver": d_av.get("selected_receiver"),
            "Sensors": d_av.get("selected_sensors")
        }))
        
        md.append("## 10. Battery System Sizing")
        md.append(dict_to_md_table({
            "Battery Weight (kg)": wb.battery_fuel_weight_kg,
            "Battery Mass Fraction (%)": f"{wb.battery_fraction*100.0:.2f}%",
            "Battery Energy (Wh)": wb.battery_fuel_weight_kg * 200.0,
            "Battery Specific Energy (Wh/kg)": 200.0
        }))
        
        md.append("## 11. Payload Configuration")
        md.append(dict_to_md_table({
            "Installed Payload Mass (kg)": d_pay.get("installed_payload_mass_kg"),
            "Requested Payload Mass (kg)": d_pay.get("requested_payload_mass_kg"),
            "Design Margin (kg)": d_pay.get("payload_design_margin_kg"),
            "Selected Sensors / Cargo": d_pay.get("selected_payloads")
        }))
        
        md.append("## 12. Mass & Weight Breakdown")
        md.append(dict_to_md_table(d_mass.get("weight_breakdown", {})))
        
        md.append("## 13. Center of Gravity (CG) & Stability")
        md.append(dict_to_md_table({
            "CG Location X (m from nose)": d_mass.get("center_of_gravity", [0])[0],
            "CG Location Y (m)": d_mass.get("center_of_gravity", [0, 0])[1],
            "CG Location Z (m)": d_mass.get("center_of_gravity", [0, 0, 0])[2],
            "Neutral Point (m from nose)": d_perf.get("stability_analysis", {}).get("neutral_point_x_m"),
            "Static Margin (%)": f"{res.mass_properties_result.static_margin*100.0:.2f}%"
        }))
        
        md.append("## 14. Aerodynamics & Flight Performance")
        md.append("### Cruising Performance")
        md.append(dict_to_md_table(d_perf.get("performance_analysis", {})))
        md.append("### Stall Speed Analysis")
        md.append(dict_to_md_table(d_perf.get("stall_analysis", {})))
        md.append("### Range Sizing")
        md.append(dict_to_md_table(d_perf.get("range_analysis", {})))
        md.append("### Endurance Sizing")
        md.append(dict_to_md_table(d_perf.get("endurance_analysis", {})))
        md.append("### Takeoff Performance")
        md.append(dict_to_md_table(d_perf.get("takeoff_analysis", {})))
        md.append("### Landing Performance")
        md.append(dict_to_md_table(d_perf.get("landing_analysis", {})))
        md.append("### Aerodynamic Coefficients")
        md.append(dict_to_md_table(d_perf.get("aerodynamic_analysis", {})))
        
        md.append("## 15. Compliance Verification & Risk Assessment")
        md.append(dict_to_md_table({
            "Verification Status": d_ver.get("verification_status"),
            "Mission Readiness": d_ver.get("mission_status"),
            "Violations Count": len(d_ver.get("constraint_violations", [])),
            "Warnings Count": len(res.warnings)
        }))
        if d_ver.get("constraint_violations"):
            md.append("### Constraint Violations")
            md.append("\n".join(f"- **VIOLATION**: {v}" for v in d_ver["constraint_violations"]) + "\n")
        if res.warnings:
            md.append("### Warnings")
            md.append("\n".join(f"- **WARNING**: {w}" for w in res.warnings) + "\n")
            
        md.append("### Verification Risk Assessment")
        md.append(dict_to_md_table(d_ver.get("risk_analysis", {})))
        
        md.append("---")
        md.append("## 16. Final Aircraft Design Configuration File Specification")
        # Put the raw result dictionary in markdown code block for handoff
        specs_json = json.dumps(to_dict(res), indent=4)
        # Truncate some large historical structures or data to keep markdown clean
        md.append("```json\n" + specs_json[:15000] + "\n... [truncated specification payload] ...\n```")
        
        # Save markdown file
        filename = f"{case_id}_ENGINEERING_DATASHEET.md"
        with open(filename, mode="w", encoding="utf-8") as f:
            f.write("\n".join(md))
        print(f"Created {filename}")
        
    # Create the summary csv
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv("fixed_wing_successful_aircraft_summary.csv", index=False)
    print("Created fixed_wing_successful_aircraft_summary.csv")

if __name__ == '__main__':
    main()
