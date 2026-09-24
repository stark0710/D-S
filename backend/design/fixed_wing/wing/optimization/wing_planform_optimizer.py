"""
Fixed-Wing Wing Planform Sizing Optimizer

Subclasses OptimizerBase to orchestrate sweeps and compile WingPlanformSpecification.
"""

from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.wing.wing_engine import WingEngine
from backend.design.fixed_wing.wing.optimization.models import WingPlanformSpecification
from backend.design.fixed_wing.wing.optimization.result import WingOptimizationResult
from backend.design.fixed_wing.wing.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.wing.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.wing.optimization.constraints import build_wing_constraints
from backend.design.fixed_wing.wing.optimization.objective_function import WingObjectiveFunction

class WingPlanformOptimizer(OptimizerBase):
    """
    Subsystem optimizer resolving optimal primary lifting geometries.
    """
    def __init__(self, engine: WingEngine | None = None) -> None:
        super().__init__("WingPlanformOptimizer")
        self._engine = engine if engine else WingEngine()
        self._evaluator = CandidateEvaluator(self._engine)
        self.constraints = build_wing_constraints()
        self.objective = WingObjectiveFunction()

    def initialize(self, context: OptimizationContext) -> None:
        priority = getattr(context, "optimization_priority", None)
        if priority is not None:
            from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
            weights = OptimizationPriorityPolicy.get_wing_weights(priority)
            for term in self.objective._terms:
                if term.name in weights:
                    term.weight = weights[term.name]

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        generator = GridSearchCandidateGenerator()
        return generator.generate_candidates(context)

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        self._evaluator.evaluate(candidate, context)

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> WingPlanformSpecification:
        vars_ = candidate.design_variables
        derived = candidate.derived_variables
        
        # Compile reasoning notes
        reasoning = (
            f"Sized optimal wing planform using deterministic grid search. "
            f"Selected Aspect Ratio: {vars_['aspect_ratio']:.1f}, "
            f"Taper Ratio: {vars_['taper_ratio']:.2f}, "
            f"Sweep: {vars_['sweep_angle_deg']:.1f} deg, "
            f"Dihedral: {vars_['dihedral_angle_deg']:.1f} deg. "
            f"Resulting Span: {derived['wing_span']:.3f} m, Area: {derived['wing_area']:.4f} m2. "
            f"Candidate overall cost: {candidate.overall_score:.4f}."
        )

        return WingPlanformSpecification(
            wing_area=derived["wing_area"],
            aspect_ratio=vars_["aspect_ratio"],
            wing_span=derived["wing_span"],
            root_chord=derived["root_chord"],
            tip_chord=derived["tip_chord"],
            mac=derived["mac"],
            taper_ratio=vars_["taper_ratio"],
            sweep=vars_["sweep_angle_deg"],
            dihedral=vars_["dihedral_angle_deg"],
            wing_loading=derived["wing_loading"],
            optimization_score=candidate.overall_score,
            reasoning=reasoning,
            estimated_mtow_kg=derived.get("estimated_mtow_kg"),
            estimated_wing_weight_kg=derived.get("estimated_wing_weight_kg"),
        )
