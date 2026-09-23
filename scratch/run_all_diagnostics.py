import sys
import os
import math

# Add workspace root to path
sys.path.append(r"c:\Users\acer\Documents\torqwings studio v2")

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

def run_mission(payload_kg, range_km, endurance_min, cruise_kmh, label):
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=payload_kg,
        target_flight_time_min=endurance_min,
        target_range_km=range_km,
        cruise_speed_kmh=cruise_kmh,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline(tolerance=0.01, max_iterations=30)
    res = pipeline.execute(req)
    return res

print("==================================================")
print("RUNNING NOMINAL MISSION DIAGNOSTIC FOR CG/STABILITY")
print("==================================================")
res = run_mission(2.0, 60.0, 90.0, 95.0, "Nominal")

if res.success:
    wb = res.mass_properties_result.weight_breakdown
    geom = res.wing_result.wing_geometry
    f_geom = res.fuselage_result.fuselage_geometry
    prop_res = res.propulsion_result
    
    print("\n--- COMPONENT MOMENTS TABLE ---")
    total_moment = 0.0
    total_mass = 0.0
    components = res.mass_properties_result.component_masses
    for c in components:
        mom = c.mass_kg * c.x_m
        total_moment += mom
        total_mass += c.mass_kg
        print(f"Component: {c.name:<25} | Mass: {c.mass_kg:>7.3f} kg | X: {c.x_m:>6.3f} m | Moment: {mom:>7.3f} kg*m")
    
    cg_x = total_moment / total_mass
    print("-" * 75)
    print(f"Calculated CG X (from moments): {cg_x:.4f} m (Engine CG: {res.mass_properties_result.center_of_gravity[0]:.4f} m)")
    print(f"Sum Mass: {total_mass:.4f} kg (Engine MTOW: {wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg:.4f} kg)")
    
    # Check intermediate calculations in MassPropertiesEngine
    wing_x = getattr(f_geom, 'wing_attachment_x_m', 0.0)
    quarter_chord_x = geom.quarter_chord_x_m
    global_quarter_chord = wing_x + quarter_chord_x
    mac = geom.mean_aerodynamic_chord_m
    
    print("\n--- GEOMETRICAL REFERENCES ---")
    print(f"Fuselage Length               : {f_geom.length_m:.4f} m")
    print(f"Wing Attachment X from Nose   : {wing_x:.4f} m")
    print(f"Wing Quarter-Chord relative to Root LE: {quarter_chord_x:.4f} m")
    print(f"Wing Global Quarter-Chord     : {global_quarter_chord:.4f} m")
    print(f"Wing MAC                      : {mac:.4f} m")
    
    # CG % MAC
    cg_pct_mac_from_root = (cg_x - quarter_chord_x) / mac * 100.0
    cg_pct_mac_from_global = (cg_x - global_quarter_chord) / mac * 100.0
    cg_pct_mac_from_wing_le = (cg_x - wing_x) / mac * 100.0
    
    print(f"CG X relative to Wing LE      : {cg_x - wing_x:.4f} m")
    print(f"CG X as % MAC relative to wing root LE: {cg_pct_mac_from_wing_le:.2f}%")
    print(f"CG X as % MAC relative to wing quarter chord: {cg_pct_mac_from_root:.2f}%")
    print(f"CG X as % MAC relative to global quarter chord: {cg_pct_mac_from_global:.2f}%")
    print(f"Engine Static Margin          : {res.mass_properties_result.static_margin*100:.2f}%")
    
    # How neutral point is calculated:
    # np_pct is 0.42 for Conventional tail
    np_pct = 0.42
    if wing_x > 0.0 or cg_x > (quarter_chord_x + mac):
        neutral_point_x = global_quarter_chord + (np_pct * mac)
    else:
        neutral_point_x = quarter_chord_x + (np_pct * mac)
    
    static_margin = (neutral_point_x - cg_x) / mac
    print(f"Neutral Point X               : {neutral_point_x:.4f} m")
    print(f"Neutral Point % MAC from wing LE: {(neutral_point_x - wing_x)/mac*100:.2f}%")
    print(f"Manual Static Margin          : {static_margin*100:.2f}%")
    
    # Let's inspect the target battery placement CG math:
    target_cg_x = quarter_chord_x + 0.24 * mac
    print(f"Target CG X used in engine    : {target_cg_x:.4f} m (Note: missing wing_x!)")
    
    # Propulsion trace
    print("\n--- PROPULSION DETAILS ---")
    t_anal = prop_res.thrust_analysis
    p_anal = prop_res.power_analysis
    ef_anal = prop_res.efficiency_analysis
    print(f"MTOW                          : {total_mass:.4f} kg")
    print(f"Required cruise thrust        : {t_anal.required_cruise_thrust_n:.2f} N")
    print(f"Required max thrust           : {t_anal.required_takeoff_thrust_n:.2f} N")
    print(f"T/W ratio                     : {t_anal.thrust_to_weight_ratio:.2f}")
    print(f"Cruise velocity               : {95.0 / 3.6:.2f} m/s")
    print(f"Aerodynamic efficiency (L/D)  : {res.performance_result.aerodynamic_analysis.lift_to_drag_ratio:.2f}")
    print(f"Propulsive efficiency (prop)   : {ef_anal.propeller_efficiency:.2f}")
    print(f"Motor efficiency              : {ef_anal.motor_efficiency:.2f}")
    print(f"Total efficiency (eta_total)  : {ef_anal.total_system_efficiency:.3f}")
    print(f"Required cruise power (shaft) : {p_anal.required_cruise_power_w:.2f} W")
    print(f"Selected motor                : {prop_res.selected_motor_or_engine}")
    print(f"Motor mass                    : {p_anal.metadata.get('motor_weight_g')/1000.0:.3f} kg")
    print(f"Selected propeller            : {prop_res.selected_propeller}")
    print(f"Battery voltage               : {p_anal.metadata.get('voltage_v'):.2f} V")
    print(f"Current draw                  : {p_anal.current_draw_cruise_a:.2f} A")
    
    # Let's verify independently:
    g = 9.80665
    T_cruise_ind = (total_mass * g) / res.performance_result.aerodynamic_analysis.lift_to_drag_ratio
    P_propulsive_ind = T_cruise_ind * (95.0 / 3.6)
    P_cruise_ind = P_propulsive_ind / ef_anal.total_system_efficiency
    print(f"Independent Cruise Thrust     : {T_cruise_ind:.4f} N (Engine: {t_anal.required_cruise_thrust_n:.2f} N)")
    print(f"Independent Cruise Power      : {P_cruise_ind:.4f} W (Engine: {p_anal.required_cruise_power_w:.2f} W)")

print("\n==================================================")
print("RUNNING FOUR CONTROL MISSIONS")
print("==================================================")
controls = [
    ("CONTROL A", 0.5, 20.0, 30.0, 60.0),
    ("CONTROL B", 1.0, 40.0, 60.0, 75.0),
    ("CONTROL C", 2.0, 60.0, 90.0, 95.0),
    ("CONTROL D", 5.0, 100.0, 120.0, 100.0)
]

for label, payload, range_km, endurance, cruise in controls:
    print(f"\nRunning {label}...")
    res = run_mission(payload, range_km, endurance, cruise, label)
    if res.success:
        wb = res.mass_properties_result.weight_breakdown
        geom = res.wing_result.wing_geometry
        f_geom = res.fuselage_result.fuselage_geometry
        verif = res.verification_result
        is_compliant = verif.compliance_report.is_fully_compliant
        
        # Calculate fractions
        mtow = wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg
        payload_frac = wb.payload_weight_kg / mtow
        battery_frac = wb.battery_fuel_weight_kg / mtow
        struct_frac = wb.structural_weight_kg / mtow
        
        # CG and NP
        cg_x = res.mass_properties_result.center_of_gravity[0]
        wing_x = getattr(f_geom, 'wing_attachment_x_m', 0.0)
        mac = geom.mean_aerodynamic_chord_m
        cg_pct_mac = (cg_x - wing_x) / mac * 100.0
        
        np_pct = 0.42
        neutral_point_x = (wing_x + geom.quarter_chord_x_m) + (np_pct * mac)
        np_pct_mac = (neutral_point_x - wing_x) / mac * 100.0
        
        print(f"  Final MTOW        : {mtow:.4f} kg")
        print(f"  Payload fraction  : {payload_frac*100:.2f}%")
        print(f"  Battery fraction  : {battery_frac*100:.2f}%")
        print(f"  Structural fraction: {struct_frac*100:.2f}%")
        print(f"  Wing span         : {geom.span_m:.4f} m")
        print(f"  Wing area         : {geom.reference_area_m2:.4f} m2")
        print(f"  Fuselage length   : {f_geom.length_m:.4f} m")
        print(f"  CG % MAC (wing LE): {cg_pct_mac:.2f}%")
        print(f"  NP % MAC (wing LE): {np_pct_mac:.2f}%")
        print(f"  Static margin     : {res.mass_properties_result.static_margin*100:.2f}%")
        print(f"  Verification      : {verif.verification_status} (Compliant={is_compliant})")
        print(f"  Iterations        : {res.iterations}")
    else:
        print(f"  Failed! Status: {res.status}, Errors: {res.errors}")
