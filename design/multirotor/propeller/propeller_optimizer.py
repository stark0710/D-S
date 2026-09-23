from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.multirotor.propeller.propeller_models import PropellerContext, PropellerCandidate
from backend.design.multirotor.propeller.propeller_selector import PropellerSelector, CatalogPropellerRecord
from backend.design.multirotor.propeller.propeller_performance import PropellerPerformance
from backend.design.multirotor.propeller.propeller_constraints import PropellerConstraintsEvaluator
from backend.design.multirotor.propeller.propeller_validator import PropellerValidator
from backend.design.multirotor.propeller.propeller_result import PropellerSpecification

class PropellerOptimizer(OptimizerBase):
    """
    Multidisciplinary Aerodynamic Propeller Sizer and Optimizer Subsystem.
    Adapts the shared OptimizerBase template method lifecycle.
    """
    def __init__(self, name: str = "PropellerOptimizer") -> None:
        super().__init__(name)
        self._selector = PropellerSelector()
        self._validator = PropellerValidator()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Pulls all catalog propeller records to match and evaluate compatibility.
        """
        assert isinstance(context, PropellerContext)
        
        candidates: List[OptimizationCandidate] = []
        matching_props = self._selector.get_all_propellers()
        for record in matching_props:
            d_vars = {
                "manufacturer": record.manufacturer,
                "model": record.model,
                "diameter_m": record.diameter_m,
                "pitch_m": record.pitch_m,
                "blade_count": record.blade_count,
            }
            cand = PropellerCandidate(design_variables=d_vars)
            cand.propeller_record = record
            candidates.append(cand)
            
        return candidates

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Redirects to constraint evaluators.
        """
        assert isinstance(candidate, PropellerCandidate)
        assert isinstance(context, PropellerContext)
        
        # Ensure evaluation runs first to calculate RPMs and powers
        if candidate.hover_rpm == 0.0:
            self.evaluate_candidate(candidate, context)
            
        passed = PropellerConstraintsEvaluator.evaluate_constraints(candidate, context)
        return passed

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Computes thrust, RPM, tip speeds, and absorbed power values.
        """
        assert isinstance(candidate, PropellerCandidate)
        assert isinstance(context, PropellerContext)
        
        PropellerPerformance.calculate_performance(candidate, context)
        
        # Save derived variables in dictionary for logger compatibility
        candidate.derived_variables = {
            "hover_rpm": candidate.hover_rpm,
            "max_rpm": candidate.max_rpm,
            "tip_speed_m_s": candidate.tip_speed_m_s,
            "hover_efficiency_g_w": candidate.hover_efficiency_g_w
        }

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Calculates optimization score using mission priorities.
        """
        assert isinstance(candidate, PropellerCandidate)
        assert isinstance(context, PropellerContext)
        
        weights = context.strategy_spec.priority_weights
        prop = candidate.propeller_record
        
        # 1. Aerodynamic efficiency score (relative to high limit 18.0 g/W)
        eff_score = min(1.0, candidate.hover_efficiency_g_w / 18.0)
        
        # 2. Quietness score (favors lower tip speed, relative to limit 220m/s)
        noise_score = max(0.0, 1.0 - (candidate.tip_speed_m_s / 220.0))
        
        # 3. Propeller Weight score (normalize by max weight 0.1kg)
        weight_score = max(0.0, 1.0 - (prop.empty_mass_kg / 0.1))
        
        weighted_sum = (
            weights.endurance * eff_score +
            weights.efficiency * eff_score +
            weights.reliability * noise_score +
            weights.safety * weight_score
        )
        
        weights_total = (
            weights.endurance +
            weights.efficiency +
            weights.reliability +
            weights.safety
        )
        
        score = weighted_sum / max(0.01, weights_total)
        candidate.overall_score = score
        candidate.objective_scores = {
            "aerodynamic_efficiency": eff_score,
            "vibration_noise": noise_score,
            "weight_score": weight_score
        }
        return score

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """
        Converts optimized candidate to PropellerSpecification.
        """
        assert isinstance(candidate, PropellerCandidate)
        assert isinstance(context, PropellerContext)
        
        prop = candidate.propeller_record
        reasoning = (
            f"Selected {prop.manufacturer} {prop.model} ({prop.diameter_m * 39.37:.1f} inch diameter, "
            f"{prop.pitch_m * 39.37:.1f} inch pitch) achieving hover efficiency "
            f"of {candidate.hover_efficiency_g_w:.2f} g/W at {candidate.hover_rpm:.0f} RPM."
        )
        
        spec = PropellerSpecification(
            manufacturer=prop.manufacturer,
            model=prop.model,
            diameter_m=prop.diameter_m,
            pitch_m=prop.pitch_m,
            blade_count=prop.blade_count,
            material=prop.material,
            weight_kg=prop.empty_mass_kg,
            disc_area_m2=candidate.disc_area_m2,
            tip_speed_m_s=candidate.tip_speed_m_s,
            hover_efficiency_g_w=candidate.hover_efficiency_g_w,
            power_absorption_w=candidate.hover_power_absorbed_w,
            optimization_score=candidate.overall_score,
            engineering_reasoning=reasoning
        )
        
        # Validate spec
        self._validator.validate_propeller(spec)
        return spec
