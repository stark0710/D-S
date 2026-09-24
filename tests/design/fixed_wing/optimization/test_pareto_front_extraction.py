"""
Phase 6B-6 Forensic Test Suite: Fixed-Wing Pareto Front Extraction.

Tests:
1. Single candidate -> front size 1
2. Simple dominance -> dominated candidate excluded
3. Trade-off candidates -> mutual non-dominance preserved
4. Multi-objective dominance -> all 5 dimensions simultaneously
5. Direction correctness -> min MTOW, max endurance, max range, max payload, max efficiency
6. Duplicate candidates -> deduplicated deterministically
7. Floating-point tolerance -> tiny differences below tolerance do not create extra points
8. Infeasible candidate filtering -> infeasible candidates rejected regardless of metrics
9. Zero candidates -> returns valid empty result
10. Baseline preservation -> pareto=False matches Phase 6B-4 exact baseline
11. Real Survey Case -> real Survey 0.5kg with Pareto enabled
12. Real Payload Sensitivity -> trade-offs across archive candidates
13. MTOW constraint -> no candidate exceeding user-specified MTOW limit
14. Verification integrity -> failed verification candidates never appear on front
15. Deterministic ordering -> identical ordering across repeated runs
16. Pareto mathematical self-check -> mutual non-dominance and feasibility proof
"""

import pytest
import copy
from backend.design.common.requirements.requirement_model import (
    RequirementModel,
    MissionType,
    TakeoffType,
    LandingType,
    OperatingEnvironment,
    OptimizationPriority,
)
from backend.design.fixed_wing.optimization.pareto.models import (
    ObjectiveDirection,
    ParetoObjectiveDefinition,
    ParetoObjectiveValue,
    ParetoTolerance,
    ParetoCandidate,
    ParetoFrontResult,
)
from backend.design.fixed_wing.optimization.pareto.dominance import (
    check_dominance,
    is_duplicate,
)
from backend.design.fixed_wing.optimization.pareto.extractor import (
    DEFAULT_OBJECTIVE_DEFINITIONS,
    ParetoFrontExtractor,
    build_candidate_from_result,
    self_check_pareto_front,
)
from backend.design.fixed_wing.pipeline.fixed_wing_pipeline import FixedWingDesignPipeline


def make_synthetic_candidate(
    candidate_id: str,
    mtow: float,
    endurance: float,
    range_km: float,
    payload: float,
    efficiency: float,
    is_feasible: bool = True,
    is_selected: bool = False,
    provenance: str = "Synthetic Test",
) -> ParetoCandidate:
    """Helper to assemble a typed ParetoCandidate with the 5 standard objectives."""
    objs = {
        "mtow": ParetoObjectiveValue("mtow", ObjectiveDirection.MINIMIZE, mtow, "kg"),
        "endurance": ParetoObjectiveValue("endurance", ObjectiveDirection.MAXIMIZE, endurance, "min"),
        "range": ParetoObjectiveValue("range", ObjectiveDirection.MAXIMIZE, range_km, "km"),
        "payload_capability": ParetoObjectiveValue("payload_capability", ObjectiveDirection.MAXIMIZE, payload, "kg"),
        "efficiency": ParetoObjectiveValue("efficiency", ObjectiveDirection.MAXIMIZE, efficiency, "dimensionless"),
    }
    return ParetoCandidate(
        candidate_id=candidate_id,
        is_feasible=is_feasible,
        is_selected_design=is_selected,
        objectives=objs,
        engineering_summary={"mtow_kg": mtow, "endurance_min": endurance},
        technical_specifications={"synthetic": True},
        provenance=provenance,
    )


def test_1_single_candidate():
    """One feasible candidate must produce a front of size 1."""
    cand = make_synthetic_candidate("c1", mtow=3.5, endurance=60.0, range_km=50.0, payload=0.5, efficiency=12.0)
    extractor = ParetoFrontExtractor()
    res = extractor.extract([cand])

    assert res.enabled is True
    assert res.front_size == 1
    assert len(res.front) == 1
    assert res.front[0].candidate_id == "c1"
    assert res.front[0].pareto_rank == 1


def test_2_simple_dominance():
    """Create synthetic candidates where one clearly dominates another. Dominated must be excluded."""
    # A is better in MTOW (lower) and endurance (higher), identical in others
    cand_a = make_synthetic_candidate("A", mtow=3.0, endurance=70.0, range_km=50.0, payload=0.5, efficiency=12.0)
    cand_b = make_synthetic_candidate("B", mtow=4.0, endurance=50.0, range_km=50.0, payload=0.5, efficiency=12.0)

    extractor = ParetoFrontExtractor()
    res = extractor.extract([cand_a, cand_b])

    assert res.candidate_count == 2
    assert res.feasible_candidate_count == 2
    assert res.dominated_candidate_count == 1
    assert res.front_size == 1
    assert res.front[0].candidate_id == "A"
    assert check_dominance(cand_a, cand_b) is True
    assert check_dominance(cand_b, cand_a) is False


def test_3_trade_off_candidates():
    """Candidates with trade-offs (A has lower MTOW, B has higher endurance) must both remain."""
    cand_a = make_synthetic_candidate("A_light", mtow=2.8, endurance=50.0, range_km=45.0, payload=0.5, efficiency=11.5)
    cand_b = make_synthetic_candidate("B_enduring", mtow=3.6, endurance=80.0, range_km=65.0, payload=0.5, efficiency=12.0)

    extractor = ParetoFrontExtractor()
    res = extractor.extract([cand_a, cand_b])

    assert res.front_size == 2
    cand_ids = {c.candidate_id for c in res.front}
    assert cand_ids == {"A_light", "B_enduring"}
    assert check_dominance(cand_a, cand_b) is False
    assert check_dominance(cand_b, cand_a) is False


def test_4_multi_objective_dominance():
    """Verify all five objective directions simultaneously."""
    # Superior in all 5
    best = make_synthetic_candidate("best", mtow=2.5, endurance=90.0, range_km=80.0, payload=1.0, efficiency=15.0)
    # Inferior in all 5
    worst = make_synthetic_candidate("worst", mtow=5.0, endurance=40.0, range_km=30.0, payload=0.3, efficiency=9.0)

    extractor = ParetoFrontExtractor()
    res = extractor.extract([best, worst])

    assert res.front_size == 1
    assert res.front[0].candidate_id == "best"
    assert res.dominated_candidate_count == 1


def test_5_direction_correctness():
    """
    Explicitly test each objective direction individually:
    - MTOW: lower is better
    - Endurance: higher is better
    - Range: higher is better
    - Payload capability: higher is better
    - Efficiency: higher is better
    """
    # Base candidate
    base = make_synthetic_candidate("base", mtow=3.5, endurance=60.0, range_km=50.0, payload=0.5, efficiency=12.0)

    # 1. MTOW: lower MTOW dominates base
    c_mtow_better = make_synthetic_candidate("mtow_better", mtow=3.2, endurance=60.0, range_km=50.0, payload=0.5, efficiency=12.0)
    assert check_dominance(c_mtow_better, base) is True
    assert check_dominance(base, c_mtow_better) is False

    # 2. Endurance: higher endurance dominates base
    c_end_better = make_synthetic_candidate("end_better", mtow=3.5, endurance=75.0, range_km=50.0, payload=0.5, efficiency=12.0)
    assert check_dominance(c_end_better, base) is True
    assert check_dominance(base, c_end_better) is False

    # 3. Range: higher range dominates base
    c_range_better = make_synthetic_candidate("range_better", mtow=3.5, endurance=60.0, range_km=65.0, payload=0.5, efficiency=12.0)
    assert check_dominance(c_range_better, base) is True
    assert check_dominance(base, c_range_better) is False

    # 4. Payload: higher payload dominates base
    c_pay_better = make_synthetic_candidate("pay_better", mtow=3.5, endurance=60.0, range_km=50.0, payload=0.8, efficiency=12.0)
    assert check_dominance(c_pay_better, base) is True
    assert check_dominance(base, c_pay_better) is False

    # 5. Efficiency: higher efficiency dominates base
    c_eff_better = make_synthetic_candidate("eff_better", mtow=3.5, endurance=60.0, range_km=50.0, payload=0.5, efficiency=14.0)
    assert check_dominance(c_eff_better, base) is True
    assert check_dominance(base, c_eff_better) is False


def test_6_duplicate_candidates():
    """Near-identical candidates must deduplicate deterministically."""
    c1 = make_synthetic_candidate("c1", mtow=3.500, endurance=60.0, range_km=50.0, payload=0.5, efficiency=12.0, is_selected=True)
    c2 = make_synthetic_candidate("c2", mtow=3.500, endurance=60.0, range_km=50.0, payload=0.5, efficiency=12.0, is_selected=False)

    extractor = ParetoFrontExtractor()
    res = extractor.extract([c1, c2])

    assert res.candidate_count == 2
    assert res.deduplicated_count == 1
    assert res.front_size == 1
    # Should retain the selected candidate deterministically
    assert res.front[0].candidate_id == "c1"
    assert res.front[0].is_selected_design is True


def test_7_floating_point_tolerance():
    """Tiny numerical differences below tolerance must not create artificial Pareto points."""
    # Tolerances: MTOW 10g (0.01 kg), Endurance 0.1 min, Range 0.1 km, Payload 0.005 kg, Efficiency 0.05
    c_orig = make_synthetic_candidate("orig", mtow=3.500, endurance=60.00, range_km=50.00, payload=0.500, efficiency=12.00)
    c_tiny = make_synthetic_candidate("tiny_diff", mtow=3.502, endurance=59.98, range_km=49.98, payload=0.501, efficiency=12.01)

    extractor = ParetoFrontExtractor()
    res = extractor.extract([c_orig, c_tiny])

    # Within tolerance, should be recognized as duplicate and deduplicated to 1 point
    assert res.front_size == 1
    assert res.deduplicated_count == 1


def test_8_infeasible_candidate_filtering():
    """An infeasible candidate with excellent objective values must NOT enter the Pareto front."""
    # Infeasible dream candidate
    dream = make_synthetic_candidate("dream_infeasible", mtow=1.0, endurance=300.0, range_km=500.0, payload=5.0, efficiency=30.0, is_feasible=False)
    # Modest feasible candidate
    modest = make_synthetic_candidate("modest_feasible", mtow=3.5, endurance=60.0, range_km=50.0, payload=0.5, efficiency=12.0, is_feasible=True)

    extractor = ParetoFrontExtractor()
    res = extractor.extract([dream, modest])

    assert res.candidate_count == 2
    assert res.feasible_candidate_count == 1
    assert res.front_size == 1
    assert res.front[0].candidate_id == "modest_feasible"
    assert res.front[0].is_feasible is True


def test_9_zero_candidates():
    """Return a valid empty Pareto result without crashing."""
    extractor = ParetoFrontExtractor()
    res = extractor.extract([])

    assert res.enabled is True
    assert res.front_size == 0
    assert res.candidate_count == 0
    assert len(res.front) == 0
    assert len(res.warnings) > 0


def test_10_baseline_preservation():
    """Pareto disabled must reproduce Phase 6B-4 exact baseline for Survey 0.5kg."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    res = FixedWingDesignPipeline().execute(req, pareto=False)

    assert res.success is True
    assert res.converged is True
    assert res.pareto_front is None
    spec = res.final_specification
    assert spec is not None
    # Check key baseline parameters
    assert abs(spec.mass_properties.maximum_takeoff_weight_kg - 3.655) < 0.05
    assert abs(spec.performance.endurance_min - 66.5) < 2.0
    assert abs(spec.performance.range_km - 77.6) < 2.0


def test_11_real_survey_case():
    """Run the standard Survey 0.5 kg representative case with Pareto enabled."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req, pareto=True)

    assert res.success is True
    assert res.pareto_front is not None
    pf: ParetoFrontResult = res.pareto_front

    assert pf.enabled is True
    assert pf.candidate_count >= 1
    assert pf.feasible_candidate_count >= 1
    assert pf.front_size >= 1

    # Every returned point must be feasible
    for cand in pf.front:
        assert cand.is_feasible is True
        assert cand.get_value("mtow") > 0.0
        assert cand.get_value("endurance") > 0.0
        assert cand.get_value("range") > 0.0
        assert cand.get_value("payload_capability") > 0.0
        assert cand.get_value("efficiency") > 0.0
        assert "motor" in cand.technical_specifications
        assert "battery" in cand.technical_specifications

    # Self-check mathematical validity
    valid, errors = self_check_pareto_front(pf)
    assert valid is True, f"Pareto self-check failed: {errors}"


def test_12_real_payload_sensitivity():
    """Verify trade-offs across candidates from distinct payload configurations."""
    c_light = make_synthetic_candidate("c_0_5kg", mtow=3.655, endurance=66.5, range_km=77.6, payload=0.5, efficiency=12.5)
    c_heavy = make_synthetic_candidate("c_1_0kg", mtow=4.617, endurance=75.7, range_km=94.6, payload=1.0, efficiency=13.0)

    extractor = ParetoFrontExtractor()
    res = extractor.extract([c_light, c_heavy])

    # c_light has lower MTOW (better); c_heavy has higher payload, endurance, range (better)
    # Neither dominates the other!
    assert res.front_size == 2
    cand_ids = [c.candidate_id for c in res.front]
    assert "c_0_5kg" in cand_ids
    assert "c_1_0kg" in cand_ids


def test_13_mtow_constraint():
    """Verify Pareto extraction never returns a candidate above the user-specified MTOW limit."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        maximum_takeoff_weight_kg=4.0,  # Strict upper limit
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    res = FixedWingDesignPipeline().execute(req, pareto=True)

    assert res.success is True
    assert res.pareto_front is not None
    for cand in res.pareto_front.front:
        assert cand.get_value("mtow") <= 4.0 + 1e-4, f"Candidate {cand.candidate_id} exceeded MTOW limit"


def test_14_verification_integrity():
    """Verify failed verification candidates never appear on the front."""
    # Create candidate with failed verification
    bad_cand = make_synthetic_candidate("failed_verification", mtow=2.0, endurance=100.0, range_km=100.0, payload=1.0, efficiency=18.0, is_feasible=False)
    good_cand = make_synthetic_candidate("passed_verification", mtow=3.5, endurance=60.0, range_km=50.0, payload=0.5, efficiency=12.0, is_feasible=True)

    extractor = ParetoFrontExtractor()
    res = extractor.extract([bad_cand, good_cand])

    assert res.front_size == 1
    assert res.front[0].candidate_id == "passed_verification"


def test_15_deterministic_ordering():
    """Run the same Pareto extraction twice and confirm identical ordering/content."""
    c1 = make_synthetic_candidate("c1", mtow=3.5, endurance=60.0, range_km=50.0, payload=0.5, efficiency=12.0)
    c2 = make_synthetic_candidate("c2", mtow=2.9, endurance=45.0, range_km=40.0, payload=0.5, efficiency=11.0)
    c3 = make_synthetic_candidate("c3", mtow=4.2, endurance=90.0, range_km=80.0, payload=0.5, efficiency=13.0)

    extractor = ParetoFrontExtractor()
    res1 = extractor.extract([c1, c2, c3])
    res2 = extractor.extract([c3, c1, c2])  # Passed in different order

    assert res1.front_size == res2.front_size
    assert [c.candidate_id for c in res1.front] == [c.candidate_id for c in res2.front]
    # Check ordering: MTOW ascending (2.9 -> 3.5 -> 4.2)
    assert [c.candidate_id for c in res1.front] == ["c2", "c1", "c3"]


def test_16_pareto_mathematical_self_check():
    """
    Forensic mathematical check:
    For every pair A, B on the front:
    NOT dominates(A, B) AND NOT dominates(B, A).
    """
    candidates = [
        make_synthetic_candidate("c1", mtow=3.0, endurance=50.0, range_km=40.0, payload=0.5, efficiency=11.0),
        make_synthetic_candidate("c2", mtow=3.5, endurance=70.0, range_km=60.0, payload=0.5, efficiency=12.0),
        make_synthetic_candidate("c3", mtow=4.0, endurance=90.0, range_km=80.0, payload=0.5, efficiency=13.0),
        make_synthetic_candidate("dominated", mtow=4.5, endurance=40.0, range_km=30.0, payload=0.4, efficiency=10.0),
    ]
    extractor = ParetoFrontExtractor()
    res = extractor.extract(candidates)

    valid, errors = self_check_pareto_front(res)
    assert valid is True, f"Errors: {errors}"
    assert res.front_size == 3
    assert all(c.candidate_id != "dominated" for c in res.front)
