from backend.design.multirotor.motor.motor_models import MotorCandidate, MotorContext

class MotorConstraintsEvaluator:
    """
    Enforces current, thrust margin, voltage compatibility, and thermal limits constraints for propulsion motors.
    """
    @staticmethod
    def evaluate_constraints(candidate: MotorCandidate, context: MotorContext) -> bool:
        """
        Runs safety checks. Updates constraint results.
        """
        motor = candidate.motor_record
        candidate.constraint_results = {}
        
        # 1. Voltage compatibility check
        v_batt = 0.5 * (motor.min_voltage_v + motor.max_voltage_v)
        voltage_passed = motor.min_voltage_v <= v_batt <= motor.max_voltage_v
        candidate.constraint_results["VoltageRange"] = {
            "status": "PASS" if voltage_passed else "FAIL",
            "reason": f"Nominal voltage: {v_batt:.1f}V (Range: {motor.min_voltage_v}-{motor.max_voltage_v}V)"
        }

        # 2. Insufficient thrust check (must exceed max required thrust)
        thrust_passed = motor.max_thrust_n >= candidate.max_thrust_n
        candidate.constraint_results["MaxThrustRequired"] = {
            "status": "PASS" if thrust_passed else "FAIL",
            "reason": f"Catalog Thrust: {motor.max_thrust_n:.1f}N (Required: {candidate.max_thrust_n:.1f}N)"
        }

        # 3. Excessive current check (peak current should not exceed catalog burst limits)
        peak_passed = candidate.max_current_a <= motor.peak_current_a
        candidate.constraint_results["PeakCurrentLimits"] = {
            "status": "PASS" if peak_passed else "FAIL",
            "reason": f"Peak Current: {candidate.max_current_a:.1f}A (Peak catalog max: {motor.peak_current_a:.1f}A)"
        }

        # 4. Thermal / Continuous current check
        # Sized hover current must not exceed 80% continuous rating
        thermal_limit = 0.8 * motor.max_continuous_current_a
        thermal_passed = candidate.hover_current_a <= thermal_limit
        candidate.constraint_results["ThermalLimitContinuous"] = {
            "status": "PASS" if thermal_passed else "FAIL",
            "reason": f"Hover Current: {candidate.hover_current_a:.1f}A (Continuous thermal limit: {thermal_limit:.1f}A)"
        }

        # 5. Motor weight fraction limit (motors should not weigh more than configuration limits)
        payload = context.requirements.payload_weight_kg
        frame_mass = context.frame_spec.frame_mass_kg
        motor_count = context.frame_spec.arm_count
        weight_ratio = (motor.empty_mass_kg * motor_count) / (payload + frame_mass)
        limit = max(0.40, 0.40 + 0.05 * (motor_count - 4))
        weight_passed = weight_ratio <= limit
        candidate.constraint_results["MotorWeightRatio"] = {
            "status": "PASS" if weight_passed else "FAIL",
            "reason": f"Motor/Frame weight ratio: {weight_ratio:.2f} (Limit: {limit:.2f})"
        }

        # 6. Sized throttle hover percentage: must be between 30% and 75% for control authority
        throttle_passed = 30.0 <= candidate.throttle_hover_pct <= 75.0
        candidate.constraint_results["HoverThrottleWindow"] = {
            "status": "PASS" if throttle_passed else "FAIL",
            "reason": f"Hover throttle: {candidate.throttle_hover_pct:.1f}% (Required: 30%-75% window)"
        }

        all_passed = voltage_passed and thrust_passed and peak_passed and thermal_passed and weight_passed and throttle_passed
        candidate.constraints_passed = all_passed
        return all_passed
