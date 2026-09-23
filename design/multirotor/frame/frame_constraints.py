import math
from typing import Dict, Any
from backend.design.multirotor.frame.frame_models import FrameCandidate, FrameContext

class FrameConstraintsEvaluator:
    """
    Evaluates physical, geometric, and structural constraints for multirotor frames.
    """
    @staticmethod
    def evaluate_constraints(candidate: FrameCandidate, context: FrameContext) -> bool:
        """
        Runs constraint checks on a FrameCandidate. Updates candidate flags.
        """
        # Load profile and requirement constraints
        req = context.requirements
        profile = context.strategy_spec.constraint_summary
        
        geom = candidate.geometry
        wheelbase = geom.wheelbase_m
        config = geom.configuration.lower().replace(" ", "").replace("copter", "")
        
        candidate.constraint_results = {}
        
        # 1. Propeller clearance check
        # For N rotors, find adjacent arm angles
        arm_count = geom.arm_count
        # Coaxial X8 has 8 rotors but only 4 physical arms
        effective_arms = 4 if "coaxial" in config or "x8" in config else arm_count
        theta = 360.0 / max(3, effective_arms)
        rad = math.radians(theta)
        
        arm_len = geom.arm_length_m
        # Distance between adjacent motor hubs
        d_hub = 2.0 * arm_len * math.sin(rad / 2.0)
        
        # Max prop diameter we expect to mount
        # Let's read from the candidate's custom variables or set dynamically
        max_prop_d = candidate.design_variables.get("max_propeller_diameter_m", 0.0)
        if max_prop_d <= 0.0:
            # Sizing guess based on wheelbase
            max_prop_d = 0.40 * wheelbase
            
        tip_gap = d_hub - max_prop_d
        prop_passed = tip_gap >= 0.015  # at least 1.5 cm gap between tips
        candidate.prop_clearance_passed = prop_passed
        candidate.constraint_results["PropellerOverlap"] = {
            "status": "PASS" if prop_passed else "FAIL",
            "reason": f"Tip gap: {tip_gap:.4f}m (Hub dist: {d_hub:.4f}m, Prop dia: {max_prop_d:.4f}m)"
        }

        # 2. Payload Fit check
        payload_l, payload_w, payload_h = context.payload_dimensions_m
        bay_l, bay_w, bay_h = geom.payload_bay_dimensions_m
        
        payload_fits = (payload_l <= bay_l) and (payload_w <= bay_w) and (payload_h <= bay_h)
        candidate.payload_fit_passed = payload_fits
        candidate.constraint_results["PayloadFit"] = {
            "status": "PASS" if payload_fits else "FAIL",
            "reason": f"Payload ({payload_l}x{payload_w}x{payload_h}) Bay ({bay_l:.2f}x{bay_w:.2f}x{bay_h:.2f})"
        }

        # 3. Ground Clearance check
        # Must clear payload height + gimbal depth
        req_clearance = payload_h + 0.05
        clearance_passed = geom.ground_clearance_m >= req_clearance
        candidate.ground_clearance_passed = clearance_passed
        candidate.constraint_results["GroundClearance"] = {
            "status": "PASS" if clearance_passed else "FAIL",
            "reason": f"Ground clearance: {geom.ground_clearance_m:.2f}m (Required: {req_clearance:.2f}m)"
        }

        # 4. Maximum size limit check
        size_passed = wheelbase <= profile.maximum_frame_size_m
        candidate.size_limit_passed = size_passed
        candidate.constraint_results["MaximumFrameSize"] = {
            "status": "PASS" if size_passed else "FAIL",
            "reason": f"Wheelbase: {wheelbase:.2f}m (Max allowed: {profile.maximum_frame_size_m:.2f}m)"
        }

        # 5. Structural margin check (bending stress under 4.0g loading)
        # AUW estimate
        est_auw = context.payload_weight_kg * 3.5  # sizing rule of thumb
        est_auw = max(1.0, est_auw)
        
        g = 9.80665
        f_arm = (4.0 * est_auw * g) / max(3, effective_arms)
        m_bending = f_arm * arm_len
        
        # Sized arm tubes: carbon fiber (yield stress = 250 MPa)
        d_outer = geom.arm_diameter_m
        d_inner = d_outer - 2.0 * geom.arm_thickness_m
        
        inertia = (math.pi / 64.0) * (d_outer**4 - d_inner**4)
        if inertia > 0.0:
            stress = (m_bending * (d_outer / 2.0)) / inertia
        else:
            stress = float("inf")
            
        yield_stress = 2.5e8  # 250 MPa
        structural_sm = (yield_stress / max(1.0, stress)) - 1.0
        candidate.structural_margin = structural_sm
        
        struct_passed = structural_sm >= 0.0
        candidate.safety_margin_passed = struct_passed
        candidate.constraint_results["StructuralStrength"] = {
            "status": "PASS" if struct_passed else "FAIL",
            "reason": f"Arm Stress: {stress/1e6:.1f} MPa (Yield: {yield_stress/1e6:.1f} MPa, SM: {structural_sm:.2f})"
        }

        # All-up constraint check
        all_passed = prop_passed and payload_fits and clearance_passed and size_passed and struct_passed
        candidate.constraints_passed = all_passed
        return all_passed
