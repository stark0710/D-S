from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.multirotor.battery.battery_models import BatteryContext, BatteryCandidate
from backend.design.multirotor.battery.battery_selector import BatterySelector, CatalogBatteryRecord
from backend.design.multirotor.battery.battery_performance import BatteryPerformance
from backend.design.multirotor.battery.battery_constraints import BatteryConstraintsEvaluator
from backend.design.multirotor.battery.battery_validator import BatteryValidator
from backend.design.multirotor.battery.battery_result import BatterySpecification, PropulsionAssembly

class BatteryOptimizer(OptimizerBase):
    """
    Multidisciplinary Battery Sizer, Optimizer, and Propulsion System Compiler Subsystem.
    Adapts the shared OptimizerBase template method lifecycle.
    """
    def __init__(self, name: str = "BatteryOptimizer") -> None:
        super().__init__(name)
        self._selector = BatterySelector()
        self._validator = BatteryValidator()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Pulls all catalog battery records to match and evaluate compatibility.
        """
        assert isinstance(context, BatteryContext)
        
        candidates: List[OptimizationCandidate] = []
        matching_batts = self._selector.get_all_batteries()
        for record in matching_batts:
            d_vars = {
                "manufacturer": record.manufacturer,
                "model": record.model,
                "chemistry": record.chemistry,
                "capacity_mah": record.capacity_mah,
                "cell_count": record.cell_count,
            }
            cand = BatteryCandidate(design_variables=d_vars)
            cand.battery_record = record
            candidates.append(cand)
            
        return candidates

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Redirects to constraint checkers.
        """
        assert isinstance(candidate, BatteryCandidate)
        assert isinstance(context, BatteryContext)
        
        # Ensure evaluation runs first to calculate margins
        if candidate.hover_current_draw_a == 0.0:
            self.evaluate_candidate(candidate, context)
            
        passed = BatteryConstraintsEvaluator.evaluate_constraints(candidate, context)
        return passed

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Computes AUW, actual currents, limits, and flight endurances.
        """
        assert isinstance(candidate, BatteryCandidate)
        assert isinstance(context, BatteryContext)
        
        BatteryPerformance.calculate_performance(candidate, context)
        
        # Save derived variables in dictionary for logger compatibility
        candidate.derived_variables = {
            "estimated_auw_kg": candidate.estimated_auw_kg,
            "estimated_flight_time_min": candidate.estimated_flight_time_min,
            "max_current_draw_a": candidate.max_current_draw_a,
            "energy_wh": candidate.battery_energy_wh
        }

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Calculates optimization score using mission priorities.
        """
        assert isinstance(candidate, BatteryCandidate)
        assert isinstance(context, BatteryContext)
        
        weights = context.strategy_spec.priority_weights
        batt = candidate.battery_record
        
        # 1. Specific energy density (normalize relative to high Li-Ion density 260 Wh/kg)
        density = candidate.battery_energy_wh / max(0.01, batt.empty_mass_kg)
        density_score = min(1.0, density / 260.0)
        
        # 2. Sized Flight endurance score (normalize relative to target 45 mins)
        endurance_score = min(1.0, candidate.estimated_flight_time_min / 45.0)
        
        # 3. Safe Discharge headroom (C-Rating margin relative to continuous capacity)
        discharge_margin = candidate.continuous_discharge_limit_a - candidate.hover_current_draw_a
        discharge_score = min(1.0, max(0.0, discharge_margin / 100.0))
        
        # 4. Mass penalty (favors lighter batteries, relative to 5kg maximum limit)
        weight_score = max(0.0, 1.0 - (batt.empty_mass_kg / 5.0))
        
        weighted_sum = (
            weights.endurance * endurance_score +
            weights.efficiency * density_score +
            weights.safety * discharge_score +
            weights.reliability * weight_score
        )
        
        weights_total = (
            weights.endurance +
            weights.efficiency +
            weights.safety +
            weights.reliability
        )
        
        score = weighted_sum / max(0.01, weights_total)
        candidate.overall_score = score
        candidate.objective_scores = {
            "flight_endurance": endurance_score,
            "specific_energy": density_score,
            "discharge_safety": discharge_score,
            "weight_penalty": weight_score
        }
        return score

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """
        Converts optimized candidate to BatterySpecification.
        """
        assert isinstance(candidate, BatteryCandidate)
        assert isinstance(context, BatteryContext)
        
        batt = candidate.battery_record
        
        reasoning = (
            f"Selected {batt.manufacturer} {batt.model} ({batt.chemistry} chemistry, "
            f"{batt.cell_count}S) providing {batt.capacity_mah:.0f} mAh capacity. "
            f"Achieves sized flight endurance of {candidate.estimated_flight_time_min:.1f} minutes "
            f"under {candidate.estimated_auw_kg:.2f} kg takeoff weight."
        )
        
        spec = BatterySpecification(
            manufacturer=batt.manufacturer,
            model=batt.model,
            chemistry=batt.chemistry,
            voltage=batt.nominal_voltage_v,
            cell_count=batt.cell_count,
            capacity_mah=batt.capacity_mah,
            weight_kg=batt.empty_mass_kg,
            energy_wh=candidate.battery_energy_wh,
            continuous_current_a=candidate.continuous_discharge_limit_a,
            burst_current_a=candidate.burst_discharge_limit_a,
            estimated_hover_time_min=candidate.estimated_hover_time_min,
            estimated_flight_time_min=candidate.estimated_flight_time_min,
            remaining_energy_margin_pct=candidate.remaining_energy_margin_pct,
            optimization_score=candidate.overall_score,
            engineering_reasoning=reasoning
        )
        
        # Validate spec
        self._validator.validate_battery(spec)
        return spec

    def build_propulsion_assembly(self, battery_spec: BatterySpecification, context: BatteryContext) -> PropulsionAssembly:
        """
        Packs and compiles the complete PropulsionAssembly.
        """
        motor = context.motor_spec
        prop = context.propeller_spec
        esc = context.esc_spec
        frame = context.frame_spec
        
        # Compile sizing totals
        motor_count = frame.arm_count
        propulsion_mass = motor_count * (motor.weight_kg + esc.weight_kg + prop.weight_kg)
        estimated_auw = context.requirements.payload_weight_kg + frame.frame_mass_kg + propulsion_mass + battery_spec.weight_kg
        
        total_hover_thrust = estimated_auw * 9.80665
        max_thrust_capability = motor.max_thrust_n * motor_count
        hover_throttle = (total_hover_thrust / max_thrust_capability) * 100.0 if max_thrust_capability > 0 else 0.0
        
        # Sized electrical totals
        # Read candidate actual weight scaled currents
        i_actual_hover_per_motor = motor.hover_current_a * ((estimated_auw / (motor.hover_thrust_n * motor_count / 9.80665)) ** 1.3)
        i_actual_max_per_motor = motor.max_current_a * ((estimated_auw / (motor.hover_thrust_n * motor_count / 9.80665)) ** 1.3)
        
        hover_current_total = (i_actual_hover_per_motor * motor_count) + 0.5
        peak_current_total = (i_actual_max_per_motor * motor_count) + 1.0
        
        hover_power_total = hover_current_total * battery_spec.voltage
        peak_power_total = peak_current_total * battery_spec.voltage
        
        safety_margins = {
            "current_margin_a": battery_spec.continuous_current_a - hover_current_total,
            "flight_time_margin_min": battery_spec.estimated_flight_time_min - context.requirements.target_flight_time_min
        }
        
        compatibility_matrix = {
            "voltage_compatible": motor.voltage_range_v[0] <= battery_spec.voltage <= motor.voltage_range_v[1],
            "current_discharge_compatible": peak_current_total <= battery_spec.burst_current_a
        }
        
        assembly = PropulsionAssembly(
            motor=motor,
            propeller=prop,
            esc=esc,
            battery=battery_spec,
            estimated_auw_kg=estimated_auw,
            total_hover_thrust_n=total_hover_thrust,
            max_thrust_capability_n=max_thrust_capability,
            hover_throttle_pct=hover_throttle,
            hover_current_total_a=hover_current_total,
            hover_power_total_w=hover_power_total,
            peak_current_total_a=peak_current_total,
            peak_power_total_w=peak_power_total,
            safety_margins=safety_margins,
            compatibility_matrix=compatibility_matrix
        )
        
        self._validator.validate_assembly(assembly)
        return assembly
