"""
Fixed-Wing Wing Planform Sizing Constraints

Checks that wing planforms satisfy physical, manufacturing, and aerodynamic bounds.
Enforces screening checks before full engine evaluations.
"""

import math
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.constraint_manager import ConstraintManager

def check_manufacturing_limits(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    taper = candidate.design_variables.get("taper_ratio", 0.5)
    if taper < 0.35 or taper > 1.0:
        return False, f"Taper ratio ({taper}) is outside manufacturing bounds [0.35, 1.00]."
    return True, ""

def check_analytical_geometry(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
    # Extract requirements and constraints
    reqs = context.requirements
    if not reqs:
        return True, ""

    m_profile = reqs.mission_result.mission_profile
    g = 9.80665
    rho = m_profile.air_density_kg_m3 or 1.225
    c_l_max = 1.4

    # 1. Determine wing loading and area
    mtow = (
        getattr(m_profile, "current_iteration_mtow_kg", None)
        or getattr(m_profile, "initial_mtow_seed_kg", None)
        or m_profile.maximum_takeoff_weight_limit_kg
        or max(2.0, getattr(m_profile, "payload_kg", 1.0) * 3.5)
    )
    if m_profile.stall_speed_target_kmh:
        v_stall = m_profile.stall_speed_target_kmh / 3.6
        wing_loading_kg = (0.5 * rho * v_stall**2 * c_l_max) / g
    else:
        v_cruise = m_profile.cruise_speed_kmh / 3.6
        v_stall = v_cruise / 1.5
        wing_loading_kg = (0.5 * rho * v_stall**2 * c_l_max) / g

    # Fallback/Overrides
    if reqs.preferred_wing_loading is not None:
        wing_loading_kg = reqs.preferred_wing_loading

    area = mtow / max(0.1, wing_loading_kg)
    ar = candidate.design_variables.get("aspect_ratio", 10.0)
    taper = candidate.design_variables.get("taper_ratio", 0.5)

    span = math.sqrt(area * ar)
    
    # Check max wingspan constraint if set in metadata/constraints
    max_span = reqs.metadata.get("max_wingspan_m")
    if max_span is not None and span > max_span:
        return False, f"Estimated wingspan ({span:.2f} m) exceeds maximum constraint limit ({max_span} m)."

    # Calculate chords
    root_chord = (2.0 * area) / (span * (1.0 + taper))
    tip_chord = taper * root_chord

    if root_chord < 0.05:
        return False, f"Estimated root chord ({root_chord:.3f} m) is below minimum allowable limit (0.05 m)."
    if tip_chord < 0.05:
        return False, f"Estimated tip chord ({tip_chord:.3f} m) is below minimum allowable limit (0.05 m)."

    # Enforce geometric coupling: root chord must comfortably accommodate fuselage width
    payload_mass = getattr(m_profile, "payload_kg", 1.0)
    min_payload_width = 0.08 + (payload_mass * 0.005)
    clearance_margin = 0.02
    min_fuse_width = min_payload_width + 2.0 * clearance_margin
    fuse_res = getattr(reqs, "fuselage_result", None)
    if fuse_res and hasattr(fuse_res, "fuselage_geometry"):
        min_fuse_width = max(min_fuse_width, fuse_res.fuselage_geometry.width_m)

    min_required_root_chord = min_fuse_width * 1.10
    if root_chord < min_required_root_chord:
        return False, (
            f"Estimated wing root chord ({root_chord:.3f} m) is insufficient for fuselage envelope "
            f"({min_required_root_chord:.3f} m, representing a 10% margin over {min_fuse_width:.3f} m)."
        )

    return True, ""

def build_wing_constraints() -> ConstraintManager:
    manager = ConstraintManager()
    manager.add_constraint("manufacturing_limits", check_manufacturing_limits)
    manager.add_constraint("analytical_geometry", check_analytical_geometry)
    return manager
