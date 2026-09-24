"""
Fixed-Wing Tail Optimization Constraints

Rejects candidate tail designs with infeasible geometry, insufficient stability,
or manufacturing violations.

Each constraint function has the shared-framework signature:
    (candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]
"""

import math
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.constraint_manager import ConstraintManager


# ---------------------------------------------------------------------------
#  Helper — compute empennage geometry from design variables
# ---------------------------------------------------------------------------

def compute_tail_geometry(candidate: OptimizationCandidate,
                          context: OptimizationContext) -> dict:
    """
    Derives horizontal and vertical tail areas, spans, and chords from
    the candidate design variables and the upstream wing specification.
    Uses the same equations as TailSizer to guarantee consistency.
    """
    wing_spec = None
    if context.previous_specifications:
        wing_spec = context.previous_specifications.get("WingPlanformOptimizer")

    wing_area = getattr(wing_spec, "area_m2", 0.4)
    mac = getattr(wing_spec, "mean_aerodynamic_chord_m", 0.22)
    wingspan = getattr(wing_spec, "span_m", 2.0)

    dv = candidate.design_variables
    V_h = dv["horizontal_V_h"]
    V_v = dv["vertical_V_v"]
    arm_ratio = dv["tail_arm_ratio"]
    h_ar = dv["horiz_ar"]
    v_ar = dv["vert_ar"]
    h_taper = dv["horiz_taper"]
    v_taper = dv["vert_taper"]

    tail_arm = arm_ratio * wingspan

    # Horizontal tail area: S_h = (V_h * S * c_mac) / l_t
    h_area = (V_h * wing_area * mac) / tail_arm if tail_arm > 0 else 0.0

    # Vertical tail area: S_v = (V_v * S * b) / l_t
    v_area = (V_v * wing_area * wingspan) / tail_arm if tail_arm > 0 else 0.0

    # Horizontal geometry
    if h_area > 0.0 and h_ar > 0.0:
        h_span = math.sqrt(h_area * h_ar)
        h_root = (2.0 * h_area) / (h_span * (1.0 + h_taper)) if h_span > 0 else 0.0
        h_tip = h_taper * h_root
    else:
        h_span = h_root = h_tip = 0.0

    # Vertical geometry
    if v_area > 0.0 and v_ar > 0.0:
        v_height = math.sqrt(v_area * v_ar)
        v_root = (2.0 * v_area) / (v_height * (1.0 + v_taper)) if v_height > 0 else 0.0
        v_tip = v_taper * v_root
    else:
        v_height = v_root = v_tip = 0.0

    return {
        "h_area": h_area,
        "v_area": v_area,
        "h_span": h_span,
        "h_root": h_root,
        "h_tip": h_tip,
        "v_height": v_height,
        "v_root": v_root,
        "v_tip": v_tip,
        "wingspan": wingspan,
        "wing_area": wing_area,
        "mac": mac,
        "tail_arm": tail_arm,
        "V_h": V_h,
        "V_v": V_v,
    }


# ---------------------------------------------------------------------------
#  Individual constraint functions
# ---------------------------------------------------------------------------

def check_configuration_compatibility(
    candidate: OptimizationCandidate, context: OptimizationContext
) -> tuple[bool, str]:
    """Reject configurations incompatible with the aircraft's declared layout."""
    config_result = context.configuration
    declared_tail = getattr(config_result, "tail_configuration", "Conventional")
    candidate_tail = candidate.design_variables["tail_configuration"]

    # Accept the declared configuration and the universal Conventional fallback
    compatible = {declared_tail, "Conventional"}
    if candidate_tail not in compatible:
        return False, (
            f"Tail configuration '{candidate_tail}' is incompatible with "
            f"declared aircraft layout '{declared_tail}'."
        )
    return True, ""


def check_static_margin(
    candidate: OptimizationCandidate, context: OptimizationContext
) -> tuple[bool, str]:
    """Reject designs with V_h outside acceptable longitudinal stability bounds."""
    V_h = candidate.design_variables["horizontal_V_h"]
    if V_h < 0.35:
        return False, f"Horizontal volume coefficient V_h ({V_h:.3f}) below minimum 0.35."
    if V_h > 0.90:
        return False, f"Horizontal volume coefficient V_h ({V_h:.3f}) above maximum 0.90."
    return True, ""


def check_directional_stability(
    candidate: OptimizationCandidate, context: OptimizationContext
) -> tuple[bool, str]:
    """Reject designs with V_v outside acceptable directional stability bounds."""
    V_v = candidate.design_variables["vertical_V_v"]
    if V_v < 0.02:
        return False, f"Vertical volume coefficient V_v ({V_v:.3f}) below minimum 0.02."
    if V_v > 0.08:
        return False, f"Vertical volume coefficient V_v ({V_v:.3f}) above maximum 0.08."
    return True, ""


def check_tail_span_ratio(
    candidate: OptimizationCandidate, context: OptimizationContext
) -> tuple[bool, str]:
    """Reject designs where horizontal tail span exceeds 70% of wingspan."""
    geom = compute_tail_geometry(candidate, context)
    if geom["wingspan"] > 0.0 and geom["h_span"] > 0.0:
        ratio = geom["h_span"] / geom["wingspan"]
        if ratio > 0.70:
            return False, (
                f"Horizontal tail span ({geom['h_span']:.3f} m) is "
                f"{ratio * 100:.1f}% of wingspan ({geom['wingspan']:.3f} m), "
                f"exceeding 70% limit."
            )
    return True, ""


def check_chord_minimums(
    candidate: OptimizationCandidate, context: OptimizationContext
) -> tuple[bool, str]:
    """Reject designs with any chord below the manufacturing minimum (0.02 m)."""
    geom = compute_tail_geometry(candidate, context)
    min_chord = 0.02
    violations = []

    if geom["h_area"] > 0.0:
        if geom["h_root"] < min_chord:
            violations.append(f"H-tail root chord ({geom['h_root']:.4f} m)")
        if geom["h_tip"] < min_chord:
            violations.append(f"H-tail tip chord ({geom['h_tip']:.4f} m)")

    if geom["v_area"] > 0.0:
        if geom["v_root"] < min_chord:
            violations.append(f"V-tail root chord ({geom['v_root']:.4f} m)")
        if geom["v_tip"] < min_chord:
            violations.append(f"V-tail tip chord ({geom['v_tip']:.4f} m)")

    if violations:
        return False, f"Chord(s) below manufacturing minimum ({min_chord} m): {', '.join(violations)}."
    return True, ""


def check_tail_arm_bounds(
    candidate: OptimizationCandidate, context: OptimizationContext
) -> tuple[bool, str]:
    """Reject designs where the tail arm exceeds the fuselage tail cone."""
    fuse_spec = None
    if context.previous_specifications:
        fuse_spec = context.previous_specifications.get("FuselageOptimizer")
    overall_length = getattr(fuse_spec, "overall_length", 1.5)

    geom = compute_tail_geometry(candidate, context)
    if geom["tail_arm"] > 0.85 * overall_length:
        return False, (
            f"Tail arm ({geom['tail_arm']:.3f} m) exceeds 85% of "
            f"fuselage length ({overall_length:.3f} m)."
        )
    if geom["tail_arm"] < 0.20:
        return False, f"Tail arm ({geom['tail_arm']:.3f} m) below 0.20 m structural minimum."
    return True, ""


def check_tail_to_propeller(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    """Reject candidates where the tail is too close to a pusher propeller."""
    config_result = context.configuration
    prop_layout = "Tractor"
    if config_result:
        prop_layout = getattr(config_result, "propulsion_configuration", "") or getattr(config_result, "propulsion_layout", "") or "Tractor"
        # Also check dictionary if it exists
        sel_cfg = getattr(config_result, "selected_configuration", {}) or {}
        if not prop_layout or prop_layout == "Tractor":
            prop_layout = sel_cfg.get("propulsion_layout", sel_cfg.get("propulsion_configuration", "Tractor"))
    
    geom = compute_tail_geometry(candidate, context)
    
    # If it is a Pusher or Twin Boom Pusher layout, tail arm must be long enough
    if "Pusher" in prop_layout or prop_layout == "Pusher":
        # Tail arm ratio must be at least 0.52 to avoid prop wash / propeller path
        tail_arm_ratio = candidate.design_variables["tail_arm_ratio"]
        if tail_arm_ratio < 0.52:
            return False, f"Tail arm ratio ({tail_arm_ratio:.3f}) too short for {prop_layout} layout (minimum 0.52)."
    return True, ""


def check_ground_clearance(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    """Reject designs with insufficient ground clearance or invalid dihedral angles."""
    geom = compute_tail_geometry(candidate, context)
    dv = candidate.design_variables
    config = dv["tail_configuration"]
    dihedral = dv.get("tail_dihedral_deg", 0.0)
    
    # Check dihedral bounds per configuration
    if config in ("Conventional", "T-Tail", "Twin Boom"):
        if abs(dihedral) > 10.0:
            return False, f"Dihedral angle ({dihedral:.1f}°) for {config} tail must be within [-10, 10] degrees."
    elif config == "V-Tail":
        if dihedral < 30.0 or dihedral > 50.0:
            return False, f"Dihedral angle ({dihedral:.1f}°) for V-Tail must be within [30, 50] degrees."
    elif config == "Inverted V-Tail":
        if dihedral < -50.0 or dihedral > -30.0:
            return False, f"Dihedral angle ({dihedral:.1f}°) for Inverted V-Tail must be within [-50, -30] degrees."
            
    # For Inverted V-Tail, check downward tip clearance
    if config == "Inverted V-Tail":
        v_height = geom["v_height"]
        downward_projection = v_height * math.sin(math.radians(abs(dihedral)))
        # Reject if downward projection is > 0.40m
        if downward_projection > 0.40:
            return False, f"Inverted V-Tail downward tip projection ({downward_projection:.3f} m) exceeds 0.40 m limit."
            
    return True, ""


def check_structural_integration(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    """Reject configurations structurally incompatible with wing/fuselage structures."""
    dv = candidate.design_variables
    config = dv["tail_configuration"]
    
    wing_spec = None
    if context.previous_specifications:
        wing_spec = context.previous_specifications.get("WingPlanformOptimizer")
    aspect_ratio = getattr(wing_spec, "aspect_ratio", 10.0)
    
    # Twin Boom layout structurally incompatible with extremely high aspect ratio wings
    if config == "Twin Boom" and aspect_ratio > 18.0:
        return False, f"Twin Boom configuration structurally incompatible with high wing aspect ratio ({aspect_ratio:.1f})."
        
    return True, ""


def check_boom_geometry(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    """Reject designs where boom length or mounting geometry is invalid."""
    dv = candidate.design_variables
    config = dv["tail_configuration"]
    arm_ratio = dv["tail_arm_ratio"]
    
    # Twin Boom layout requires boom length ratio within specific limits
    if config == "Twin Boom":
        if arm_ratio < 0.50 or arm_ratio > 0.65:
            return False, f"Twin Boom length ratio ({arm_ratio:.3f}) must be within [0.50, 0.65] range."
            
    return True, ""


def check_control_surfaces_fit(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    """Reject designs if aspect ratio is too high, causing chords to be too thin to fit control surfaces."""
    geom = compute_tail_geometry(candidate, context)
    
    # Check if horizontal tail chord is too narrow
    if geom["h_area"] > 0.0:
        h_chord_avg = geom["h_area"] / geom["h_span"] if geom["h_span"] > 0 else 0.0
        if h_chord_avg < 0.035:
            return False, f"Horizontal tail chord average ({h_chord_avg:.4f} m) too thin to fit control surfaces (minimum 0.035 m)."
            
    if geom["v_area"] > 0.0:
        v_chord_avg = geom["v_area"] / geom["v_height"] if geom["v_height"] > 0 else 0.0
        if v_chord_avg < 0.030:
            return False, f"Vertical tail chord average ({v_chord_avg:.4f} m) too thin to fit control surfaces (minimum 0.030 m)."
            
    return True, ""


def check_servo_installation(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    """Reject if tip chord or average chord is too small for servo installation."""
    geom = compute_tail_geometry(candidate, context)
    min_tip = 0.03
    if geom["h_area"] > 0.0 and geom["h_tip"] < min_tip:
        return False, f"Horizontal tip chord ({geom['h_tip']:.4f} m) too small for servo installation (minimum {min_tip} m)."
    if geom["v_area"] > 0.0 and geom["v_tip"] < min_tip:
        return False, f"Vertical tip chord ({geom['v_tip']:.4f} m) too small for servo installation (minimum {min_tip} m)."
    return True, ""


def check_manufacturing_feasibility(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    """Reject candidates with sweep too high (> 20 degrees) or complex angles for manufacturing."""
    dv = candidate.design_variables
    horiz_sweep = dv["horiz_sweep"]
    vert_sweep = dv["vert_sweep"]
    
    if horiz_sweep > 20.0:
        return False, f"Horizontal sweep ({horiz_sweep:.1f}°) exceeds 20.0° manufacturing limit."
    if vert_sweep > 20.0:
        return False, f"Vertical sweep ({vert_sweep:.1f}°) exceeds 20.0° manufacturing limit."
        
    return True, ""


# ---------------------------------------------------------------------------
#  Factory
# ---------------------------------------------------------------------------

def build_tail_constraints() -> ConstraintManager:
    """Builds and returns a ConstraintManager pre-loaded with tail feasibility rules."""
    manager = ConstraintManager()
    manager.add_constraint("configuration_compatibility", check_configuration_compatibility)
    manager.add_constraint("static_margin", check_static_margin)
    manager.add_constraint("directional_stability", check_directional_stability)
    manager.add_constraint("tail_span_ratio", check_tail_span_ratio)
    manager.add_constraint("chord_minimums", check_chord_minimums)
    manager.add_constraint("tail_arm_bounds", check_tail_arm_bounds)
    manager.add_constraint("tail_to_propeller", check_tail_to_propeller)
    manager.add_constraint("ground_clearance", check_ground_clearance)
    manager.add_constraint("structural_integration", check_structural_integration)
    manager.add_constraint("boom_geometry", check_boom_geometry)
    manager.add_constraint("control_surfaces_fit", check_control_surfaces_fit)
    manager.add_constraint("servo_installation", check_servo_installation)
    manager.add_constraint("manufacturing_feasibility", check_manufacturing_feasibility)
    return manager
