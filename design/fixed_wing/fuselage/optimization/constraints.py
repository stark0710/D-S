"""
Fixed-Wing Fuselage Sizing Constraints

Checks packaging clearances, tail stability margins, and internal volumes.
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.constraint_manager import ConstraintManager

def check_packaging_fit(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    reqs = context.requirements
    if not reqs:
        return True, ""
    
    m_profile = reqs.mission_result.mission_profile if reqs.mission_result else None
    if not m_profile:
        return True, ""
        
    payload_mass = m_profile.payload_kg
    clearance = 0.015
    
    w = candidate.design_variables["width"]
    h = candidate.design_variables["height"]
    l = candidate.design_variables["length"]
    
    # 1. Payload fit
    min_payload_width = 0.08 + (payload_mass * 0.005)
    if w - 2.0 * clearance < min_payload_width:
        return False, f"Fuselage width ({w:.2f} m) is insufficient for payload width ({min_payload_width:.2f} m)."
        
    # 2. Battery fit
    bat_vol = (l * 0.16) * (w - 2.0 * clearance) * (h * 0.55)
    if bat_vol < 0.0002:
        return False, f"Estimated battery volume ({bat_vol:.6f} m3) is below required limit (0.0002 m3)."
        
    return True, ""

def check_tail_arm(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    reqs = context.requirements
    if not reqs or not reqs.wing_result:
        return True, ""
        
    wing_geom = reqs.wing_result.wing_geometry
    span = wing_geom.span_m
    
    l = candidate.design_variables["length"]
    wing_attach_x = l * 0.32
    tail_attach_x = l * 0.95
    tail_arm = tail_attach_x - wing_attach_x

    # Pusher configurations require longer tail arm clearance (0.52 span) than tractor (0.30 span)
    cfg = getattr(reqs, "configuration_result", None) or getattr(context, "configuration", None)
    is_pusher = False
    if cfg:
        p_cfg = getattr(cfg, "propulsion_configuration", "") or getattr(cfg, "propulsion_layout", "")
        if not p_cfg and hasattr(cfg, "selected_configuration"):
            p_cfg = cfg.selected_configuration.get("propulsion_layout", "")
        is_pusher = "pusher" in p_cfg.lower()

    min_arm_ratio = 0.52 if is_pusher else 0.30
    min_tail_arm = span * min_arm_ratio

    if l * 0.85 < min_tail_arm or tail_arm < min_tail_arm:
        return False, f"Fuselage length ({l:.2f} m) cannot accommodate required tail arm ({min_tail_arm:.2f} m for {'pusher' if is_pusher else 'tractor'})."
        
    return True, ""

def check_internal_volume(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    w = candidate.design_variables["width"]
    h = candidate.design_variables["height"]
    l = candidate.design_variables["length"]
    nose_l = candidate.design_variables["nose_length"]
    tail_cone_l = candidate.design_variables["tail_cone_length"]
    
    total_vol = w * h * (l - 0.5 * (nose_l + tail_cone_l))
    if total_vol < 0.001:
        return False, f"Fuselage internal volume ({total_vol:.5f} m3) is below minimum threshold (0.001 m3)."
    return True, ""

def build_fuselage_constraints() -> ConstraintManager:
    manager = ConstraintManager()
    manager.add_constraint("packaging_fit", check_packaging_fit)
    manager.add_constraint("tail_arm", check_tail_arm)
    manager.add_constraint("internal_volume", check_internal_volume)
    return manager
