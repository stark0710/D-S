"""
Fixed-Wing Wing Planform Optimizer

Main orchestrator running parameter sweeps, checking constraints, and scoring candidates.
"""

import time
from typing import List, Dict, Any
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
from backend.design.fixed_wing.wing.wing_engine import WingEngine
from backend.design.fixed_wing.wing.wing_validator import WingValidationError
from backend.design.fixed_wing.optimization.optimization_models import PlanformCandidate, OptimizationBounds
from backend.design.fixed_wing.optimization.optimization_result import WingOptimizationResult
from backend.design.fixed_wing.optimization.candidate_generator import CandidateGenerator, GridSearchCandidateGenerator
from backend.design.fixed_wing.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.optimization.optimization_constraints import OptimizationConstraints
from backend.design.fixed_wing.optimization.optimization_objective import OptimizationObjective, WeightedMultiObjective

class WingPlanformOptimizer:
    """
    Facade managing candidate sweep generation and evaluation to identify optimal planforms.
    """
    def __init__(self, engine: WingEngine | None = None) -> None:
        self._engine = engine if engine else WingEngine()
        self._evaluator = CandidateEvaluator(self._engine)

    def optimize(
        self,
        base_requirements: WingRequirements,
        bounds: OptimizationBounds,
        generator: CandidateGenerator | None = None,
        constraints: OptimizationConstraints | None = None,
        objective: OptimizationObjective | None = None,
    ) -> WingOptimizationResult:
        """
        Runs the optimization sweep to locate the best-scoring feasible candidate.
        """
        start_time = time.time()
        
        if generator is None:
            generator = GridSearchCandidateGenerator()
        if constraints is None:
            max_span_m = base_requirements.metadata.get("max_wingspan_m")
            constraints = OptimizationConstraints(max_wingspan_m=max_span_m)
        if objective is None:
            objective = WeightedMultiObjective()

        candidates = generator.generate(bounds)
        
        best_candidate = None
        best_result = None
        best_score = float("inf")
        history = []
        feasible_count = 0
        evaluated_count = 0

        for candidate in candidates:
            evaluated_count += 1
            is_feasible = False
            score = None
            errors = []
            result = None

            try:
                # 1. Run sizing/evaluation
                result = self._evaluator.evaluate(candidate, base_requirements)
                
                # 2. Check feasibility constraints
                passed_constraints, violations = constraints.check_constraints(candidate, result)
                if passed_constraints:
                    is_feasible = True
                    feasible_count += 1
                    # 3. Calculate cost score
                    score = objective.calculate_score(candidate, result)
                    
                    if score < best_score:
                        best_score = score
                        best_candidate = candidate
                        best_result = result
                else:
                    errors.extend(violations)
            except WingValidationError as e:
                errors.append(f"WingValidationError: {e}")
            except Exception as e:
                errors.append(f"Exception: {type(e).__name__}: {e}")

            history.append({
                "candidate": {
                    "aspect_ratio": candidate.aspect_ratio,
                    "taper_ratio": candidate.taper_ratio,
                    "sweep_angle_deg": candidate.sweep_angle_deg,
                    "wing_loading_kg_m2": candidate.wing_loading_kg_m2
                },
                "is_feasible": is_feasible,
                "score": score,
                "errors": errors
            })

        execution_time = time.time() - start_time
        success = best_candidate is not None
        message = (
            f"Successfully optimized wing planform. Found optimal candidate at score: {best_score:.3f}."
            if success
            else "Optimization failed: Zero feasible planform candidates were found."
        )

        return WingOptimizationResult(
            best_candidate=best_candidate,
            best_wing_result=best_result,
            success=success,
            message=message,
            evaluated_count=evaluated_count,
            feasible_count=feasible_count,
            history=history,
            execution_time_seconds=round(execution_time, 4)
        )
