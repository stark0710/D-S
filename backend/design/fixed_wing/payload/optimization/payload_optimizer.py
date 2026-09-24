"""
Fixed-Wing Payload Packaging Sizing Optimizer

Subclasses OptimizerBase to orchestrate sweeps and compile PayloadPackagingSpecification.
"""

from typing import List
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.payload.optimization.models import PayloadPackagingSpecification
from backend.design.fixed_wing.payload.optimization.result import PayloadPackagingOptimizationResult
from backend.design.fixed_wing.payload.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.payload.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.payload.optimization.constraints import build_payload_constraints
from backend.design.fixed_wing.payload.optimization.objective_function import PayloadObjectiveFunction

class PayloadPackagingOptimizer(OptimizerBase):
    """
    Subsystem optimizer resolving optimal internal compartment layout and equipment packaging.
    """
    def __init__(self) -> None:
        super().__init__("PayloadPackagingOptimizer")
        self._evaluator = CandidateEvaluator()
        self.constraints = build_payload_constraints()
        self.objective = PayloadObjectiveFunction()

    def initialize(self, context: OptimizationContext) -> None:
        priority = getattr(context, "optimization_priority", None)
        if priority is not None:
            from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
            weights = OptimizationPriorityPolicy.get_payload_weights(priority)
            for term in self.objective._terms:
                if term.name in weights:
                    term.weight = weights[term.name]

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        generator = GridSearchCandidateGenerator()
        return generator.generate_candidates(context)

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        self._evaluator.evaluate(candidate, context)

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> PayloadPackagingSpecification:
        vars_ = candidate.design_variables
        derived = candidate.derived_variables
        
        reasoning = (
            f"Selected optimal internal layout: "
            f"Payload: {vars_['payload_position_mode']}, "
            f"Battery: {vars_['battery_position_mode']} ({vars_['battery_orientation']}), "
            f"Electronics: {vars_['electronics_layout_mode']}. "
            f"Candidate score: {candidate.overall_score:.4f}."
        )

        return PayloadPackagingSpecification(
            payload_position=derived["payload_position"],
            battery_position=derived["battery_position"],
            battery_orientation=vars_["battery_orientation"],
            avionics_layout={
                "position_x": derived["payload_position"] + 0.15,
                "layout_mode": vars_["electronics_layout_mode"]
            },
            electronics_layout={
                "layout_mode": vars_["electronics_layout_mode"]
            },
            gps_position=derived["gps_position"],
            receiver_position=derived["receiver_position"],
            telemetry_position=derived["telemetry_position"],
            power_distribution={
                "pmu_position_x": derived["battery_position"] + 0.05
            },
            access_panels=[
                {"location_x": derived["payload_position"], "type": "Payload Hatch"},
                {"location_x": derived["battery_position"], "type": "Battery Canopy"}
            ],
            reserved_expansion_space=0.08,
            packaging_efficiency_score=derived["packing_efficiency"],
            optimization_score=candidate.overall_score,
            reasoning=reasoning
        )
