import os

def revert():
    # 1. Revert fixed_wing_design_pipeline.py
    pipeline_path = r"c:\Users\acer\Documents\torqwings studio v2\backend\design\fixed_wing\pipeline\fixed_wing_design_pipeline.py"
    with open(pipeline_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    target_post = 'verif_passed = getattr(verif_report, "is_fully_compliant", False) if verif_report else True'
    target_pre = 'verif_passed = getattr(verif_report, "overall_compliance", True) if verif_report else True'
    if target_post in content:
        content = content.replace(target_post, target_pre)
        with open(pipeline_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Reverted fixed_wing_design_pipeline.py")
    else:
        print("fixed_wing_design_pipeline.py already pre-fix or diff mismatch")

    # 2. Revert mass_properties_engine.py
    mass_path = r"c:\Users\acer\Documents\torqwings studio v2\backend\design\fixed_wing\mass_properties\mass_properties_engine.py"
    with open(mass_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    post_block = """        # Sized payload
        pay_mass = m_profile.payload_kg
        pay_x = requirements.payload_result.payload_layout.placement_x_m

        # Sized battery mass using physics-based continuous power energy sizing
        p_av = requirements.avionics_result.power_analysis.continuous_power_w
        p_pay = requirements.payload_result.payload_analysis.power_consumption_w
        p_cruise = requirements.propulsion_result.power_analysis.required_cruise_power_w
        p_continuous = p_cruise + p_av + p_pay
        # Sized battery capacity assuming 85% usable depth of discharge (15% reserve)
        required_energy_wh = p_continuous * (m_profile.flight_time_min / 60.0) / 0.85
        # Specific energy of 200.0 Wh/kg
        batt_mass = required_energy_wh / 200.0
        wing_x = getattr(f_geom, 'wing_attachment_x_m', 0.35 * f_geom.length_m)
        target_cg_x = wing_x + wing_geom.quarter_chord_x_m + (0.24 * wing_geom.mean_aerodynamic_chord_m)
        # Sizing battery x: sum_m_without_batt * x_without_batt + m_batt * x_batt = m_total * target_cg
        non_batt_mass = w_mass + t_mass + f_mass + p_mass + av_mass + pay_mass
        non_batt_moment = (w_mass * w_x_pos +
                             t_mass * (f_geom.length_m - 0.12) +
                             f_mass * (f_geom.length_m * 0.46) +
                             p_mass * motor_x +
                             av_mass * av_x +
                             pay_mass * pay_x)
        
        # We need: (non_batt_moment + batt_mass * x_batt) / (non_batt_mass + batt_mass) = target_cg_x
        # x_batt = [target_cg_x * (non_batt_mass + batt_mass) - non_batt_moment] / batt_mass
        batt_x = (target_cg_x * (non_batt_mass + batt_mass) - non_batt_moment) / max(0.1, batt_mass)
        batt_x = max(0.10, min(f_geom.length_m - 0.20, batt_x))
        components.append(ComponentMass("Energy Battery", round(batt_mass, 3), round(batt_x, 3), 0.0, -0.04))

        components.append(ComponentMass("Mission Payload", round(pay_mass, 3), round(pay_x, 3), 0.0, -0.05))"""
        
    pre_block = """        # Sized battery / fuel mass
        mtow_est = m_profile.maximum_takeoff_weight_limit_kg or 3.5
        effective_batt_frac = max(batt_frac, min(0.48, batt_frac * (m_profile.flight_time_min / 60.0)))
        batt_mass = mtow_est * effective_batt_frac
        target_cg_x = wing_geom.quarter_chord_x_m + (0.24 * wing_geom.mean_aerodynamic_chord_m)
        # Sizing battery x: sum_m_without_batt * x_without_batt + m_batt * x_batt = m_total * target_cg
        non_batt_mass = w_mass + t_mass + f_mass + p_mass + av_mass
        non_batt_moment = (w_mass * (wing_geom.quarter_chord_x_m + 0.04) +
                             t_mass * (f_geom.length_m - 0.12) +
                             f_mass * (f_geom.length_m * 0.46) +
                             p_mass * motor_x +
                             av_mass * av_x)
        
        # We need: (non_batt_moment + batt_mass * x_batt) / (non_batt_mass + batt_mass) = target_cg_x
        # x_batt = [target_cg_x * (non_batt_mass + batt_mass) - non_batt_moment] / batt_mass
        batt_x = (target_cg_x * (non_batt_mass + batt_mass) - non_batt_moment) / max(0.1, batt_mass)
        batt_x = max(0.10, min(f_geom.length_m - 0.20, batt_x))
        components.append(ComponentMass("Energy Battery", round(batt_mass, 3), round(batt_x, 3), 0.0, -0.04))

        # Sized payload
        pay_mass = m_profile.payload_kg
        pay_x = requirements.payload_result.payload_layout.placement_x_m
        components.append(ComponentMass("Mission Payload", round(pay_mass, 3), round(pay_x, 3), 0.0, -0.05))"""
        
    # We clean up carriage returns for robust matching
    content_clean = content.replace('\r\n', '\n')
    post_block_clean = post_block.replace('\r\n', '\n')
    pre_block_clean = pre_block.replace('\r\n', '\n')
    
    if post_block_clean in content_clean:
        content_clean = content_clean.replace(post_block_clean, pre_block_clean)
        with open(mass_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content_clean)
        print("Reverted mass_properties_engine.py")
    else:
        print("mass_properties_engine.py already pre-fix or block mismatch")

    # 3. Revert stability_checker.py
    stab_path = r"c:\Users\acer\Documents\torqwings studio v2\backend\design\fixed_wing\verification\stability_checker.py"
    with open(stab_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    post_stab = """        elif mass_res.static_margin > 0.25:
            failures.append(
                f"Excessive static stability margin ({mass_res.static_margin*100:.1f}%). "
                "The aircraft is excessively nose-heavy, causing high trim drag and limited elevator pitch control authority."
            )"""
    pre_stab = """        elif mass_res.static_margin > 0.25:
            # excessive stability is a warning, not failure
            pass"""
            
    content_clean = content.replace('\r\n', '\n')
    post_stab_clean = post_stab.replace('\r\n', '\n')
    pre_stab_clean = pre_stab.replace('\r\n', '\n')
    
    if post_stab_clean in content_clean:
        content_clean = content_clean.replace(post_stab_clean, pre_stab_clean)
        with open(stab_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content_clean)
        print("Reverted stability_checker.py")
    else:
        print("stability_checker.py already pre-fix or block mismatch")

    # 4. Revert flight_performance_engine.py
    perf_path = r"c:\Users\acer\Documents\torqwings studio v2\backend\design\fixed_wing\flight_performance\flight_performance_engine.py"
    with open(perf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    post_to = "takeoff_dist = (2.0 * wing_geom.wing_loading_kg_m2) / max(0.01, rho * t_to_w * cl_takeoff)"
    pre_to = "takeoff_dist = (20.0 * wing_geom.wing_loading_kg_m2) / max(0.01, t_to_w * cl_takeoff * g)"
    
    post_ld = "landing_dist = (1.2 * wing_geom.wing_loading_kg_m2) / max(0.01, rho * cl_max_landing)"
    pre_ld = "landing_dist = (12.0 * wing_geom.wing_loading_kg_m2) / max(0.01, rho * cl_max_landing * g)"
    
    content_clean = content.replace('\r\n', '\n')
    if post_to in content_clean:
        content_clean = content_clean.replace(post_to, pre_to)
    if post_ld in content_clean:
        content_clean = content_clean.replace(post_ld, pre_ld)
        
    with open(perf_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content_clean)
    print("Reverted flight_performance_engine.py")

    # 5. Revert propulsion_engine.py
    prop_path = r"c:\Users\acer\Documents\torqwings studio v2\backend\design\fixed_wing\propulsion\propulsion_engine.py"
    with open(prop_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    post_prop = "to_dist = (2.0 * wl) / max(0.1, rho * t_to_w_actual * cl_to)"
    pre_prop = "to_dist = (20.0 * wl) / max(0.1, t_to_w_actual * cl_to * g)"
    
    content_clean = content.replace('\r\n', '\n')
    if post_prop in content_clean:
        content_clean = content_clean.replace(post_prop, pre_prop)
        with open(prop_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content_clean)
        print("Reverted propulsion_engine.py")
    else:
        print("propulsion_engine.py already pre-fix or block mismatch")

if __name__ == '__main__':
    revert()
