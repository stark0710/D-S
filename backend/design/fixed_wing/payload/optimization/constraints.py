"""
Fixed-Wing Payload Packaging Sizing Constraints

Rejects candidate layouts with overlapping components, spar interference, or invalid bounds.
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.constraint_manager import ConstraintManager

def map_layout_coordinates(candidate: OptimizationCandidate, context: OptimizationContext) -> dict:
    fuse_spec = None
    if context.previous_specifications:
        fuse_spec = context.previous_specifications.get("FuselageOptimizer")
        
    L = getattr(fuse_spec, "overall_length", 1.3)
    nose_l = getattr(fuse_spec, "nose_length", 0.23)
    cabin_l = getattr(fuse_spec, "cabin_length", 0.55)
    wing_x = getattr(fuse_spec, "wing_mount_position", 0.416)
    
    p_mode = candidate.design_variables["payload_position_mode"]
    b_mode = candidate.design_variables["battery_position_mode"]
    b_ori = candidate.design_variables["battery_orientation"]
    e_mode = candidate.design_variables["electronics_layout_mode"]
    
    mode_offsets = {
        "Forward": nose_l + 0.15 * cabin_l,
        "Mid": nose_l + 0.50 * cabin_l,
        "Central": nose_l + 0.50 * cabin_l,
        "Rear": nose_l + 0.85 * cabin_l
    }
    
    x_payload = mode_offsets[p_mode]
    x_battery = mode_offsets[b_mode]
    
    if e_mode in ["Stacked Above", "Stacked Below", "Side Mounted"]:
        x_avionics = x_battery
    else:
        all_modes = {"Forward", "Mid", "Rear", "Central"}
        used_modes = {p_mode, b_mode}
        rem_modes = list(all_modes - used_modes)
        rem_mode = rem_modes[0] if rem_modes else "Rear"
        x_avionics = mode_offsets[rem_mode]
        
    x_gps = x_avionics + 0.12
    x_telemetry = x_avionics - 0.08
    x_receiver = x_avionics + 0.04
    
    return {
        "payload_x": x_payload,
        "battery_x": x_battery,
        "avionics_x": x_avionics,
        "gps_x": x_gps,
        "telemetry_x": x_telemetry,
        "receiver_x": x_receiver,
        "wing_x": wing_x,
        "nose_l": nose_l,
        "cabin_l": cabin_l,
        "total_l": L
    }

def get_component_lengths(context: OptimizationContext, battery_orientation: str) -> tuple[float, float]:
    reqs = context.requirements
    m_profile = getattr(reqs.mission_result, "mission_profile", None) if reqs else None
    payload_mass = getattr(m_profile, "payload_kg", 2.0)
    
    p_len = max(0.05, min(0.16, 0.04 + payload_mass * 0.04))
    
    mtow = (
        getattr(m_profile, "maximum_takeoff_weight_limit_kg", None)
        or getattr(m_profile, "current_iteration_mtow_kg", None)
        or getattr(m_profile, "initial_mtow_seed_kg", None)
        or 10.0
    )
    b_len_base = max(0.05, min(0.13, 0.03 + mtow * 0.01))
    
    if battery_orientation == "Lateral":
        b_len = b_len_base * 0.5
    else:
        b_len = b_len_base
        
    return p_len, b_len

def check_overlap(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    coords = map_layout_coordinates(candidate, context)
    b_ori = candidate.design_variables["battery_orientation"]
    p_len, b_len = get_component_lengths(context, b_ori)
    
    p_min = coords["payload_x"] - p_len / 2.0
    p_max = coords["payload_x"] + p_len / 2.0
    
    b_min = coords["battery_x"] - b_len / 2.0
    b_max = coords["battery_x"] + b_len / 2.0
    
    if max(p_min, b_min) < min(p_max, b_max):
        return False, f"Payload [{p_min:.3f}, {p_max:.3f}] overlaps with Battery [{b_min:.3f}, {b_max:.3f}]."
        
    e_mode = candidate.design_variables["electronics_layout_mode"]
    if e_mode not in ["Stacked Above", "Stacked Below", "Side Mounted"]:
        a_min = coords["avionics_x"] - 0.05
        a_max = coords["avionics_x"] + 0.05
        if max(p_min, a_min) < min(p_max, a_max):
            return False, f"Payload [{p_min:.3f}, {p_max:.3f}] overlaps with Avionics [{a_min:.3f}, {a_max:.3f}]."
            
    return True, ""

def check_wing_spar_collision(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    coords = map_layout_coordinates(candidate, context)
    wing_x = coords["wing_x"]
    p_len, _ = get_component_lengths(context, "Longitudinal")
    
    p_min = coords["payload_x"] - p_len / 2.0
    p_max = coords["payload_x"] + p_len / 2.0
    
    if p_min <= wing_x <= p_max:
        return False, f"Wing spar position ({wing_x:.3f} m) intersects with Payload compartment [{p_min:.3f}, {p_max:.3f}]."
        
    return True, ""

def check_gps_interference(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    coords = map_layout_coordinates(candidate, context)
    gps_x = coords["gps_x"]
    bat_x = coords["battery_x"]
    
    dist = abs(gps_x - bat_x)
    if dist < 0.10:
        return False, f"GPS-to-Battery separation ({dist:.3f} m) is below safe electromagnetic threshold (0.10 m)."
        
    return True, ""

def check_boundary_fit(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    coords = map_layout_coordinates(candidate, context)
    nose_l = coords["nose_l"]
    cabin_end = nose_l + coords["cabin_l"]
    
    b_ori = candidate.design_variables["battery_orientation"]
    p_len, b_len = get_component_lengths(context, b_ori)
    
    p_min = coords["payload_x"] - p_len / 2.0
    p_max = coords["payload_x"] + p_len / 2.0
    
    b_min = coords["battery_x"] - b_len / 2.0
    b_max = coords["battery_x"] + b_len / 2.0
    
    if p_min < nose_l or p_max > cabin_end:
        return False, f"Payload compartment [{p_min:.3f}, {p_max:.3f}] exceeds cabin boundaries [{nose_l:.3f}, {cabin_end:.3f}]."
        
    if b_min < nose_l or b_max > cabin_end:
        return False, f"Battery compartment [{b_min:.3f}, {b_max:.3f}] exceeds cabin boundaries [{nose_l:.3f}, {cabin_end:.3f}]."
        
    return True, ""

def build_payload_constraints() -> ConstraintManager:
    manager = ConstraintManager()
    manager.add_constraint("overlap", check_overlap)
    manager.add_constraint("wing_spar_collision", check_wing_spar_collision)
    manager.add_constraint("gps_interference", check_gps_interference)
    manager.add_constraint("boundary_fit", check_boundary_fit)
    return manager
