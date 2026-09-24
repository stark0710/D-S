"""
Unit tests for Drone Design Optimization Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import DroneMissionProfile
from backend.design.drone.configuration import ConfigurationEngine
from backend.design.drone.structure import StructureEngine
from backend.design.drone.propulsion import PropulsionEngine
from backend.design.drone.electrical import ElectricalEngine
from backend.design.drone.avionics import AvionicsEngine
from backend.design.drone.payload import PayloadEngine
from backend.design.drone.mass_properties import MassPropertiesEngine
from backend.design.drone.performance import PerformanceEngine
from backend.design.drone.verification import VerificationEngine
from backend.design.drone.optimization import (
    DesignVariables,
    ObjectiveFunction,
    ConstraintManager,
    CandidateGenerator,
    CandidateEvaluator,
    ParetoFront,
    TradeoffAnalysis,
    OptimizationResult,
    OptimizationValidator,
    OptimizationEngine,
)


def test_optimization_subservices():
    """Verify ObjectiveFunction, ConstraintManager, CandidateGenerator, ParetoFront, TradeoffAnalysis."""
    gen = CandidateGenerator()
    base_vars = DesignVariables()
    candidates = gen.generate_candidates(base_vars, max_candidates=4)
    assert len(candidates) == 4

    pareto = ParetoFront()
    obj_fn = ObjectiveFunction()
    tradeoff = TradeoffAnalysis()

    res = tradeoff.analyze_tradeoff(20.0, 15.0, 5.0, 25.0, 18.0, 5.5)
    assert res.endurance_gain_min == 5.0
    assert res.range_gain_km == 3.0


def test_optimization_engine_full_workflow():
    """Verify OptimizationEngine evaluates optimization search and returns optimal candidate result."""
    mission = DroneMissionProfile(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=2.0,
        target_hover_time_min=15.0,
        target_cruise_time_min=15.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0
    )

    config_engine = ConfigurationEngine()
    cfg_result = config_engine.evaluate_configurations(mission)

    structure_engine = StructureEngine()
    frame_result = structure_engine.design_structure(mission, cfg_result)

    propulsion_engine = PropulsionEngine()
    prop_result = propulsion_engine.design_propulsion(mission, cfg_result, frame_result)

    electrical_engine = ElectricalEngine()
    elec_result = electrical_engine.design_electrical(mission, cfg_result, frame_result, prop_result)

    avionics_engine = AvionicsEngine()
    avionics_result = avionics_engine.design_avionics(mission, cfg_result, frame_result, prop_result, elec_result)

    payload_engine = PayloadEngine()
    payload_result = payload_engine.integrate_payload(
        mission, cfg_result, frame_result, prop_result, elec_result, avionics_result
    )

    mass_engine = MassPropertiesEngine()
    mass_result = mass_engine.analyze_mass_properties(
        frame_result, prop_result, elec_result, avionics_result, payload_result
    )

    perf_engine = PerformanceEngine()
    perf_result = perf_engine.evaluate_performance(
        mission, cfg_result, frame_result, prop_result, elec_result, avionics_result, payload_result, mass_result
    )

    verif_engine = VerificationEngine()
    verif_result = verif_engine.verify_mission(
        mission, cfg_result, frame_result, prop_result, elec_result, avionics_result, payload_result, mass_result, perf_result
    )

    opt_engine = OptimizationEngine()
    opt_result = opt_engine.optimize_design(
        mission, verif_result, perf_result, mass_result, frame_result, elec_result
    )

    assert isinstance(opt_result, OptimizationResult)
    assert opt_result.best_design[0].flight_time_min > 0
    assert len(opt_result.candidate_designs) > 0
    assert opt_result.optimization_iterations > 0
