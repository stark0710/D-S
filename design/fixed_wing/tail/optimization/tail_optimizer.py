"""
Fixed-Wing Tail Optimization Engine

Subclasses OptimizerBase to orchestrate tail geometry sweeps,
evaluate candidates via TailSizer + TailAnalysisService, and
compile the winning TailSpecification.
"""

from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.tail.optimization.models import TailSpecification
from backend.design.fixed_wing.tail.optimization.result import TailOptimizationResult
from backend.design.fixed_wing.tail.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.tail.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.tail.optimization.constraints import build_tail_constraints
from backend.design.fixed_wing.tail.optimization.objective_function import TailObjectiveFunction


class TailOptimizer(OptimizerBase):
    """
    Subsystem optimizer resolving the optimal empennage configuration,
    volume coefficients, and geometric sizing using a deterministic grid
    search evaluated against the existing TailEngine calculation backend.
    """

    def __init__(self) -> None:
        super().__init__("TailOptimizer")
        self._evaluator = CandidateEvaluator()
        self.constraints = build_tail_constraints()
        self.objective = TailObjectiveFunction()

    def initialize(self, context: OptimizationContext) -> None:
        priority = getattr(context, "optimization_priority", None)
        if priority is not None:
            from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
            weights = OptimizationPriorityPolicy.get_tail_weights(priority)
            for term in self.objective._terms:
                if term.name in weights:
                    term.weight = weights[term.name]
                elif term.name == "mission_suitability" and "mission" in weights:
                    term.weight = weights["mission"]

    # ------------------------------------------------------------------
    #  OptimizerBase lifecycle hooks
    # ------------------------------------------------------------------

    def generate_candidates(
        self, context: OptimizationContext
    ) -> List[OptimizationCandidate]:
        generator = GridSearchCandidateGenerator()
        return generator.generate_candidates(context)

    def evaluate_candidate(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> None:
        self._evaluator.evaluate(candidate, context)

    def build_specification(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> TailSpecification:
        dv = candidate.design_variables
        dd = candidate.derived_variables

        reasoning = (
            f"Selected optimal tail: {dv['tail_configuration']}, "
            f"V_h={dd.get('V_h_actual', dv['horizontal_V_h']):.3f}, "
            f"V_v={dd.get('V_v_actual', dv['vertical_V_v']):.3f}, "
            f"arm={dd.get('tail_arm_m', 0):.3f} m, "
            f"H-AR={dv['horiz_ar']}, V-AR={dv['vert_ar']}. "
            f"Score: {candidate.overall_score:.4f}."
        )

        return TailSpecification(
            tail_configuration=dv["tail_configuration"],
            horizontal_tail_area_m2=round(dd.get("h_area_m2", 0.0), 4),
            horizontal_tail_span_m=round(dd.get("h_span_m", 0.0), 3),
            horizontal_tail_root_chord_m=round(dd.get("h_root_chord_m", 0.0), 3),
            horizontal_tail_tip_chord_m=round(dd.get("h_tip_chord_m", 0.0), 3),
            vertical_tail_area_m2=round(dd.get("v_area_m2", 0.0), 4),
            vertical_tail_height_m=round(dd.get("v_height_m", 0.0), 3),
            vertical_tail_root_chord_m=round(dd.get("v_root_chord_m", 0.0), 3),
            vertical_tail_tip_chord_m=round(dd.get("v_tip_chord_m", 0.0), 3),
            horizontal_volume_coefficient=round(dd.get("V_h_actual", dv["horizontal_V_h"]), 3),
            vertical_volume_coefficient=round(dd.get("V_v_actual", dv["vertical_V_v"]), 3),
            tail_arm_m=round(dd.get("tail_arm_m", 0.0), 3),
            horizontal_aspect_ratio=dv["horiz_ar"],
            vertical_aspect_ratio=dv["vert_ar"],
            horizontal_taper_ratio=dv["horiz_taper"],
            vertical_taper_ratio=dv["vert_taper"],
            horizontal_sweep_deg=dv["horiz_sweep"],
            vertical_sweep_deg=dv["vert_sweep"],
            tail_dihedral_deg=dv.get("tail_dihedral_deg", 0.0),
            optimization_score=round(candidate.overall_score, 4),
            reasoning=reasoning,
        )
