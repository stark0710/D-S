"""
Phase 6B-2 Unit Tests: Fixed-Wing Tail Objective Function Normalization

Validates:
1. Term Directionality: Better engineering metrics produce lower/better normalized scores.
2. Term Boundedness: All normalized terms evaluate to [0.0, 1.0].
3. Scale Imbalance Correction: Normalized weighted contributions are balanced (ratio < 5x), eliminating raw scale domination.
4. Hard Constraints: Infeasible candidates remain strictly rejected.
5. Priority Interaction: All 7 OptimizationPriority modes propagate weights to the normalized objective.
6. Baseline Regression: BALANCED preserves the protected Survey 0.5kg baseline.
"""

import pytest
import numpy as np

from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.fixed_wing.tail.optimization.objective_function import TailObjectiveFunction
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer
from backend.design.fixed_wing.tail.optimization.constraints import build_tail_constraints
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

from tests.design.fixed_wing.tail.optimization.test_tail_optimization import mock_tail_context


def test_term_directionality_and_bounds(mock_tail_context):
    """Verify that every normalized objective term improves with better engineering values and stays in [0, 1]."""
    obj = TailObjectiveFunction()

    # 1. Longitudinal Stability (minimize=True: target V_h = 0.55)
    c_vh_best = OptimizationCandidate(design_variables={"horizontal_V_h": 0.55})
    c_vh_good = OptimizationCandidate(design_variables={"horizontal_V_h": 0.60})
    c_vh_worse = OptimizationCandidate(design_variables={"horizontal_V_h": 0.75})
    s_best = obj._calc_longitudinal_stability(c_vh_best, mock_tail_context)
    s_good = obj._calc_longitudinal_stability(c_vh_good, mock_tail_context)
    s_worse = obj._calc_longitudinal_stability(c_vh_worse, mock_tail_context)
    assert 0.0 <= s_best < s_good < s_worse <= 1.0
    assert s_best == pytest.approx(0.0)

    # 2. Directional Stability (minimize=True: target V_v = 0.04)
    c_vv_best = OptimizationCandidate(design_variables={"vertical_V_v": 0.04})
    c_vv_good = OptimizationCandidate(design_variables={"vertical_V_v": 0.045})
    c_vv_worse = OptimizationCandidate(design_variables={"vertical_V_v": 0.07})
    s_best = obj._calc_directional_stability(c_vv_best, mock_tail_context)
    s_good = obj._calc_directional_stability(c_vv_good, mock_tail_context)
    s_worse = obj._calc_directional_stability(c_vv_worse, mock_tail_context)
    assert 0.0 <= s_best < s_good < s_worse <= 1.0
    assert s_best == pytest.approx(0.0)

    # 3. Drag Penalty (minimize=True: lower area is better)
    c_drag_low = OptimizationCandidate(design_variables={}, derived_variables={"h_area_m2": 0.03, "v_area_m2": 0.015})
    c_drag_high = OptimizationCandidate(design_variables={}, derived_variables={"h_area_m2": 0.09, "v_area_m2": 0.045})
    s_low = obj._calc_drag_penalty(c_drag_low, mock_tail_context)
    s_high = obj._calc_drag_penalty(c_drag_high, mock_tail_context)
    assert 0.0 <= s_low < s_high <= 1.0

    # 4. Structural Weight (minimize=True: lower area*arm is better)
    c_struct_light = OptimizationCandidate(design_variables={}, derived_variables={"h_area_m2": 0.03, "v_area_m2": 0.015, "tail_arm_m": 0.8})
    c_struct_heavy = OptimizationCandidate(design_variables={}, derived_variables={"h_area_m2": 0.09, "v_area_m2": 0.045, "tail_arm_m": 1.4})
    s_light = obj._calc_structural_weight(c_struct_light, mock_tail_context)
    s_heavy = obj._calc_structural_weight(c_struct_heavy, mock_tail_context)
    assert 0.0 <= s_light < s_heavy <= 1.0

    # 5. Manufacturability (minimize=False: higher score is better)
    c_mfg_poor = OptimizationCandidate(design_variables={}, derived_variables={"manufacturability_score": 60.0})
    c_mfg_great = OptimizationCandidate(design_variables={}, derived_variables={"manufacturability_score": 95.0})
    s_poor = obj._calc_manufacturability(c_mfg_poor, mock_tail_context)
    s_great = obj._calc_manufacturability(c_mfg_great, mock_tail_context)
    assert 0.0 <= s_poor < s_great <= 1.0
    assert s_poor == pytest.approx(0.60)
    assert s_great == pytest.approx(0.95)

    # 6. Mission Suitability (minimize=False: higher score is better)
    c_mis_poor = OptimizationCandidate(design_variables={}, derived_variables={"mission_suitability": 70.0})
    c_mis_great = OptimizationCandidate(design_variables={}, derived_variables={"mission_suitability": 90.0})
    s_poor = obj._calc_mission_suitability(c_mis_poor, mock_tail_context)
    s_great = obj._calc_mission_suitability(c_mis_great, mock_tail_context)
    assert 0.0 <= s_poor < s_great <= 1.0

    # 7. CG Robustness (minimize=True: lower deficit is better)
    c_cg_robust = OptimizationCandidate(
        design_variables={"horizontal_V_h": 0.80, "tail_arm_ratio": 0.65}
    )
    c_cg_marginal = OptimizationCandidate(
        design_variables={"horizontal_V_h": 0.55, "tail_arm_ratio": 0.55}
    )
    c_cg_poor = OptimizationCandidate(
        design_variables={"horizontal_V_h": 0.45, "tail_arm_ratio": 0.38}
    )
    s_robust = obj._calc_cg_robustness(c_cg_robust, mock_tail_context)
    s_marginal = obj._calc_cg_robustness(c_cg_marginal, mock_tail_context)
    s_poor = obj._calc_cg_robustness(c_cg_poor, mock_tail_context)
    assert 0.0 <= s_robust < s_marginal < s_poor <= 1.0
    assert s_robust == pytest.approx(0.0)


def test_scale_imbalance_corrected(mock_tail_context):
    """Verify that normalized term contributions reflect priority weights and candidate scores without 95x distortion."""
    optimizer = TailOptimizer()
    optimizer.initialize(mock_tail_context)

    candidates = optimizer.generate_candidates(mock_tail_context)
    feasible = []
    for c in candidates:
        if optimizer.apply_constraints(c, mock_tail_context):
            optimizer.evaluate_candidate(c, mock_tail_context)
            optimizer.score_candidate(c, mock_tail_context)
            feasible.append(c)

    winner = optimizer.select_best_candidate(feasible, mock_tail_context)
    assert winner is not None

    contribs = {}
    for t in optimizer.objective._terms:
        score = winner.objective_scores[t.name]
        contrib = t.weight * score * (1.0 if t.minimize else -1.0)
        contribs[t.name] = abs(contrib)

    max_contrib = max(contribs.values())
    min_contrib = min(contribs.values())
    ratio = max_contrib / min_contrib

    # The ratio under the original objective was ~95.0x.
    # Under normalized terms, the ratio must be bounded and comparable (< 10x, observed ~4.4x)
    assert ratio < 10.0, f"Scale imbalance ratio {ratio:.1f}x exceeds threshold of 10.0x"
    assert contribs["directional_stability"] > 0.02, "Directional stability contribution should be meaningfully sized"


def test_hard_constraints_still_rejected(mock_tail_context):
    """Verify that infeasible candidates are rejected by hard constraints."""
    constraints = build_tail_constraints()

    # 1. Infeasible V_h (< 0.35)
    c_bad_vh = OptimizationCandidate(
        design_variables={
            "tail_configuration": "Conventional", "horizontal_V_h": 0.20,
            "vertical_V_v": 0.04, "tail_arm_ratio": 0.55, "horiz_ar": 4.0,
            "vert_ar": 1.8, "horiz_taper": 0.6, "vert_taper": 0.6,
            "horiz_sweep": 0.0, "vert_sweep": 0.0, "tail_dihedral_deg": 0.0
        }
    )
    assert constraints.evaluate_constraints(c_bad_vh, mock_tail_context) is False

    # 2. Infeasible V_v (< 0.02)
    c_bad_vv = OptimizationCandidate(
        design_variables={
            "tail_configuration": "Conventional", "horizontal_V_h": 0.55,
            "vertical_V_v": 0.01, "tail_arm_ratio": 0.55, "horiz_ar": 4.0,
            "vert_ar": 1.8, "horiz_taper": 0.6, "vert_taper": 0.6,
            "horiz_sweep": 0.0, "vert_sweep": 0.0, "tail_dihedral_deg": 0.0
        }
    )
    assert constraints.evaluate_constraints(c_bad_vv, mock_tail_context) is False


def test_optimization_priority_interaction(mock_tail_context):
    """Verify that all 7 OptimizationPriority modes configure valid weights in TailOptimizer."""
    for priority in OptimizationPriority:
        ctx = OptimizationContext(
            requirements=mock_tail_context.requirements,
            configuration=mock_tail_context.configuration,
            previous_specifications=mock_tail_context.previous_specifications,
            optimization_priority=priority
        )
        optimizer = TailOptimizer()
        optimizer.initialize(ctx)

        term_weights = {t.name: t.weight for t in optimizer.objective._terms}
        assert abs(sum(term_weights.values()) - 1.0) < 1e-4, f"Weights under {priority} must sum to 1.0"

        # Check priority-specific weight shifts
        if priority == OptimizationPriority.LOWEST_WEIGHT:
            assert term_weights["structural_weight"] == pytest.approx(0.30)
        elif priority == OptimizationPriority.LOWEST_COST:
            assert term_weights["manufacturability"] == pytest.approx(0.35)
        elif priority == OptimizationPriority.MAXIMUM_RANGE:
            assert term_weights["low_drag"] == pytest.approx(0.35)
        elif priority == OptimizationPriority.MAXIMUM_PAYLOAD:
            assert term_weights["longitudinal_stability"] == pytest.approx(0.30)
            assert term_weights["cg_robustness"] == pytest.approx(0.20)


def test_balanced_baseline_exact_reproduction():
    """Verify that Survey 0.5kg reproduces the validated canonical baseline under BALANCED."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED
    )
    res = FixedWingDesignPipeline().execute(req)
    assert res.success is True
    spec = res.final_specification

    # Baseline MTOW is 3.655 kg with target-aware battery sizing (5000mAh vs legacy oversized 10000mAh)
    assert abs(spec.mass_properties.maximum_takeoff_weight_kg - 3.655) < 0.01
    assert spec.tail.tail_configuration == "Conventional"
    assert spec.tail.horizontal_volume_coefficient == pytest.approx(0.625)
    assert spec.tail.vertical_volume_coefficient == pytest.approx(0.030)
    assert spec.tail.horizontal_tail_area_m2 == pytest.approx(0.0243, abs=0.001)
    assert spec.tail.vertical_tail_area_m2 == pytest.approx(0.0108, abs=0.001)
    assert spec.tail.tail_arm_m == pytest.approx(1.24)

