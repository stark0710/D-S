from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.multirotor.electrical.electrical_models import ElectricalContext, ElectricalCandidate
from backend.design.multirotor.electrical.wiring_optimizer import WiringOptimizer, CatalogWireRecord
from backend.design.multirotor.electrical.connector_selector import ConnectorSelector, CatalogConnectorRecord
from backend.design.multirotor.electrical.power_distribution import PowerDistributionSizer, PowerDistributionBudget
from backend.design.multirotor.electrical.electrical_constraints import ElectricalConstraintsEvaluator
from backend.design.multirotor.electrical.electrical_validator import ElectricalValidator
from backend.design.multirotor.electrical.electrical_result import ElectricalSpecification

class ElectricalEngine(OptimizerBase):
    """
    Multidisciplinary Power Distribution & Electrical Integration Optimization Engine.
    Adapts the shared OptimizerBase template method lifecycle.
    """
    def __init__(self, name: str = "ElectricalEngine") -> None:
        super().__init__(name)
        self._wiring_opt = WiringOptimizer()
        self._connector_sel = ConnectorSelector()
        self._validator = ElectricalValidator()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Generates wiring gauge configuration combinations.
        """
        assert isinstance(context, ElectricalContext)
        
        assembly = context.propulsion_assembly
        arm_count = context.frame_spec.arm_count
        
        # 1. Budget power distribution requirements
        esc_has_bec = assembly.esc.bec != "None"
        budget = PowerDistributionSizer.size_power_distribution(
            payload_weight_kg=context.requirements.payload_weight_kg,
            arm_count=arm_count,
            esc_has_bec=esc_has_bec
        )
        
        # 2. Select optimal connectors
        batt_conn = self._connector_sel.select_connector_for_current(assembly.hover_current_total_a, is_motor_phase=False)
        
        i_motor_hover = assembly.hover_current_total_a / arm_count
        motor_conn = self._connector_sel.select_connector_for_current(i_motor_hover, is_motor_phase=True)
        
        # 3. Generate wire configurations (evaluating combinations of main and esc gauges)
        candidates: List[OptimizationCandidate] = []
        wires = self._wiring_opt.get_all_wires()
        
        for main_wire in wires:
            for esc_wire in wires:
                # Motor wire typically matches ESC wire or fits next gauge
                motor_wire = esc_wire
                
                d_vars = {
                    "main_awg": main_wire.awg,
                    "esc_awg": esc_wire.awg,
                    "motor_awg": motor_wire.awg,
                    "battery_connector": batt_conn.name,
                    "motor_connector": motor_conn.name
                }
                
                cand = ElectricalCandidate(design_variables=d_vars)
                cand.main_wire = main_wire
                cand.esc_wire = esc_wire
                cand.motor_wire = motor_wire
                cand.battery_connector = batt_conn
                cand.motor_connector = motor_conn
                cand.power_budget = budget
                candidates.append(cand)
                
        return candidates

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Redirects to constraints checkers.
        """
        assert isinstance(candidate, ElectricalCandidate)
        assert isinstance(context, ElectricalContext)
        
        if candidate.wiring_power_loss_w == 0.0:
            self.evaluate_candidate(candidate, context)
            
        passed = ElectricalConstraintsEvaluator.evaluate_constraints(candidate, context)
        return passed

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Computes wire lengths, electrical drops, contact losses, and safety margins.
        """
        assert isinstance(candidate, ElectricalCandidate)
        assert isinstance(context, ElectricalContext)
        
        assembly = context.propulsion_assembly
        wheelbase = context.frame_spec.wheelbase_m
        arm_count = context.frame_spec.arm_count
        
        # 1. Wire lengths
        l_main = 0.15  # battery main lead length (m)
        l_esc = 0.20   # ESC power lead length (m)
        l_motor = 0.5 * wheelbase  # Motor phase wires length (m)
        
        # Currents
        i_total = assembly.hover_current_total_a
        i_esc = i_total / arm_count
        i_motor = i_esc  # phase current approximation
        
        # 2. Voltage drops
        candidate.main_voltage_drop_v = WiringOptimizer.calculate_voltage_drop(i_total, candidate.main_wire.resistance_ohms_per_m, l_main)
        candidate.esc_voltage_drop_v = WiringOptimizer.calculate_voltage_drop(i_esc, candidate.esc_wire.resistance_ohms_per_m, l_esc)
        candidate.motor_voltage_drop_v = WiringOptimizer.calculate_voltage_drop(i_motor, candidate.motor_wire.resistance_ohms_per_m, l_motor)

        # 3. Wiring power losses: P = I^2 * R * L * 2
        p_loss_main = (i_total ** 2) * candidate.main_wire.resistance_ohms_per_m * l_main * 2.0
        p_loss_esc = ((i_esc ** 2) * candidate.esc_wire.resistance_ohms_per_m * l_esc * 2.0) * arm_count
        p_loss_motor = ((i_motor ** 2) * candidate.motor_wire.resistance_ohms_per_m * l_motor * 2.0) * arm_count
        candidate.wiring_power_loss_w = p_loss_main + p_loss_esc + p_loss_motor

        # 4. Connector contact resistance losses (contact resistance R ~ 0.5 milliohms)
        r_contact_batt = 0.0003
        r_contact_motor = 0.0005
        p_loss_conn_batt = (i_total ** 2) * r_contact_batt
        p_loss_conn_motor = ((i_motor ** 2) * r_contact_motor * 3) * arm_count
        candidate.connector_power_loss_w = p_loss_conn_batt + p_loss_conn_motor

        # 5. Regulator / BEC efficiency losses (~12% loss on BEC bus)
        candidate.regulator_power_loss_w = candidate.power_budget.total_auxiliary_power_w * 0.12

        # 6. Electrical efficiency
        p_total_hover = assembly.hover_power_total_w
        p_losses = candidate.wiring_power_loss_w + candidate.connector_power_loss_w + candidate.regulator_power_loss_w
        candidate.electrical_efficiency = max(0.01, (p_total_hover - p_losses) / max(1.0, p_total_hover))

        # 7. Sized overall Safety margin
        candidate.safety_margin_pct = max(0.0, ((candidate.main_wire.max_continuous_current_a - i_total) / candidate.main_wire.max_continuous_current_a) * 100.0)
        
        # Save derived variables in dictionary for logger compatibility
        candidate.derived_variables = {
            "main_voltage_drop_v": candidate.main_voltage_drop_v,
            "wiring_power_loss_w": candidate.wiring_power_loss_w,
            "connector_power_loss_w": candidate.connector_power_loss_w,
            "electrical_efficiency": candidate.electrical_efficiency
        }

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Calculates optimization score using mission priorities.
        """
        assert isinstance(candidate, ElectricalCandidate)
        assert isinstance(context, ElectricalContext)
        
        weights = context.strategy_spec.priority_weights
        
        # Calculate combined wiring mass
        wheelbase = context.frame_spec.wheelbase_m
        arm_count = context.frame_spec.arm_count
        main_mass = 0.15 * candidate.main_wire.weight_kg_per_m
        esc_mass = 0.20 * candidate.esc_wire.weight_kg_per_m * arm_count
        motor_mass = (0.5 * wheelbase) * candidate.motor_wire.weight_kg_per_m * arm_count * 3.0  # 3 phase wires
        total_mass = main_mass + esc_mass + motor_mass
        
        # 1. Low Weight score (normalize by max wiring weight 1.5kg)
        weight_score = max(0.0, 1.0 - (total_mass / 1.5))
        
        # 2. Efficiency score
        eff_score = candidate.electrical_efficiency
        
        # 3. Voltage drop safety (limits drop relative to 3% budget)
        v_batt = context.propulsion_assembly.battery.voltage
        v_limit = 0.03 * v_batt
        total_drop = candidate.main_voltage_drop_v + candidate.esc_voltage_drop_v
        safety_score = max(0.0, 1.0 - (total_drop / v_limit))
        
        weighted_sum = (
            weights.efficiency * eff_score +
            weights.endurance * weight_score +
            weights.safety * safety_score
        )
        
        weights_total = (
            weights.efficiency +
            weights.endurance +
            weights.safety
        )
        
        score = weighted_sum / max(0.01, weights_total)
        candidate.overall_score = score
        candidate.objective_scores = {
            "electrical_efficiency": eff_score,
            "weight_score": weight_score,
            "voltage_safety": safety_score
        }
        return score

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """
        Converts optimized candidate to ElectricalSpecification.
        """
        assert isinstance(candidate, ElectricalCandidate)
        assert isinstance(context, ElectricalContext)
        
        assembly = context.propulsion_assembly
        budget = candidate.power_budget
        
        wire_summary = {
            "Main Battery Wire": f"AWG {candidate.main_wire.awg}",
            "ESC Power Lead Wire": f"AWG {candidate.esc_wire.awg}",
            "Motor Phase Wire": f"AWG {candidate.motor_wire.awg}"
        }
        
        connector_summary = {
            "Battery Connector": candidate.battery_connector.name,
            "Motor Connector": candidate.motor_connector.name,
            "Avionics Connector": "Servo Connector"
        }
        
        power_budget_dict = {
            "Avionics Bus Power (W)": budget.avionics_power_w,
            "Payload Power (W)": budget.payload_power_w,
            "Total Auxiliary Power (W)": budget.total_auxiliary_power_w,
            "Propulsion Power Hover (W)": assembly.hover_power_total_w,
            "Propulsion Power Peak (W)": assembly.peak_power_total_w
        }
        
        voltage_budget_dict = {
            "Battery Nominal Voltage (V)": assembly.battery.voltage,
            "Avionics BEC Voltage (V)": 5.0,
            "Payload Regulated Voltage (V)": 12.0 if budget.bec_capacity_12v_a > 0 else 0.0,
            "Main Wire Drop (V)": candidate.main_voltage_drop_v,
            "ESC Wire Drop (V)": candidate.esc_voltage_drop_v,
            "Motor Wire Drop (V)": candidate.motor_voltage_drop_v
        }
        
        current_budget_dict = {
            "Total Propulsion Hover Current (A)": assembly.hover_current_total_a,
            "Total Propulsion Peak Current (A)": assembly.peak_current_total_a,
            "Avionics BEC 5V Load (A)": budget.bec_capacity_5v_a - (budget.bec_capacity_5v_a * budget.bec_margin_5v_pct / 100.0),
            "Payload BEC 12V Load (A)": budget.bec_capacity_12v_a - (budget.bec_capacity_12v_a * budget.bec_margin_12v_pct / 100.0) if budget.bec_capacity_12v_a > 0 else 0.0
        }
        
        loss_summary_dict = {
            "Conductor Wire Losses (W)": candidate.wiring_power_loss_w,
            "Connector Contact Losses (W)": candidate.connector_power_loss_w,
            "Regulator/BEC Losses (W)": candidate.regulator_power_loss_w,
            "Total Heat Loss (W)": candidate.wiring_power_loss_w + candidate.connector_power_loss_w + candidate.regulator_power_loss_w
        }
        
        safety_margins_dict = {
            "BEC 5V Current Margin (%)": budget.bec_margin_5v_pct,
            "BEC 12V Current Margin (%)": budget.bec_margin_12v_pct,
            "Main Wire Current Margin (%)": candidate.safety_margin_pct,
            "Main Voltage Drop Percentage (%)": (candidate.main_voltage_drop_v / assembly.battery.voltage) * 100.0
        }
        
        reasoning = (
            f"Sized main battery wire to AWG {candidate.main_wire.awg} and ESC branch leads to AWG {candidate.esc_wire.awg} "
            f"to support continuous currents up to {assembly.hover_current_total_a:.1f}A with an overall voltage drop of "
            f"{candidate.main_voltage_drop_v + candidate.esc_voltage_drop_v:.3f}V. Power distribution handled by "
            f"{budget.pdb_type} with dual BEC (5V {budget.bec_capacity_5v_a:.0f}A, 12V {budget.bec_capacity_12v_a:.0f}A)."
        )
        
        spec = ElectricalSpecification(
            power_distribution=budget.pdb_type,
            wire_gauge_summary=wire_summary,
            connector_summary=connector_summary,
            power_budget=power_budget_dict,
            voltage_budget=voltage_budget_dict,
            current_budget=current_budget_dict,
            loss_summary=loss_summary_dict,
            electrical_efficiency_pct=candidate.electrical_efficiency * 100.0,
            safety_margins=safety_margins_dict,
            optimization_score=candidate.overall_score,
            engineering_reasoning=reasoning
        )
        
        # Validate spec
        self._validator.validate_electrical(spec)
        return spec
