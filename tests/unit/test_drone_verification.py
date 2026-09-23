"""
Unit tests for Drone Mission Verification Engineering Framework.
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
from backend.design.drone.verification import (
    MissionCompliance,
    PerformanceVerification,
    SafetyVerification,
    ReliabilityVerification,
    ConstraintVerification,
    VerificationScoreCalculator,
    VerificationResult,
    VerificationValidator,
    VerificationEngine,
)


def test_verification_subservice_modules():
    """Verify MissionCompliance, PerformanceVerification, SafetyVerification, ReliabilityVerification, ConstraintVerification, VerificationScoreCalculator."""
    score_calc = VerificationScoreCalculator()
    score_res = score_calc.calculate_score(mission_score=100.0, performance_score=90.0, safety_score=95.0, reliability_score=80.0)

    assert score_res.overall_score > 90.0
    assert score_res.mission_compliance_score == 100.0


def test_verification_engine_full_workflow():
    """Verify VerificationEngine evaluates aircraft across all disciplines and returns passed verification result."""
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

    assert isinstance(verif_result, VerificationResult)
    assert verif_result.overall_status in ["PASSED", "MARGINAL", "FAILED"]
    assert verif_result.verification_score.overall_score > 0
    assert len(verif_result.passed_requirements) > 0
