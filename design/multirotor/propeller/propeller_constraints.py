import math
from backend.design.multirotor.propeller.propeller_models import PropellerCandidate, PropellerContext

class PropellerConstraintsEvaluator:
    """
    Enforces geometric, aerodynamic, and structural constraints for multirotor propellers.
    """
    @staticmethod
    def evaluate_constraints(candidate: PropellerCandidate, context: PropellerContext) -> bool:
        """
        Runs safety checks. Updates constraint results.
        """
        frame = context.frame_spec
        motor = context.motor_spec
        prop = candidate.propeller_record
        
        candidate.constraint_results = {}
        
        # 1. Propellers overlap / clearance check
        # Calculate hub distance between adjacent arms
        arm_count = frame.arm_count
        config_clean = frame.configuration.lower().replace(" ", "").replace("copter", "")
        effective_arms = 4 if "coaxial" in config_clean or "x8" in config_clean else arm_count
        theta = 360.0 / max(3, effective_arms)
        rad = math.radians(theta)
        
        d_hub = 2.0 * frame.arm_length_m * math.sin(rad / 2.0)
        
        prop_dia = prop.diameter_m
        tip_gap = d_hub - prop_dia
        
        clearance_passed = tip_gap >= 0.015  # at least 1.5 cm gap between tips
        candidate.constraint_results["PropellerClearance"] = {
            "status": "PASS" if clearance_passed else "FAIL",
            "reason": f"Tip gap: {tip_gap:.4f}m (Hub dist: {d_hub:.4f}m, Prop dia: {prop_dia:.4f}m)"
        }

        # 2. Tip speed safety check (must not exceed 220 m/s to prevent noise & shockwaves)
        tip_passed = candidate.tip_speed_m_s <= 220.0
        candidate.constraint_results["BladeTipSpeed"] = {
            "status": "PASS" if tip_passed else "FAIL",
            "reason": f"Max tip speed: {candidate.tip_speed_m_s:.1f} m/s (Limit: 220.0 m/s)"
        }

        # 3. Propeller structural RPM limit check
        rpm_passed = candidate.max_rpm <= prop.max_rpm
        candidate.constraint_results["PropellerRpmLimit"] = {
            "status": "PASS" if rpm_passed else "FAIL",
            "reason": f"Max RPM: {candidate.max_rpm:.0f} (Prop limit: {prop.max_rpm:.0f})"
        }

        # 4. Motor power loading compatibility check
        # Sized max power absorbed must not exceed motor power limit
        v_batt = 0.5 * (motor.voltage_range_v[0] + motor.voltage_range_v[1])
        # Sized motor continuous power capacity = power margin + hover electrical power
        p_motor_max = motor.power_margin_w + (motor.hover_current_a * v_batt)
        
        power_passed = candidate.max_power_absorbed_w <= p_motor_max * 1.50  # allow 50% burst peak power margin
        candidate.constraint_results["MotorPowerAbsorption"] = {
            "status": "PASS" if power_passed else "FAIL",
            "reason": f"Max Absorbed: {candidate.max_power_absorbed_w:.1f}W (Motor electrical limit: {p_motor_max:.1f}W)"
        }

        all_passed = clearance_passed and tip_passed and rpm_passed and power_passed
        candidate.constraints_passed = all_passed
        return all_passed
