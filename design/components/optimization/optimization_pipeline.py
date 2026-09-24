"""
OptimizationPipeline Subsystem

Purpose:
    Defines the `OptimizationPipeline` class responsible for executing iterative engineering optimization loops.

Role in Architecture:
    `OptimizationPipeline` coordinates candidate modification generation via `OptimizationStrategy`, passes variants through
    `CompatibilityEngine`, `ConstraintEngine`, and `ScoringEngine`, checks `OptimizationStopCondition`, tracks step records,
    and constructs an `OptimizationResult`.
"""

import time
from typing import Any
from backend.design.components.compatibility import CompatibilityEngine, CompatibilityStatus
from backend.design.components.constraints import ConstraintEngine, ConstraintStatus
from backend.design.components.scoring import ScoringEngine, EngineeringScore
from backend.design.components.optimization.optimization_candidate import OptimizationCandidate
from backend.design.components.optimization.optimization_iteration import OptimizationIteration
from backend.design.components.optimization.optimization_result import OptimizationResult
from backend.design.components.optimization.optimization_stop_condition import OptimizationStopCondition
from backend.design.components.optimization.optimization_strategy import OptimizationStrategy, GreedyOptimizationStrategy


def _extract_score(candidate: OptimizationCandidate) -> float:
    """Helper extracting numeric overall score from candidate."""
    if isinstance(candidate.engineering_score, EngineeringScore):
        return float(candidate.engineering_score.overall_score)
    elif isinstance(candidate.engineering_score, (int, float)):
        return float(candidate.engineering_score)
    return 0.0


class OptimizationPipeline:
    """
    Pipeline for executing iterative aircraft engineering optimization workflows.

    Design Principles:
        - Pipeline Pattern: Iterative generation, multi-stage evaluation, and history tracking.
        - Strict Evaluation: Every variant MUST pass Compatibility, Constraint, and Scoring evaluation.
    """

    def __init__(
        self,
        strategy: OptimizationStrategy | None = None,
        stop_condition: OptimizationStopCondition | None = None,
        compatibility_engine: CompatibilityEngine | None = None,
        constraint_engine: ConstraintEngine | None = None,
        scoring_engine: ScoringEngine | None = None
    ) -> None:
        """
        Initializes the OptimizationPipeline.

        Args:
            strategy (OptimizationStrategy | None): Injected optimization strategy. Defaults to GreedyOptimizationStrategy.
            stop_condition (OptimizationStopCondition | None): Injected termination condition evaluator.
            compatibility_engine (CompatibilityEngine | None): Injected compatibility checker.
            constraint_engine (ConstraintEngine | None): Injected constraint evaluator.
            scoring_engine (ScoringEngine | None): Injected engineering scorer.
        """
        self._strategy: OptimizationStrategy = strategy if strategy else GreedyOptimizationStrategy()
        self._stop_condition: OptimizationStopCondition = (
            stop_condition if stop_condition else OptimizationStopCondition()
        )
        self._compatibility_engine: CompatibilityEngine = (
            compatibility_engine if compatibility_engine else CompatibilityEngine()
        )
        self._constraint_engine: ConstraintEngine = (
            constraint_engine if constraint_engine else ConstraintEngine()
        )
        self._scoring_engine: ScoringEngine = (
            scoring_engine if scoring_engine else ScoringEngine()
        )

    def execute(self, baseline_candidate: OptimizationCandidate) -> OptimizationResult:
        """
        Executes iterative optimization loop starting from baseline_candidate.

        Args:
            baseline_candidate (OptimizationCandidate): Initial feasible baseline design.

        Returns:
            OptimizationResult: Final optimization result containing best design and history.
        """
        # Initial scoring of baseline candidate if unassigned
        if baseline_candidate.engineering_score is None:
            baseline_candidate.engineering_score = self._scoring_engine.score_design(
                baseline_candidate.design_context
            )

        current_best = baseline_candidate
        current_best_score = _extract_score(current_best)

        history: list[OptimizationCandidate] = [baseline_candidate]
        iterations: list[OptimizationIteration] = []
        no_improvement_count = 0

        iteration_num = 0
        termination_reason = ""

        while True:
            iteration_num += 1
            t0 = time.time()

            # 1. Generate modified variants using strategy
            variants = self._strategy.generate_modifications(current_best, iteration_num)
            valid_variants: list[OptimizationCandidate] = []

            # 2. Evaluate variants through full evaluation pipeline
            for var in variants:
                # Compatibility check
                compat_res = self._compatibility_engine.check_compatibility(var.design_context.design_data)
                if compat_res.status == CompatibilityStatus.INCOMPATIBLE:
                    continue  # Reject physically incompatible variant

                # Constraint check
                const_res = self._constraint_engine.evaluate_constraints(var.design_context)
                if const_res.status == ConstraintStatus.VIOLATED:
                    continue  # Reject constraint-violating variant

                # Engineering scoring
                var.engineering_score = self._scoring_engine.score_design(var.design_context)
                valid_variants.append(var)
                history.append(var)

            t1 = time.time()

            # 3. Check for improvement
            best_variant_in_step = None
            step_best_score = current_best_score

            if valid_variants:
                valid_variants.sort(key=lambda c: _extract_score(c), reverse=True)
                top_step = valid_variants[0]
                step_best_score = _extract_score(top_step)

                if step_best_score > current_best_score:
                    best_variant_in_step = top_step

            improvement_delta = max(0.0, step_best_score - current_best_score)

            if best_variant_in_step and improvement_delta >= self._stop_condition.min_improvement:
                current_best = best_variant_in_step
                current_best_score = step_best_score
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            # Record iteration history step
            iter_record = OptimizationIteration(
                iteration_number=iteration_num,
                candidate_count=len(valid_variants),
                best_score=round(current_best_score, 3),
                improvement=round(improvement_delta, 4),
                duration=round(t1 - t0, 4)
            )
            iterations.append(iter_record)

            # 4. Check stop conditions
            should_stop, reason = self._stop_condition.should_stop(
                current_iteration=iteration_num,
                improvement_delta=improvement_delta,
                current_best_score=current_best_score,
                no_improvement_count=no_improvement_count
            )

            if should_stop:
                termination_reason = reason
                break

        baseline_score = _extract_score(baseline_candidate)
        total_improvement = current_best_score - baseline_score
        summary = (
            f"Optimization complete ({termination_reason}). "
            f"Baseline score: {baseline_score:.3f} -> Optimized score: {current_best_score:.3f} "
            f"(Total improvement: +{total_improvement:.3f} across {iteration_num} iterations)."
        )

        return OptimizationResult(
            best_design=current_best,
            optimization_history=history,
            iterations=iterations,
            improvement_summary=summary,
            termination_reason=termination_reason,
            metadata={"strategy": self._strategy.strategy_name}
        )
