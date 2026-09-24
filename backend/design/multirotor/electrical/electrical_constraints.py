from backend.design.multirotor.electrical.electrical_models import ElectricalCandidate, ElectricalContext

class ElectricalConstraintsEvaluator:
    """
    Enforces electrical safety, current capacities, voltage drop limits, and BEC capacity constraint rules.
    """
    @staticmethod
    def evaluate_constraints(candidate: ElectricalCandidate, context: ElectricalContext) -> bool:
        """
        Runs safety checks. Updates constraint results.
        """
        assembly = context.propulsion_assembly
        battery = assembly.battery
        
        candidate.constraint_results = {}
        
        # 1. Wire continuous current capacity checks
        # Main wire handles total hover current
        main_passed = candidate.main_wire.max_continuous_current_a >= assembly.hover_current_total_a
        candidate.constraint_results["MainWireCapacity"] = {
            "status": "PASS" if main_passed else "FAIL",
            "reason": f"Total Hover: {assembly.hover_current_total_a:.1f}A (Main wire AWG {candidate.main_wire.awg} limit: {candidate.main_wire.max_continuous_current_a:.1f}A)"
        }
        
        # ESC wire handles individual ESC current
        i_esc_hover = assembly.hover_current_total_a / context.frame_spec.arm_count
        esc_passed = candidate.esc_wire.max_continuous_current_a >= i_esc_hover
        candidate.constraint_results["EscWireCapacity"] = {
            "status": "PASS" if esc_passed else "FAIL",
            "reason": f"ESC Hover: {i_esc_hover:.1f}A (ESC wire AWG {candidate.esc_wire.awg} limit: {candidate.esc_wire.max_continuous_current_a:.1f}A)"
        }

        # 2. Voltage drop limit checks (must be <= 3% of nominal battery voltage)
        v_limit = 0.03 * battery.voltage
        main_drop_passed = candidate.main_voltage_drop_v <= v_limit
        candidate.constraint_results["MainVoltageDrop"] = {
            "status": "PASS" if main_drop_passed else "FAIL",
            "reason": f"Main Drop: {candidate.main_voltage_drop_v:.3f}V (Limit: {v_limit:.3f}V)"
        }
        
        esc_drop_passed = candidate.esc_voltage_drop_v <= v_limit
        candidate.constraint_results["EscVoltageDrop"] = {
            "status": "PASS" if esc_drop_passed else "FAIL",
            "reason": f"ESC Drop: {candidate.esc_voltage_drop_v:.3f}V (Limit: {v_limit:.3f}V)"
        }

        # 3. Connector current capacity checks
        batt_conn_passed = candidate.battery_connector.max_continuous_current_a >= assembly.hover_current_total_a
        candidate.constraint_results["BatteryConnectorCapacity"] = {
            "status": "PASS" if batt_conn_passed else "FAIL",
            "reason": f"Total Hover: {assembly.hover_current_total_a:.1f}A (Battery connector {candidate.battery_connector.name} limit: {candidate.battery_connector.max_continuous_current_a:.1f}A)"
        }

        # 4. BEC Capacity margins (minimum 10% safety margin)
        bec_5v_passed = candidate.power_budget.bec_margin_5v_pct >= 10.0
        candidate.constraint_results["BecAvionicsMargin"] = {
            "status": "PASS" if bec_5v_passed else "FAIL",
            "reason": f"BEC 5V Margin: {candidate.power_budget.bec_margin_5v_pct:.1f}% (Minimum: 10.0%)"
        }

        all_passed = main_passed and esc_passed and main_drop_passed and esc_drop_passed and batt_conn_passed and bec_5v_passed
        candidate.constraints_passed = all_passed
        return all_passed
