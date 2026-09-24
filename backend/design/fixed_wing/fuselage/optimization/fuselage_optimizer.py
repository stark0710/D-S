"""
Fixed-Wing Fuselage Sizing Optimizer

Subclasses OptimizerBase to orchestrate sweeps and compile FuselageSpecification.
"""

from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.fuselage.fuselage_engine import FuselageEngine
from backend.design.fixed_wing.fuselage.optimization.models import FuselageSpecification
from backend.design.fixed_wing.fuselage.optimization.result import FuselageOptimizationResult
from backend.design.fixed_wing.fuselage.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.fuselage.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.fuselage.optimization.constraints import build_fuselage_constraints
from backend.design.fixed_wing.fuselage.optimization.objective_function import FuselageObjectiveFunction

class FuselageOptimizer(OptimizerBase):
    """
    Subsystem optimizer resolving optimal fuselage and compartment layout sizing.
    """
    def __init__(self, engine: FuselageEngine | None = None) -> None:
        super().__init__("FuselageOptimizer")
        self._engine = engine if engine else FuselageEngine()
        self._evaluator = CandidateEvaluator(self._engine)
        self.constraints = build_fuselage_constraints()
        self.objective = FuselageObjectiveFunction()

    def initialize(self, context: OptimizationContext) -> None:
        priority = getattr(context, "optimization_priority", None)
        if priority is not None:
            from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
            weights = OptimizationPriorityPolicy.get_fuselage_weights(priority)
            for term in self.objective._terms:
                if term.name in weights:
                    term.weight = weights[term.name]

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        generator = GridSearchCandidateGenerator()
        return generator.generate_candidates(context)

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        self._evaluator.evaluate(candidate, context)

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> FuselageSpecification:
        vars_ = candidate.design_variables
        derived = candidate.derived_variables
        
        reasoning = (
            f"Sized optimal fuselage layout via grid search. "
            f"Length: {vars_['length']:.2f} m, Width: {vars_['width']:.2f} m, Height: {vars_['height']:.2f} m, "
            f"Nose Length: {vars_['nose_length']:.2f} m, Cabin Length: {vars_['cabin_length']:.2f} m, "
            f"Tail Cone Length: {vars_['tail_cone_length']:.2f} m. "
            f"Selected Shape: {vars_['cross_section']}, Fineness: {vars_['fineness_ratio']:.1f}. "
            f"Candidate overall cost: {candidate.overall_score:.4f}."
        )

        return FuselageSpecification(
            overall_length=vars_["length"],
            width=vars_["width"],
            height=vars_["height"],
            nose_length=vars_["nose_length"],
            cabin_length=vars_["cabin_length"],
            tail_cone_length=vars_["tail_cone_length"],
            cross_section=vars_["cross_section"],
            fineness_ratio=vars_["fineness_ratio"],
            wing_mount_position=vars_["length"] * 0.32,
            payload_bay=derived["payload_bay"],
            battery_bay=derived["battery_bay"],
            avionics_bay=derived["avionics_bay"],
            bulkhead_locations=vars_["bulkhead_locations"],
            optimization_score=candidate.overall_score,
            reasoning=reasoning
        )
