import pytest
from typing import List, Any
from backend.design.common.optimization import (
    OptimizationContext,
    OptimizationCandidate,
    OptimizationResult,
    ConstraintManager,
    ObjectiveFunction,
    OptimizationLogger,
    OptimizationReport,
    normalize_value,
    weighted_sum,
    format_diagnostics,
    OptimizerBase,
)

class MockOptimizer(OptimizerBase):
    """
    Dummy concrete optimizer implementation to validate framework base class lifecycles.
    """
    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        return [
            OptimizationCandidate(design_variables={"x": 1.0, "y": 2.0}),
            OptimizationCandidate(design_variables={"x": 2.0, "y": 3.0}),
            OptimizationCandidate(design_variables={"x": 3.0, "y": 4.0}),
        ]

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        x = candidate.design_variables["x"]
        y = candidate.design_variables["y"]
        candidate.derived_variables["sum"] = x + y

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        return {
            "x_opt": candidate.design_variables["x"],
            "y_opt": candidate.design_variables["y"],
            "sum_opt": candidate.derived_variables["sum"]
        }

def test_context_and_models():
    """Verify that models and contexts hold correct states."""
    ctx = OptimizationContext(requirements="reqs_mock", configuration="config_mock")
    assert ctx.requirements == "reqs_mock"
    assert ctx.configuration == "config_mock"
    assert ctx.iteration_count == 0
    assert isinstance(ctx.previous_specifications, dict)

    cand = OptimizationCandidate(design_variables={"val": 10})
    assert cand.design_variables["val"] == 10
    assert cand.constraints_passed is True
    assert cand.status == "PENDING"

    res = OptimizationResult(winning_candidate=cand, generated_specification="spec", success=True, message="Success")
    assert res.success is True
    assert res.winning_candidate.design_variables["val"] == 10
    assert res.generated_specification == "spec"

def test_constraint_manager():
    """Verify ConstraintManager registers and evaluates checks."""
    manager = ConstraintManager()
    
    # 1. Register a mock constraint checking x < 2.5
    def check_x_limit(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
        x = candidate.design_variables.get("x", 0.0)
        if x > 2.5:
            return False, f"x ({x}) exceeds limit 2.5."
        return True, ""

    manager.add_constraint("x_limit", check_x_limit)
    ctx = OptimizationContext(requirements=None)

    cand1 = OptimizationCandidate(design_variables={"x": 1.0})
    passed1 = manager.evaluate_constraints(cand1, ctx)
    assert passed1 is True
    assert cand1.constraints_passed is True
    assert cand1.constraint_results["x_limit"]["status"] == "PASS"

    cand2 = OptimizationCandidate(design_variables={"x": 3.0})
    passed2 = manager.evaluate_constraints(cand2, ctx)
    assert passed2 is False
    assert cand2.constraints_passed is False
    assert cand2.constraint_results["x_limit"]["status"] == "FAIL"
    assert "exceeds limit 2.5" in cand2.constraint_results["x_limit"]["reason"]

def test_objective_function():
    """Verify ObjectiveFunction handles registration and scoring weights."""
    obj = ObjectiveFunction()
    
    # 1. Minimize x: cost is x
    obj.add_objective("minimize_x", lambda c, ctx: c.design_variables["x"], weight=2.0, minimize=True)
    # 2. Maximize y: cost is -y
    obj.add_objective("maximize_y", lambda c, ctx: c.design_variables["y"], weight=1.0, minimize=False)

    ctx = OptimizationContext(requirements=None)
    cand = OptimizationCandidate(design_variables={"x": 2.0, "y": 5.0})
    
    # Expected overall cost = 2.0 * 2.0 (minimize) - 1.0 * 5.0 (maximize) = 4.0 - 5.0 = -1.0
    score = obj.calculate_scores(cand, ctx)
    assert score == pytest.approx(-1.0)
    assert cand.overall_score == pytest.approx(-1.0)
    assert cand.objective_scores["minimize_x"] == 2.0
    assert cand.objective_scores["maximize_y"] == 5.0

def test_utilities():
    """Verify utility formulas (normalization, weighted sum)."""
    assert normalize_value(5.0, 0.0, 10.0) == 0.5
    assert normalize_value(5.0, 10.0, 10.0) == 0.0  # division by zero guard

    assert weighted_sum([2.0, 3.0], [0.5, 2.0]) == pytest.approx(7.0)
    with pytest.raises(ValueError):
        weighted_sum([1.0], [1.0, 2.0])

    diag = format_diagnostics({"a": 1, "b": "test"})
    assert "a: 1" in diag
    assert "b: test" in diag

def test_optimizer_base_lifecycle():
    """Verify OptimizerBase standard lifecycle stages execution."""
    optimizer = MockOptimizer("MockOptimizer")
    ctx = OptimizationContext(requirements="reqs")

    # Add constraints
    def constraint_y_limit(candidate: OptimizationCandidate, context: OptimizationContext) -> tuple[bool, str]:
        y = candidate.design_variables.get("y", 0.0)
        if y > 3.5:
            return False, "y exceeds limit 3.5"
        return True, ""
    
    optimizer.constraints.add_constraint("y_limit", constraint_y_limit)

    # Add objective (minimize x)
    optimizer.objective.add_objective("min_x", lambda c, ctx: c.design_variables["x"], weight=1.0, minimize=True)

    result = optimizer.optimize(ctx)

    assert result.success is True
    assert result.evaluated_count == 3
    assert result.feasible_count == 2  # Candidates with y=2.0 and y=3.0 pass. y=4.0 fails y_limit constraint.
    assert result.iteration_count == 3

    # Winning candidate should have lowest x among feasible ones (x=1.0, y=2.0)
    assert result.winning_candidate is not None
    assert result.winning_candidate.design_variables["x"] == 1.0
    assert result.winning_candidate.design_variables["y"] == 2.0
    assert result.winning_candidate.derived_variables["sum"] == 3.0
    assert result.generated_specification["sum_opt"] == 3.0

    # Rejected summary check
    assert result.rejected_summary["y_limit"] == 1

def test_optimization_report_generation():
    """Verify that reporting formats results correctly into markdown files."""
    cand = OptimizationCandidate(design_variables={"x": 1.2}, derived_variables={"sum": 3.4}, overall_score=0.25)
    cand.constraint_results = {"c1": {"status": "PASS", "reason": ""}}
    cand.objective_scores = {"o1": 0.25}

    result = OptimizationResult(
        winning_candidate=cand,
        generated_specification={"a": 1},
        success=True,
        message="Optimal design located.",
        evaluated_count=1,
        feasible_count=1,
        history=[cand],
        execution_time_seconds=0.005,
        iteration_count=1
    )

    md = OptimizationReport.generate_markdown(result)
    assert "## 1. Optimization Executive Summary" in md
    assert "SUCCESS" in md
    assert "x" in md
    assert "1.2" in md
    assert "sum" in md
    assert "3.4" in md
    assert "Winning Score" in md
