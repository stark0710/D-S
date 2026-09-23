"""
Unit tests for Drone Mass Properties & Center of Gravity Engineering Framework.
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
from backend.design.drone.mass_properties import (
    ComponentMass,
    MassBreakdownCalculator,
    CenterOfGravityCalculator,
    MomentOfInertiaCalculator,
    BalanceAnalysis,
    MassResult,
    MassValidator,
    MassPropertiesEngine,
)


def test_component_mass_and_cg_calculations():
    """Verify CenterOfGravityCalculator weighted 3D center of gravity spatial moment calculation."""
    components = [
        ComponentMass("Front Mass", "STRUCTURE", 500.0, position_x_mm=200.0, position_y_mm=0.0, position_z_mm=0.0),
        ComponentMass("Rear Mass", "STRUCTURE", 500.0, position_x_mm=-200.0, position_y_mm=0.0, position_z_mm=0.0),
    ]

    cg_calc = CenterOfGravityCalculator()
    cg = cg_calc.calculate_cg(components)

    assert cg.cg_x_mm == 0.0
    assert cg.cg_y_mm == 0.0
    assert cg.cg_z_mm == 0.0

    moi_calc = MomentOfInertiaCalculator()
    moi = moi_calc.calculate_moi(components, cg)

    assert moi.iyy_kg_m2 > 0.0
    assert moi.izz_kg_m2 > 0.0


def test_mass_properties_engine_execution():
    """Verify MassPropertiesEngine aggregates all subsystem results and calculates complete mass properties."""
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
        frame_result, prop_result, elec_result, avionics_result, payload_result, max_mtow_kg=25.0
    )

    assert isinstance(mass_result, MassResult)
    assert mass_result.total_mass_kg > 0
    assert mass_result.empty_mass_kg > 0
    assert mass_result.payload_mass_kg > 0
    assert mass_result.mass_breakdown.structure_mass_g > 0
    assert mass_result.mass_breakdown.electrical_mass_g > 0
    assert mass_result.moment_of_inertia.ixx_kg_m2 > 0
    assert mass_result.moment_of_inertia.iyy_kg_m2 > 0
    assert mass_result.moment_of_inertia.izz_kg_m2 > 0
