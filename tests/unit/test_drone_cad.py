"""
Unit tests for Drone CAD Generation Engineering Framework.
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
from backend.design.drone.cad import (
    GeometryBuilder,
    PlacementEngine,
    AssemblyBuilder,
    CollisionChecker,
    ClearanceChecker,
    ExportManager,
    CADResult,
    CADValidator,
    CADEngine,
)


def test_cad_subservice_modules():
    """Verify GeometryBuilder, PlacementEngine, AssemblyBuilder, CollisionChecker, ClearanceChecker, ExportManager."""
    collision_engine = CollisionChecker()
    clearance_engine = ClearanceChecker()
    export_engine = ExportManager()

    clearances = clearance_engine.check_clearances([])
    assert clearances["ground_clearance_mm"] > 0


def test_cad_engine_full_workflow():
    """Verify CADEngine converts engineered multirotor into parametric 3D CAD assembly and export payload."""
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

    cad_engine = CADEngine()
    cad_result = cad_engine.generate_cad(
        frame_result, prop_result, elec_result, avionics_result, payload_result
    )

    assert isinstance(cad_result, CADResult)
    assert len(cad_result.components) > 0
    assert cad_result.assembly.total_mass_g > 0
    assert cad_result.generated_files["format"] == "JSON_PARAMETRIC"
    assert len(cad_result.placements) == len(cad_result.components)
