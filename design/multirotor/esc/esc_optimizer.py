from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.multirotor.esc.esc_models import EscContext, EscCandidate
from backend.design.multirotor.esc.esc_selector import EscSelector, CatalogEscRecord
from backend.design.multirotor.esc.esc_performance import EscPerformance
from backend.design.multirotor.esc.esc_constraints import EscConstraintsEvaluator
from backend.design.multirotor.esc.esc_validator import EscValidator
from backend.design.multirotor.esc.esc_result import ESCSpecification

class EscOptimizer(OptimizerBase):
    """
    Multidisciplinary Electronic Speed Controller (ESC) Sizer and Optimizer Subsystem.
    Adapts the shared OptimizerBase template method lifecycle.
    """
    def __init__(self, name: str = "EscOptimizer") -> None:
        super().__init__(name)
        self._selector = EscSelector()
        self._validator = EscValidator()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Pulls all catalog ESC records to match and evaluate compatibility.
        """
        assert isinstance(context, EscContext)
        
        candidates: List[OptimizationCandidate] = []
        matching_escs = self._selector.get_all_escs()
        for record in matching_escs:
            d_vars = {
                "manufacturer": record.manufacturer,
                "model": record.model,
                "continuous_current_a": record.continuous_current_a,
                "burst_current_a": record.burst_current_a,
            }
            cand = EscCandidate(design_variables=d_vars)
            cand.esc_record = record
            candidates.append(cand)
            
        return candidates

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Redirects to constraint checkers.
        """
        assert isinstance(candidate, EscCandidate)
        assert isinstance(context, EscContext)
        
        # Ensure evaluation runs first to calculate margins
        if candidate.hover_current_a == 0.0:
            self.evaluate_candidate(candidate, context)
            
        passed = EscConstraintsEvaluator.evaluate_constraints(candidate, context)
        return passed

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Computes current loads, margins, power losses, and efficiencies.
        """
        assert isinstance(candidate, EscCandidate)
        assert isinstance(context, EscContext)
        
        EscPerformance.calculate_performance(candidate, context)
        
        # Save derived variables in dictionary for logger compatibility
        candidate.derived_variables = {
            "hover_current_a": candidate.hover_current_a,
            "max_current_a": candidate.max_current_a,
            "thermal_margin_pct": candidate.thermal_margin_pct,
            "esc_efficiency": candidate.esc_efficiency
        }

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Calculates optimization score using mission priorities.
        """
        assert isinstance(candidate, EscCandidate)
        assert isinstance(context, EscContext)
        
        weights = context.strategy_spec.priority_weights
        esc = candidate.esc_record
        
        # 1. Safety current margin score (favor large headroom relative to 100A max current)
        margin_score = min(1.0, candidate.current_margin_a / 100.0)
        
        # 2. Low weight score (normalize by max ESC weight 0.35kg)
        weight_score = max(0.0, 1.0 - (esc.empty_mass_kg / 0.35))
        
        # 3. Efficiency score
        eff_score = candidate.esc_efficiency
        
        # 4. Thermal margin
        thermal_score = candidate.thermal_margin_pct / 100.0
        
        weighted_sum = (
            weights.safety * margin_score +
            weights.endurance * weight_score +
            weights.efficiency * eff_score +
            weights.reliability * thermal_score
        )
        
        weights_total = (
            weights.safety +
            weights.endurance +
            weights.efficiency +
            weights.reliability
        )
        
        score = weighted_sum / max(0.01, weights_total)
        candidate.overall_score = score
        candidate.objective_scores = {
            "current_margin": margin_score,
            "weight_score": weight_score,
            "efficiency": eff_score,
            "thermal_margin": thermal_score
        }
        return score

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """
        Converts optimized candidate to ESCSpecification.
        """
        assert isinstance(candidate, EscCandidate)
        assert isinstance(context, EscContext)
        
        esc = candidate.esc_record
        
        # Resolve protocol
        pref_protocol = context.requirements.metadata.get("signaling_protocol", "DShot600")
        is_heavy_lift = context.motor_spec.kv < 300.0
        
        if pref_protocol in esc.supported_protocols:
            protocol = pref_protocol
        elif is_heavy_lift and "PWM" in esc.supported_protocols:
            protocol = "PWM"
        else:
            protocol = esc.supported_protocols[0]
            
        bec_desc = f"{esc.bec_voltage_v}V/{esc.bec_current_a}A" if esc.has_bec else "None"
        
        reasoning = (
            f"Selected {esc.manufacturer} {esc.model} ({esc.continuous_current_a:.0f}A continuous, "
            f"{esc.burst_current_a:.0f}A burst) supporting {protocol} signaling. Sized continuous "
            f"headroom margin is {candidate.current_margin_a:.1f}A with thermal safety {candidate.thermal_margin_pct:.1f}%."
        )
        
        spec = ESCSpecification(
            manufacturer=esc.manufacturer,
            model=esc.model,
            continuous_current_a=esc.continuous_current_a,
            burst_current_a=esc.burst_current_a,
            voltage_range_v=(esc.min_voltage_v, esc.max_voltage_v),
            bec=bec_desc,
            protocol=protocol,
            weight_kg=esc.empty_mass_kg,
            current_margin_a=candidate.current_margin_a,
            thermal_margin_pct=candidate.thermal_margin_pct,
            efficiency_pct=candidate.esc_efficiency * 100.0,
            optimization_score=candidate.overall_score,
            engineering_reasoning=reasoning
        )
        
        # Validate spec
        self._validator.validate_esc(spec)
        return spec
