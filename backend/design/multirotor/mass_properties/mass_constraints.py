from backend.design.multirotor.mass_properties.mass_models import MassPropertiesCandidate, MassPropertiesContext

class MassConstraintsEvaluator:
    """
    Enforces center of gravity bounds, weight limit constraints, and realistic mass fraction checks.
    """
    @staticmethod
    def evaluate_constraints(candidate: MassPropertiesCandidate, context: MassPropertiesContext) -> bool:
        """
        Runs safety checks. Updates constraint results.
        """
        req = context.requirements
        breakdown = candidate.weight_breakdown
        
        candidate.constraint_results = {}
        
        # 1. CG lateral offset checks (must be <= 2cm from central origin)
        cg_x_passed = abs(candidate.cg_x_m) <= 0.02
        candidate.constraint_results["CgXEnvelope"] = {
            "status": "PASS" if cg_x_passed else "FAIL",
            "reason": f"X_cg offset: {candidate.cg_x_m*100:.1f} cm (Limit: <= 2.0 cm)"
        }
        
        cg_y_passed = abs(candidate.cg_y_m) <= 0.02
        candidate.constraint_results["CgYEnvelope"] = {
            "status": "PASS" if cg_y_passed else "FAIL",
            "reason": f"Y_cg offset: {candidate.cg_y_m*100:.1f} cm (Limit: <= 2.0 cm)"
        }

        # 2. Maximum design weight check
        max_takeoff = req.maximum_takeoff_weight_kg if req.maximum_takeoff_weight_kg else 25.0
        weight_passed = breakdown.total_mass_kg <= max_takeoff
        candidate.constraint_results["MaxTakeoffWeight"] = {
            "status": "PASS" if weight_passed else "FAIL",
            "reason": f"Total Mass: {breakdown.total_mass_kg:.2f} kg (Max MTOW: {max_takeoff:.2f} kg)"
        }

        # 3. Mass fraction realism limits
        # Structural fraction (frame + cables) should be between 1% and 45%
        structural_passed = 0.01 <= breakdown.structural_fraction <= 0.45
        candidate.constraint_results["StructuralFractionLimit"] = {
            "status": "PASS" if structural_passed else "FAIL",
            "reason": f"Structural fraction: {breakdown.structural_fraction*100:.1f}% (Limit: 1.0% to 45.0%)"
        }
        
        # Battery fraction should be between 1% and 55%
        battery_passed = 0.01 <= breakdown.battery_fraction <= 0.55
        candidate.constraint_results["BatteryFractionLimit"] = {
            "status": "PASS" if battery_passed else "FAIL",
            "reason": f"Battery fraction: {breakdown.battery_fraction*100:.1f}% (Limit: 1.0% to 55.0%)"
        }

        # Payload fraction should be between 1% and 60%
        payload_passed = 0.01 <= breakdown.payload_fraction <= 0.60
        candidate.constraint_results["PayloadFractionLimit"] = {
            "status": "PASS" if payload_passed else "FAIL",
            "reason": f"Payload fraction: {breakdown.payload_fraction*100:.1f}% (Limit: 1.0% to 60.0%)"
        }

        all_passed = cg_x_passed and cg_y_passed and weight_passed and structural_passed and battery_passed and payload_passed
        candidate.constraints_passed = all_passed
        return all_passed
