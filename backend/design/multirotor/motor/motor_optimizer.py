from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.multirotor.motor.motor_models import MotorContext, MotorCandidate
from backend.design.multirotor.motor.motor_selector import MotorSelector, CatalogMotorRecord
from backend.design.multirotor.motor.motor_performance import MotorPerformance
from backend.design.multirotor.motor.motor_constraints import MotorConstraintsEvaluator
from backend.design.multirotor.motor.motor_validator import MotorValidator
from backend.design.multirotor.motor.motor_result import MotorSpecification

class MotorOptimizer(OptimizerBase):
    """
    Multidisciplinary Propulsion Motor Sizer and Optimizer Subsystem.
    Adapts the shared OptimizerBase template method lifecycle.
    """
    def __init__(self, name: str = "MotorOptimizer") -> None:
        super().__init__(name)
        self._selector = MotorSelector()
        self._validator = MotorValidator()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Queries catalog database for motor options.
        """
        assert isinstance(context, MotorContext)
        
        candidates: List[OptimizationCandidate] = []
        
        # Always generate all catalog motors to guarantee finding a physically feasible sizing candidate
        matching_motors = self._selector.get_all_motors()
        for record in matching_motors:
            d_vars = {
                "manufacturer": record.manufacturer,
                "model": record.model,
                "kv": record.kv_rating,
                "weight_kg": record.empty_mass_kg,
            }
            cand = MotorCandidate(design_variables=d_vars)
            cand.motor_record = record
            candidates.append(cand)
            
        return candidates

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Redirects to constraint evaluators.
        """
        assert isinstance(candidate, MotorCandidate)
        assert isinstance(context, MotorContext)
        
        # Ensure evaluation runs first to calculate currents and powers
        if candidate.hover_thrust_n == 0.0:
            self.evaluate_candidate(candidate, context)
            
        passed = MotorConstraintsEvaluator.evaluate_constraints(candidate, context)
        return passed

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Computes thrust, currents, and power consumption margins.
        """
        assert isinstance(candidate, MotorCandidate)
        assert isinstance(context, MotorContext)
        
        MotorPerformance.calculate_performance(candidate, context)
        
        # Save derived variables in dictionary for logger compatibility
        candidate.derived_variables = {
            "estimated_auw_kg": candidate.estimated_auw_kg,
            "hover_current_a": candidate.hover_current_a,
            "max_current_a": candidate.max_current_a,
            "throttle_hover_pct": candidate.throttle_hover_pct,
            "efficiency_pct": candidate.motor_efficiency * 100.0
        }

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Calculates optimization score using mission priorities.
        """
        assert isinstance(candidate, MotorCandidate)
        assert isinstance(context, MotorContext)
        
        weights = context.strategy_spec.priority_weights
        motor = candidate.motor_record
        
        # 1. Low Weight score (normalize by max weight 1.0kg)
        weight_score = max(0.0, 1.0 - (motor.empty_mass_kg / 1.0))
        
        # 2. Efficiency score
        eff_score = candidate.motor_efficiency
        
        # 3. Current safety margin score
        current_margin = max(0.0, 1.0 - (candidate.hover_current_a / motor.max_continuous_current_a))
        
        # 4. Thrust safety margin score
        thrust_ratio = candidate.max_thrust_n / max(0.01, motor.max_thrust_n)
        thrust_score = max(0.0, 1.0 - abs(thrust_ratio - 0.5))  # favors ~50% throttle at hover
        
        # 5. KV range alignment score
        kv_min, kv_max = context.strategy_spec.engineering_targets.preferred_motor_kv_range
        kv_score = 1.0 if kv_min <= motor.kv_rating <= kv_max else 0.4
        
        weighted_sum = (
            weights.endurance * weight_score +
            weights.efficiency * eff_score +
            weights.reliability * current_margin +
            weights.safety * thrust_score +
            0.5 * kv_score
        )
        
        weights_total = (
            weights.endurance +
            weights.efficiency +
            weights.reliability +
            weights.safety +
            0.5
        )
        
        score = weighted_sum / max(0.01, weights_total)
        candidate.overall_score = score
        candidate.objective_scores = {
            "weight_score": weight_score,
            "efficiency": eff_score,
            "current_margin": current_margin,
            "thrust_margin": thrust_score,
            "kv_alignment": kv_score
        }
        return score

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """
        Converts optimized candidate to MotorSpecification.
        """
        assert isinstance(candidate, MotorCandidate)
        assert isinstance(context, MotorContext)
        
        motor = candidate.motor_record
        
        # Calculate nominal power margin
        v_batt = 0.5 * (motor.min_voltage_v + motor.max_voltage_v)
        max_power = motor.max_continuous_current_a * v_batt
        hover_power = candidate.hover_current_a * v_batt
        power_margin = max_power - hover_power
        
        reasoning = (
            f"Selected {motor.manufacturer} {motor.model} ({motor.kv_rating:.0f} KV) "
            f"providing {motor.max_thrust_n:.1f}N max thrust at {candidate.throttle_hover_pct:.1f}% hover throttle "
            f"with estimated AUW of {candidate.estimated_auw_kg:.2f} kg."
        )
        
        spec = MotorSpecification(
            manufacturer=motor.manufacturer,
            model=motor.model,
            kv=motor.kv_rating,
            voltage_range_v=(motor.min_voltage_v, motor.max_voltage_v),
            max_thrust_n=motor.max_thrust_n,
            hover_thrust_n=candidate.hover_thrust_n,
            hover_current_a=candidate.hover_current_a,
            max_current_a=candidate.max_current_a,
            efficiency_pct=candidate.motor_efficiency * 100.0,
            weight_kg=motor.empty_mass_kg,
            power_margin_w=power_margin,
            throttle_hover_pct=candidate.throttle_hover_pct,
            mount_pattern_mm=motor.mount_pattern_mm,
            optimization_score=candidate.overall_score,
            engineering_reasoning=reasoning
        )
        
        # Validate spec
        self._validator.validate_motor(spec)
        return spec
