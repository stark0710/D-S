"""
Torq Wings VTOL Phase 7 - Dedicated Optimization & Pareto Test Suite.

Comprehensive verification of:
1. Design-variable validation
2. Bound validation
3. Deterministic candidate evaluation
4. Candidate hashing
5. Duplicate elimination
6. Objective direction handling
7. Constraint evaluation
8. Infeasible candidate detection
9. Pareto dominance
10. Pareto non-dominance
11. Pareto front extraction
12. Infeasible candidates excluded from feasible Pareto front
13. Serialization
14. Empty feasible set
15. Single feasible candidate
16. Multiple identical candidates
17. Mixed minimize/maximize objectives
18. Provenance propagation
19. Deferred parameter handling
20. CLI execution
21. Zero Fixed-Wing modification invariant
"""

import json
import os
import subprocess
import sys
import pytest

from backend.design.vtol.optimization import (
    DesignCandidate,
    DesignEvaluation,
    DesignVariable,
    OptimizationVariable,
    OptimizationStatus,
    EvaluationStatus,
    OptimizationProvenance,
    ObjectiveDefinition,
    ObjectiveDirection,
    ConstraintDefinition,
    ConstraintResult,
    STANDARD_VTOL_VARIABLES,
    STANDARD_OBJECTIVES,
    STANDARD_CONSTRAINTS,
    VTOLDesignEvaluator,
    VTOLOptimizationPipeline,
    OptimizationEngine,
    dominates,
    extract_pareto_front,
    extract_best_by_objective,
    validate_variable_bounds,
)


# ==============================================================================
# 1. DESIGN-VARIABLE VALIDATION
# ==============================================================================
def test_design_variable_validation():
    var = DesignVariable(
        name="payload_mass_kg",
        base_value=2.5,
        min_bound=1.0,
        max_bound=5.0,
        units="kg",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
        is_active=True,
        description="Mission payload",
    )
    assert var.name == "payload_mass_kg"
    assert var.base_value == 2.5
    assert var.value == 2.5
    assert var.min_bound == 1.0
    assert var.max_bound == 5.0
    assert var.units == "kg"
    assert var.is_active is True
    assert var.validate_value(2.5) is True
    assert var.validate_value(0.5) is False
    assert var.validate_value(6.0) is False

    d = var.to_dict()
    assert d["name"] == "payload_mass_kg"
    assert d["provenance"] == "PROJECT_REQUIREMENT"


# ==============================================================================
# 2. BOUND VALIDATION
# ==============================================================================
def test_bound_validation():
    # Valid variable
    valid_var = DesignVariable(name="valid", base_value=2.0, min_bound=1.0, max_bound=3.0)
    validate_variable_bounds(valid_var)  # Should not raise

    # Invalid variable bounds
    with pytest.raises(ValueError, match="cannot exceed max_bound"):
        DesignVariable(name="invalid", base_value=2.0, min_bound=5.0, max_bound=2.0)


# ==============================================================================
# 3. DETERMINISTIC CANDIDATE EVALUATION
# ==============================================================================
def test_deterministic_candidate_evaluation():
    evaluator1 = VTOLDesignEvaluator()
    evaluator2 = VTOLDesignEvaluator()

    cand = DesignCandidate(
        candidate_id="DET_TEST",
        variables={"payload_mass_kg": 2.5, "cruise_speed_kmh": 85.0},
        mission_overrides={"target_range": 35.0, "target_flight_time": 25.0},
    )

    ev1 = evaluator1.evaluate_candidate(cand)
    ev2 = evaluator2.evaluate_candidate(cand)

    assert ev1.is_feasible is True
    assert ev2.is_feasible is True
    assert ev1.mtow_kg == pytest.approx(ev2.mtow_kg, rel=1e-5)
    assert ev1.static_margin_pct == pytest.approx(ev2.static_margin_pct, rel=1e-5)
    assert ev1.neutral_point_x_m == pytest.approx(ev2.neutral_point_x_m, rel=1e-5)
    assert ev1.cg_x_m == pytest.approx(ev2.cg_x_m, rel=1e-5)
    assert ev1.total_mission_energy_wh == pytest.approx(ev2.total_mission_energy_wh, rel=1e-5)


# ==============================================================================
# 4. CANDIDATE HASHING
# ==============================================================================
def test_candidate_hashing():
    c1 = DesignCandidate(
        candidate_id="C1",
        variables={"a": 1.0, "b": 2.00001},
        mission_overrides={"m": 10},
    )
    # Different variable order and near-identical floating point within rounding
    c2 = DesignCandidate(
        candidate_id="C2",
        variables={"b": 2.00004, "a": 1.0},
        mission_overrides={"m": 10},
    )
    assert c1.candidate_hash == c2.candidate_hash

    # Truly different candidate
    c3 = DesignCandidate(
        candidate_id="C3",
        variables={"a": 1.5, "b": 2.0},
        mission_overrides={"m": 10},
    )
    assert c1.candidate_hash != c3.candidate_hash


# ==============================================================================
# 5. DUPLICATE ELIMINATION
# ==============================================================================
def test_duplicate_elimination():
    evaluator = VTOLDesignEvaluator()
    pipeline = VTOLOptimizationPipeline(evaluator=evaluator)

    c1 = DesignCandidate(candidate_id="C1", variables={"payload_mass_kg": 2.5, "cruise_speed_kmh": 85.0})
    c2 = DesignCandidate(candidate_id="C2", variables={"payload_mass_kg": 2.5, "cruise_speed_kmh": 85.0})
    c3 = DesignCandidate(candidate_id="C3", variables={"payload_mass_kg": 2.5, "cruise_speed_kmh": 85.0})

    result = pipeline.run_optimization(candidates=[c1, c2, c3])
    assert result.total_candidates == 3
    assert result.evaluated_candidates == 1
    assert result.cached_evaluations == 2
    assert result.feasible_count == 3


# ==============================================================================
# 6. OBJECTIVE DIRECTION HANDLING
# ==============================================================================
def test_objective_direction_handling():
    min_obj = ObjectiveDefinition(
        name="weight",
        direction=ObjectiveDirection.MINIMIZE,
        units="kg",
        source="spec.mtow_kg",
    )
    max_obj = ObjectiveDefinition(
        name="endurance",
        direction=ObjectiveDirection.MAXIMIZE,
        units="min",
        source="spec.endurance_min",
    )

    # For MINIMIZE, lower value yields lower (better) score
    assert min_obj.to_minimization_score(7.0) < min_obj.to_minimization_score(8.0)
    # For MAXIMIZE, higher value yields lower (better) score
    assert max_obj.to_minimization_score(60.0) < max_obj.to_minimization_score(30.0)


# ==============================================================================
# 7. CONSTRAINT EVALUATION
# ==============================================================================
def test_constraint_evaluation():
    con = ConstraintDefinition(
        name="mtow_limit",
        min_bound=None,
        max_bound=10.0,
        units="kg",
        provenance=OptimizationProvenance.PROJECT_REQUIREMENT,
    )

    res_pass = con.evaluate(7.869)
    assert res_pass.is_passed is True
    assert res_pass.violation_magnitude == 0.0

    res_fail = con.evaluate(11.5)
    assert res_fail.is_passed is False
    assert res_fail.violation_magnitude == pytest.approx(1.5, abs=1e-4)


# ==============================================================================
# 8. INFEASIBLE CANDIDATE DETECTION
# ==============================================================================
def test_infeasible_candidate_detection():
    evaluator = VTOLDesignEvaluator()

    # Strict constraint that will definitely fail for 7.869 kg MTOW
    strict_con = ConstraintDefinition(
        name="strict_mtow",
        min_bound=None,
        max_bound=5.0,  # Below achievable MTOW
        units="kg",
        attribute_key="mtow_kg",
    )

    cand = DesignCandidate(
        candidate_id="INFEAS_TEST",
        variables={"payload_mass_kg": 2.5, "cruise_speed_kmh": 85.0},
    )
    ev = evaluator.evaluate_candidate(cand, constraints=[strict_con])

    assert ev.is_feasible is False
    assert ev.status == EvaluationStatus.INFEASIBLE
    assert "strict_mtow" in ev.violated_constraints


# ==============================================================================
# 9. PARETO DOMINANCE
# ==============================================================================
def test_pareto_dominance():
    obj_mtow = ObjectiveDefinition(name="mtow", direction=ObjectiveDirection.MINIMIZE, units="kg", source="")
    obj_endur = ObjectiveDefinition(name="endurance", direction=ObjectiveDirection.MAXIMIZE, units="min", source="")
    objectives = [obj_mtow, obj_endur]

    # Candidate A: 7.0 kg, 30 min
    # Candidate B: 8.0 kg, 25 min (strictly worse in both)
    eval_a = DesignEvaluation(
        candidate_id="A",
        candidate_hash="ha",
        status=EvaluationStatus.FEASIBLE,
        is_feasible=True,
        objectives={"mtow": 7.0, "endurance": 30.0},
    )
    eval_b = DesignEvaluation(
        candidate_id="B",
        candidate_hash="hb",
        status=EvaluationStatus.FEASIBLE,
        is_feasible=True,
        objectives={"mtow": 8.0, "endurance": 25.0},
    )

    assert dominates(eval_a, eval_b, objectives) is True
    assert dominates(eval_b, eval_a, objectives) is False


# ==============================================================================
# 10. PARETO NON-DOMINANCE (TRADEOFF)
# ==============================================================================
def test_pareto_non_dominance():
    obj_mtow = ObjectiveDefinition(name="mtow", direction=ObjectiveDirection.MINIMIZE, units="kg", source="")
    obj_endur = ObjectiveDefinition(name="endurance", direction=ObjectiveDirection.MAXIMIZE, units="min", source="")
    objectives = [obj_mtow, obj_endur]

    # Candidate A: lighter (7.0 kg), but lower endurance (25 min)
    # Candidate B: heavier (8.0 kg), but higher endurance (35 min)
    eval_a = DesignEvaluation(
        candidate_id="A",
        candidate_hash="ha",
        status=EvaluationStatus.FEASIBLE,
        is_feasible=True,
        objectives={"mtow": 7.0, "endurance": 25.0},
    )
    eval_b = DesignEvaluation(
        candidate_id="B",
        candidate_hash="hb",
        status=EvaluationStatus.FEASIBLE,
        is_feasible=True,
        objectives={"mtow": 8.0, "endurance": 35.0},
    )

    assert dominates(eval_a, eval_b, objectives) is False
    assert dominates(eval_b, eval_a, objectives) is False


# ==============================================================================
# 11. PARETO FRONT EXTRACTION
# ==============================================================================
def test_pareto_front_extraction():
    obj_mtow = ObjectiveDefinition(name="mtow", direction=ObjectiveDirection.MINIMIZE, units="kg", source="")
    obj_endur = ObjectiveDefinition(name="endurance", direction=ObjectiveDirection.MAXIMIZE, units="min", source="")
    objectives = [obj_mtow, obj_endur]

    # A: 7.0 kg, 25 min (tradeoff)
    # B: 8.0 kg, 35 min (tradeoff)
    # C: 9.0 kg, 20 min (dominated by both A and B)
    eval_a = DesignEvaluation(candidate_id="A", candidate_hash="ha", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 7.0, "endurance": 25.0})
    eval_b = DesignEvaluation(candidate_id="B", candidate_hash="hb", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 8.0, "endurance": 35.0})
    eval_c = DesignEvaluation(candidate_id="C", candidate_hash="hc", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 9.0, "endurance": 20.0})

    partition = extract_pareto_front([eval_a, eval_b, eval_c], objectives)

    assert partition.pareto_count == 2
    front_ids = {c.candidate_id for c in partition.pareto_front}
    assert front_ids == {"A", "B"}
    assert partition.dominated_count == 1
    assert partition.dominated_candidates[0].candidate_id == "C"


# ==============================================================================
# 12. INFEASIBLE CANDIDATES EXCLUDED FROM FEASIBLE PARETO FRONT
# ==============================================================================
def test_infeasible_excluded_from_pareto_front():
    obj_mtow = ObjectiveDefinition(name="mtow", direction=ObjectiveDirection.MINIMIZE, units="kg", source="")
    objectives = [obj_mtow]

    # Feasible design: 7.8 kg
    eval_feas = DesignEvaluation(candidate_id="FEAS", candidate_hash="hf", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 7.8})
    # Infeasible design with superficially better weight (5.0 kg) but constraint failed
    eval_infeas = DesignEvaluation(candidate_id="INFEAS", candidate_hash="hi", status=EvaluationStatus.INFEASIBLE, is_feasible=False, objectives={"mtow": 5.0})

    partition = extract_pareto_front([eval_feas, eval_infeas], objectives)

    assert partition.pareto_count == 1
    assert partition.pareto_front[0].candidate_id == "FEAS"
    assert partition.infeasible_count == 1
    assert partition.infeasible_candidates[0].candidate_id == "INFEAS"


# ==============================================================================
# 13. SERIALIZATION
# ==============================================================================
def test_serialization():
    pipeline = VTOLOptimizationPipeline()
    cand = DesignCandidate(candidate_id="SER_TEST", variables={"payload_mass_kg": 2.5, "cruise_speed_kmh": 85.0})
    res = pipeline.run_optimization(candidates=[cand])

    res_dict = res.to_dict()
    assert isinstance(res_dict, dict)
    assert res_dict["optimization_status"] == OptimizationStatus.COMPLETED.value
    assert "pareto_front" in res_dict
    assert "problem_definition" in res_dict
    assert "provenance_matrix" in res_dict

    # Ensure JSON serializable with no error
    json_bytes = json.dumps(res_dict)
    assert len(json_bytes) > 0


# ==============================================================================
# 14. EMPTY FEASIBLE SET
# ==============================================================================
def test_empty_feasible_set():
    obj_mtow = ObjectiveDefinition(name="mtow", direction=ObjectiveDirection.MINIMIZE, units="kg", source="")
    objectives = [obj_mtow]

    eval_infeas1 = DesignEvaluation(candidate_id="I1", candidate_hash="h1", status=EvaluationStatus.INFEASIBLE, is_feasible=False, objectives={"mtow": 5.0})
    eval_infeas2 = DesignEvaluation(candidate_id="I2", candidate_hash="h2", status=EvaluationStatus.INFEASIBLE, is_feasible=False, objectives={"mtow": 6.0})

    partition = extract_pareto_front([eval_infeas1, eval_infeas2], objectives)
    assert partition.pareto_count == 0
    assert partition.infeasible_count == 2


# ==============================================================================
# 15. SINGLE FEASIBLE CANDIDATE
# ==============================================================================
def test_single_feasible_candidate():
    obj_mtow = ObjectiveDefinition(name="mtow", direction=ObjectiveDirection.MINIMIZE, units="kg", source="")
    eval_single = DesignEvaluation(candidate_id="SOLO", candidate_hash="hs", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 7.869})

    partition = extract_pareto_front([eval_single], [obj_mtow])
    assert partition.pareto_count == 1
    assert partition.pareto_front[0].candidate_id == "SOLO"


# ==============================================================================
# 16. MULTIPLE IDENTICAL CANDIDATES
# ==============================================================================
def test_multiple_identical_candidates():
    obj_mtow = ObjectiveDefinition(name="mtow", direction=ObjectiveDirection.MINIMIZE, units="kg", source="")
    c1 = DesignEvaluation(candidate_id="ID1", candidate_hash="h1", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 7.8})
    c2 = DesignEvaluation(candidate_id="ID2", candidate_hash="h2", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 7.8})

    # Neither strictly dominates the other because neither is strictly better
    assert dominates(c1, c2, [obj_mtow]) is False
    assert dominates(c2, c1, [obj_mtow]) is False

    partition = extract_pareto_front([c1, c2], [obj_mtow])
    assert partition.pareto_count == 2


# ==============================================================================
# 17. MIXED MINIMIZE / MAXIMIZE OBJECTIVES
# ==============================================================================
def test_mixed_minimize_maximize_objectives():
    objs = [
        ObjectiveDefinition(name="mtow", direction=ObjectiveDirection.MINIMIZE, units="kg", source=""),
        ObjectiveDefinition(name="energy", direction=ObjectiveDirection.MINIMIZE, units="Wh", source=""),
        ObjectiveDefinition(name="endurance", direction=ObjectiveDirection.MAXIMIZE, units="min", source=""),
        ObjectiveDefinition(name="range", direction=ObjectiveDirection.MAXIMIZE, units="km", source=""),
    ]

    # Best design: lower MTOW, lower energy, higher endurance, higher range
    best = DesignEvaluation(candidate_id="BEST", candidate_hash="h_b", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 7.0, "energy": 250.0, "endurance": 35.0, "range": 45.0})
    worse = DesignEvaluation(candidate_id="WORSE", candidate_hash="h_w", status=EvaluationStatus.FEASIBLE, is_feasible=True, objectives={"mtow": 8.0, "energy": 300.0, "endurance": 25.0, "range": 30.0})

    assert dominates(best, worse, objs) is True
    assert dominates(worse, best, objs) is False


# ==============================================================================
# 18. PROVENANCE PROPAGATION
# ==============================================================================
def test_provenance_propagation():
    pipeline = VTOLOptimizationPipeline()
    cand = DesignCandidate(candidate_id="PROV_TEST", variables={"payload_mass_kg": 2.5, "cruise_speed_kmh": 85.0})
    res = pipeline.run_optimization(candidates=[cand])

    matrix = res.provenance_matrix
    assert "static_margin_boundaries_+5_+15_mac" in matrix
    assert matrix["static_margin_boundaries_+5_+15_mac"] == "CONFIGURABLE_ASSUMPTION"
    assert "aft_cg_boundary_44.23_mac" in matrix
    assert matrix["aft_cg_boundary_44.23_mac"] == "ASSUMPTION_BASED"
    assert "6dof_dynamic_stability" in matrix
    assert matrix["6dof_dynamic_stability"] == "DEFERRED"


# ==============================================================================
# 19. DEFERRED PARAMETER HANDLING
# ==============================================================================
def test_deferred_parameter_handling():
    pipeline = VTOLOptimizationPipeline()
    cand = DesignCandidate(candidate_id="DEF_TEST", variables={"payload_mass_kg": 2.5, "cruise_speed_kmh": 85.0})
    res = pipeline.run_optimization(candidates=[cand])

    assert len(res.deferred_items) >= 4
    assert any("6-DOF" in item for item in res.deferred_items)
    assert any("Phase 8" in item for item in res.deferred_items)


# ==============================================================================
# 20. CLI EXECUTION
# ==============================================================================
def test_cli_execution(tmp_path):
    cli_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts", "run_vtol_optimization.py")
    cli_path = os.path.abspath(cli_path)

    cmd = [
        sys.executable,
        cli_path,
        "--non-interactive",
        "--grid-resolution", "2",
        "--output-dir", str(tmp_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "PHASE 7 OPTIMIZATION EXECUTION COMPLETE" in result.stdout
    assert "PARETO FRONT CANDIDATES" in result.stdout

    # Check that output JSON was generated
    files = os.listdir(str(tmp_path))
    assert any(f.endswith(".json") for f in files)
    assert any(f.endswith(".md") for f in files)


# ==============================================================================
# 21. FIXED-WING MODIFICATION AUDIT
# ==============================================================================
def test_no_fixed_wing_modifications():
    """Verify zero Phase 7 source modifications to backend/design/fixed_wing/."""
    fixed_wing_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "design", "fixed_wing")
    )
    # Check that no python file in fixed_wing was modified after Phase 7 started
    this_file_mtime = os.path.getmtime(os.path.abspath(__file__))
    recently_modified = []
    for root, _, files in os.walk(fixed_wing_dir):
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                if os.path.getmtime(fpath) >= this_file_mtime - 1800:
                    recently_modified.append(f)

    assert len(recently_modified) == 0, f"Fixed-Wing files modified during Phase 7: {recently_modified}"
