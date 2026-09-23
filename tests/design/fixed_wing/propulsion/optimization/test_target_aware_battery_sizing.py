"""
Unit and Integration Tests for Phase 6B-3: Target-Aware Battery Sizing
Torq Wings Fixed-Wing Sizing Engine
"""

import pytest
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.fixed_wing.propulsion.optimization.constraints import (
    check_mission_energy_sufficiency,
    build_propulsion_constraints,
)
from backend.design.fixed_wing.propulsion.optimization.objective_function import (
    PropulsionObjectiveFunction,
)
from backend.design.fixed_wing.propulsion.optimization.candidate_generator import (
    GridSearchPropulsionCandidateGenerator,
)
from backend.design.fixed_wing.propulsion.optimization.candidate_evaluator import (
    CandidateEvaluator,
)
from backend.design.fixed_wing.propulsion.optimization.propulsion_optimizer import (
    PropulsionOptimizer,
)


def test_battery_sensitivity_matrix():
    """Verify that battery capacity and MTOW scale with increasing mission target endurance."""
    pipeline = FixedWingDesignPipeline()
    targets = [20.0, 30.0, 45.0, 60.0, 80.0]
    results = []

    for t in targets:
        req = RequirementModel(
            mission_type=MissionType.SURVEY,
            payload_weight_kg=0.5,
            target_flight_time_min=t,
            target_range_km=30.0,
            cruise_speed_kmh=70.0,
            takeoff_type=TakeoffType.RUNWAY,
            landing_type=LandingType.RUNWAY,
            environment=OperatingEnvironment.RURAL,
            optimization_priority=OptimizationPriority.BALANCED,
        )
        res = pipeline.execute(req)
        assert res.success is True, f"Pipeline execution failed for target {t} min"
        spec = res.final_specification
        cap = spec.propulsion.battery_capacity_mah
        mass = spec.propulsion.battery_weight_g
        endurance = spec.performance.endurance_min
        mtow = spec.mass_properties.maximum_takeoff_weight_kg

        # Sizing requirement: achieved endurance must satisfy target endurance
        assert endurance >= t, f"Achieved endurance {endurance} min is below target {t} min"

        results.append({
            "target": t,
            "capacity": cap,
            "mass": mass,
            "endurance": endurance,
            "mtow": mtow,
        })

    # Verify that battery capacity is NOT identical across dramatically different targets
    capacities = [r["capacity"] for r in results]
    assert len(set(capacities)) >= 3, f"Expected distinct battery capacities, got {capacities}"

    # Verify battery capacity and MTOW monotonically increase or stay constant with target
    for i in range(len(results) - 1):
        assert results[i]["capacity"] <= results[i + 1]["capacity"], (
            f"Capacity decreased from {results[i]['capacity']} to {results[i+1]['capacity']}"
        )
        assert results[i]["mtow"] <= results[i + 1]["mtow"], (
            f"MTOW decreased from {results[i]['mtow']} to {results[i+1]['mtow']}"
        )


def test_oversizing_rejection():
    """Verify that a 45-minute mission rejects excessive 10000mAh oversizing in favor of sufficient capacity."""
    pipeline = FixedWingDesignPipeline()
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
    res = pipeline.execute(req)
    assert res.success is True
    spec = res.final_specification

    # Sized battery for 45 min must not be the 10000mAh pack
    cap = spec.propulsion.battery_capacity_mah
    assert cap < 10000.0, f"Expected target-sized battery (<10000mAh), got {cap} mAh"
    assert cap >= 3300.0, f"Battery capacity too small: {cap} mAh"
    # Sized endurance must satisfy the 45 min target with sensible reserve
    assert spec.performance.endurance_min >= 45.0
    assert spec.performance.endurance_min < 90.0, f"Excessive endurance: {spec.performance.endurance_min} min"


def test_hard_constraint_mission_energy_sufficiency():
    """Verify that check_mission_energy_sufficiency rejects candidates failing target endurance."""
    cand = OptimizationCandidate(
        design_variables={
            "motor": {"name": "Test", "max_current_a": 30.0, "cell_count_s": 6},
            "esc": {"name": "ESC", "continuous_current_a": 40.0},
            "battery": {"name": "Batt", "cell_count_s": 6, "capacity_mah": 2200.0, "nominal_voltage_v": 22.2, "max_discharge_current_a": 60.0},
            "propeller": {"diameter_m": 0.25},
        },
        derived_variables={
            "estimated_flight_time_min": 25.0,
            "climb_current_a": 20.0,
            "cruise_power_w": 100.0,
            "takeoff_thrust_n": 10.0,
            "static_thrust_n": 15.0,
            "cruise_thrust_n": 5.0,
            "climb_power_w": 200.0,
        },
        status="EVALUATED",
    )

    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    context = OptimizationContext(requirements=req)

    # Flight time 25.0 min < Target 45.0 min -> must fail constraint
    passed, reason = check_mission_energy_sufficiency(cand, context)
    assert passed is False
    assert "below controlling mission requirement" in reason

    # Update flight time to 50.0 min -> must pass constraint
    cand.derived_variables["estimated_flight_time_min"] = 50.0
    passed, reason = check_mission_energy_sufficiency(cand, context)
    assert passed is True
    assert reason == ""


def test_impossible_endurance_rejection():
    """Verify that an impossible mission requirement (e.g. 500 min endurance) is rejected."""
    pipeline = FixedWingDesignPipeline()
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=500.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
    )
    res = pipeline.execute(req)
    # The pipeline must fail because no battery candidate satisfies 500 min endurance
    assert res.success is False, "Pipeline unexpectedly passed with impossible 500 min target"


def test_priority_sensitivity_battery_selection():
    """Verify that LOWEST_WEIGHT selects a lower-mass battery than BALANCED."""
    pipeline = FixedWingDesignPipeline()
    req_base = RequirementModel(
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
    res_balanced = pipeline.execute(req_base)
    assert res_balanced.success is True

    req_weight = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.LOWEST_WEIGHT,
    )
    res_weight = pipeline.execute(req_weight)
    assert res_weight.success is True

    # LOWEST_WEIGHT battery mass must be less than or equal to BALANCED
    m_bal = res_balanced.final_specification.propulsion.battery_weight_g
    m_wt = res_weight.final_specification.propulsion.battery_weight_g
    assert m_wt <= m_bal, f"LOWEST_WEIGHT battery ({m_wt} g) heavier than BALANCED ({m_bal} g)"
    # MTOW under LOWEST_WEIGHT should be lower
    mtow_bal = res_balanced.final_specification.mass_properties.maximum_takeoff_weight_kg
    mtow_wt = res_weight.final_specification.mass_properties.maximum_takeoff_weight_kg
    assert mtow_wt < mtow_bal, f"LOWEST_WEIGHT MTOW ({mtow_wt} kg) not lower than BALANCED ({mtow_bal} kg)"


def test_battery_technical_specification_output():
    """Verify that PropulsionSpecification exposes manufacturer-independent engineering requirements."""
    pipeline = FixedWingDesignPipeline()
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
    res = pipeline.execute(req)
    assert res.success is True
    spec = res.final_specification.propulsion

    # 1. Direct fields
    assert spec.battery_chemistry in ["LiPo", "Li-Ion", "LiHV"]
    assert spec.battery_energy_wh > 0.0
    assert spec.required_energy_wh > 0.0
    assert spec.battery_c_rating > 0.0
    assert spec.required_c_rating > 0.0
    assert spec.target_endurance_min == pytest.approx(45.0)
    assert spec.target_range_km == pytest.approx(30.0)
    assert spec.energy_margin_pct >= 0.0

    # 2. Manufacturer-independent technical specification dictionary
    tech = spec.battery_technical_spec
    assert isinstance(tech, dict)
    assert "chemistry" in tech
    assert "cells" in tech
    assert "capacity" in tech
    assert "energy" in tech
    assert "discharge" in tech
    assert "mass" in tech
    assert "compatibility" in tech

    assert tech["cells"]["series"] == spec.cell_count_s
    assert tech["cells"]["nominal_voltage_v"] == spec.operating_voltage_v
    assert tech["capacity"]["selected_mah"] == spec.battery_capacity_mah
    assert tech["capacity"]["minimum_required_mah"] > 0.0
    assert tech["energy"]["usable_wh"] > 0.0
    assert tech["discharge"]["continuous_current_a"] > 0.0
    assert tech["compatibility"]["motor_voltage_compatible"] is True
    assert tech["compatibility"]["esc_voltage_compatible"] is True
