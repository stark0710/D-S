from backend.design.multirotor.battery.battery_models import BatteryCandidate, BatteryContext

class BatteryConstraintsEvaluator:
    """
    Enforces electrical, structural, and endurance constraints for Battery packs.
    """
    @staticmethod
    def evaluate_constraints(candidate: BatteryCandidate, context: BatteryContext) -> bool:
        """
        Runs safety checks. Updates constraint results.
        """
        motor = context.motor_spec
        batt = candidate.battery_record
        req = context.requirements
        
        candidate.constraint_results = {}
        
        # 1. Voltage range check
        voltage_passed = motor.voltage_range_v[0] <= batt.nominal_voltage_v <= motor.voltage_range_v[1]
        candidate.constraint_results["VoltageRange"] = {
            "status": "PASS" if voltage_passed else "FAIL",
            "reason": f"Battery Nominal voltage: {batt.nominal_voltage_v:.1f}V (Motor range: {motor.voltage_range_v[0]}-{motor.voltage_range_v[1]}V)"
        }

        # 2. Continuous discharge capability check
        continuous_passed = candidate.hover_current_draw_a <= candidate.continuous_discharge_limit_a
        candidate.constraint_results["ContinuousDischarge"] = {
            "status": "PASS" if continuous_passed else "FAIL",
            "reason": f"Hover Draw: {candidate.hover_current_draw_a:.1f}A (Continuous capacity: {candidate.continuous_discharge_limit_a:.1f}A)"
        }

        # 3. Peak / Burst discharge capability check
        burst_passed = candidate.max_current_draw_a <= candidate.burst_discharge_limit_a
        candidate.constraint_results["BurstDischarge"] = {
            "status": "PASS" if burst_passed else "FAIL",
            "reason": f"Max Climb Draw: {candidate.max_current_draw_a:.1f}A (Burst capacity: {candidate.burst_discharge_limit_a:.1f}A)"
        }

        # 4. Structural Max Takeoff Weight check
        # Takeoff weight must be within design limits (max takeoff weight constraint)
        max_takeoff = req.maximum_takeoff_weight_kg if req.maximum_takeoff_weight_kg else 25.0
        weight_passed = candidate.estimated_auw_kg <= max_takeoff
        candidate.constraint_results["StructuralWeight"] = {
            "status": "PASS" if weight_passed else "FAIL",
            "reason": f"Estimated AUW: {candidate.estimated_auw_kg:.2f} kg (Max MTOW: {max_takeoff:.2f} kg)"
        }

        # 5. Flight time check (warning/advisory, not a hard blocking failure to avoid over-constrained traps)
        target_time = req.target_flight_time_min if req.target_flight_time_min else 20.0
        time_passed = candidate.estimated_flight_time_min >= target_time
        candidate.constraint_results["FlightTimeAdvisory"] = {
            "status": "PASS" if time_passed else "WARNING",
            "reason": f"Flight time: {candidate.estimated_flight_time_min:.1f} min (Target: {target_time:.1f} min)"
        }

        # Voltage, discharge capability, and structural weight are absolute safety limits
        all_passed = voltage_passed and continuous_passed and burst_passed and weight_passed
        candidate.constraints_passed = all_passed
        return all_passed
