from backend.design.multirotor.esc.esc_models import EscCandidate, EscContext

class EscConstraintsEvaluator:
    """
    Enforces electrical, thermal, and protocol constraints for Electronic Speed Controllers (ESCs).
    """
    @staticmethod
    def evaluate_constraints(candidate: EscCandidate, context: EscContext) -> bool:
        """
        Runs safety checks. Updates constraint results.
        """
        motor = context.motor_spec
        esc = candidate.esc_record
        
        candidate.constraint_results = {}
        
        # 1. Voltage compatibility check
        v_batt = 0.5 * (motor.voltage_range_v[0] + motor.voltage_range_v[1])
        voltage_passed = esc.min_voltage_v <= v_batt <= esc.max_voltage_v
        candidate.constraint_results["VoltageRange"] = {
            "status": "PASS" if voltage_passed else "FAIL",
            "reason": f"Nominal voltage: {v_batt:.1f}V (ESC Range: {esc.min_voltage_v}-{esc.max_voltage_v}V)"
        }

        # 2. Sized continuous current check (continuous load <= 85%)
        continuous_limit = 0.85 * esc.continuous_current_a
        continuous_passed = candidate.hover_current_a <= continuous_limit
        candidate.constraint_results["ContinuousCurrentLimit"] = {
            "status": "PASS" if continuous_passed else "FAIL",
            "reason": f"Hover Current: {candidate.hover_current_a:.1f}A (Continuous limit: {continuous_limit:.1f}A)"
        }

        # 3. Peak / Burst current check
        burst_passed = candidate.max_current_a <= esc.burst_current_a
        candidate.constraint_results["BurstCurrentLimit"] = {
            "status": "PASS" if burst_passed else "FAIL",
            "reason": f"Max Peak Current: {candidate.max_current_a:.1f}A (ESC Burst rating: {esc.burst_current_a:.1f}A)"
        }

        # 4. Signaling protocol compatibility check
        # Large heavy lift motors (low KV) typically use industrial Flame ESCs supporting PWM only
        pref_protocol = context.requirements.metadata.get("signaling_protocol", "DShot600")
        
        # If low KV, automatically allow fallback to PWM
        is_heavy_lift = motor.kv < 300.0
        protocol_passed = (
            pref_protocol in esc.supported_protocols or 
            (is_heavy_lift and "PWM" in esc.supported_protocols) or
            "PWM" in esc.supported_protocols
        )
        
        candidate.constraint_results["ProtocolSupport"] = {
            "status": "PASS" if protocol_passed else "FAIL",
            "reason": f"Preferred protocol: {pref_protocol} (Supported: {', '.join(esc.supported_protocols)})"
        }

        all_passed = voltage_passed and continuous_passed and burst_passed and protocol_passed
        candidate.constraints_passed = all_passed
        return all_passed
