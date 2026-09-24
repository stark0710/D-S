"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Framework Base

Defines the core template methods and standard lifecycle for design optimization.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_result import OptimizationResult
from backend.design.common.optimization.constraint_manager import ConstraintManager
from backend.design.common.optimization.objective_function import ObjectiveFunction
from backend.design.common.optimization.optimization_logger import OptimizationLogger
from backend.design.common.optimization.optimization_utils import TimingHelper

class OptimizerBase(ABC):
    """
    Standardized base interface orchestrating parameter searches for subsystems.
    """
    def __init__(self, name: str = "Optimizer") -> None:
        self.name = name
        self.constraints = ConstraintManager()
        self.objective = ObjectiveFunction()
        self.logger = OptimizationLogger(name)

    def optimize(self, context: OptimizationContext) -> OptimizationResult:
        """
        Executes the uniform optimization search lifecycle.
        """
        with TimingHelper() as timer:
            self.logger.info(f"Starting {self.name} process...")
            
            # 1. Initialize
            self.initialize(context)
            
            # 2. Generate Candidates
            candidates = self.generate_candidates(context)
            self.logger.info(f"Generated {len(candidates)} candidates.")
            
            feasible_candidates = []
            history = []
            
            for candidate in candidates:
                context.iteration_count += 1
                
                # 3. Apply Constraints
                passed = self.apply_constraints(candidate, context)
                
                if passed:
                    # 4. Evaluate Candidate
                    try:
                        self.evaluate_candidate(candidate, context)
                        candidate.status = "FEASIBLE"
                        feasible_candidates.append(candidate)
                    except Exception as e:
                        candidate.status = "ERROR"
                        candidate.diagnostics["error"] = f"EvaluationException: {type(e).__name__}: {e}"
                        self.logger.error(f"Error evaluating candidate: {e}")
                else:
                    candidate.status = "INFEASIBLE"
                
                history.append(candidate)
                self.logger.log_candidate(candidate)

            self.logger.info(f"Feasible candidates count: {len(feasible_candidates)}/{len(candidates)}")

            # 5. Score Candidates
            for candidate in feasible_candidates:
                self.score_candidate(candidate, context)
                
            # 6. Select Best Candidate
            best_candidate = self.select_best_candidate(feasible_candidates, context)
            
            # 7. Build Specification
            spec = None
            if best_candidate:
                spec = self.build_specification(best_candidate, context)
                success = True
                message = f"{self.name} completed successfully."
            else:
                success = False
                message = f"{self.name} failed: No feasible design candidates found."

        result = OptimizationResult(
            winning_candidate=best_candidate,
            generated_specification=spec,
            success=success,
            message=message,
            evaluated_count=len(candidates),
            feasible_count=len(feasible_candidates),
            history=history,
            rejected_summary=self._summarize_rejections(history),
            execution_time_seconds=timer.elapsed,
            iteration_count=context.iteration_count,
            diagnostics={"name": self.name}
        )
        
        self.logger.log_summary(result)
        return result

    def initialize(self, context: OptimizationContext) -> None:
        """Lifecycle hook allowing subclass parameter setups."""
        pass

    @abstractmethod
    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """Generates raw candidate parameter selections to explore."""
        pass

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """Runs registered validation checks."""
        return self.constraints.evaluate_constraints(candidate, context)

    @abstractmethod
    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """Populates derived variables by calling subsystem tools."""
        pass

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """Calculates candidate fitness score using registered objective terms."""
        return self.objective.calculate_scores(candidate, context)

    def select_best_candidate(self, feasible_candidates: List[OptimizationCandidate], context: OptimizationContext) -> OptimizationCandidate | None:
        """Identifies candidate with lowest overall objective cost."""
        if not feasible_candidates:
            return None
        return min(feasible_candidates, key=lambda c: c.overall_score)

    @abstractmethod
    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """Generates the structured sub-spec handoff from the winner candidate."""
        pass

    def _summarize_rejections(self, history: List[OptimizationCandidate]) -> Dict[str, int]:
        summary = {}
        for cand in history:
            if not cand.constraints_passed:
                for name, res in cand.constraint_results.items():
                    if res["status"] == "FAIL":
                        summary[name] = summary.get(name, 0) + 1
        return summary
