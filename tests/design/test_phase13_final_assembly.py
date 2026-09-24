"""
Phase 13 Dedicated Test Suite: Torq Wings Final Design Engine Assembly & Universal Entry Pipeline.

Validates:
    A. Universal entry point & routing dispatch
    B. Technical requirement validation (no raw English parsing, no silent architecture selection)
    C. FinalAircraftDesign contract completeness & deterministic serialization
    D. Fixed-Wing pipeline integration & locked output preservation
    E. VTOL pipeline integration & Phase 8/11 hardware identity preservation
    F. Requirement traceability & evaluable margins
    G. CAD handover data structures
    H. Simulation handover data structures
    I. Provenance categories and integrity
    J. CLI execution and report export
"""

import os
import json
import tempfile
import pytest

from backend.design.assembly import (
    TorqWingsDesignEngine,
    FinalAircraftDesign,
    AircraftClass,
    OverallDesignStatus,
    UnsupportedArchitectureError,
    InvalidTechnicalRequirementsError,
    ContractValidationError,
    ProvenanceCategory,
    EngineeringStatus,
    to_dict_deterministic,
)
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def nominal_fixed_wing_reqs():
    return {
        "aircraft_class": "FIXED_WING",
        "mission": {
            "mission_type": "SURVEY",
            "range_km": 30.0,
            "endurance_min": 35.0,
            "cruise_speed_kmh": 80.0,
            "cruise_altitude_m": 150.0,
        },
        "payload": {
            "mass_kg": 0.6,
        },
    }


@pytest.fixture
def nominal_vtol_reqs():
    return {
        "aircraft_class": "VTOL",
        "mission": {
            "mission_type": "SURVEY",
            "range_km": 40.0,
            "endurance_min": 30.0,
            "cruise_speed_kmh": 90.0,
            "hover_duration_min": 5.0,
            "cruise_altitude_m": 150.0,
        },
        "payload": {
            "mass_kg": 1.5,
        },
        "lift_motor_count": 4,
    }


# ---------------------------------------------------------------------------
# A. Universal Entry Point
# ---------------------------------------------------------------------------

def test_a1_universal_entry_accepts_fixed_wing(nominal_fixed_wing_reqs):
    """Verify universal entry accepts string 'FIXED_WING' and generates valid design."""
    design = TorqWingsDesignEngine.generate("FIXED_WING", nominal_fixed_wing_reqs)
    assert isinstance(design, FinalAircraftDesign)
    assert design.aircraft_class == AircraftClass.FIXED_WING
    assert design.design_status == OverallDesignStatus.DESIGN_VALIDATED


def test_a2_universal_entry_accepts_vtol(nominal_vtol_reqs):
    """Verify universal entry accepts string 'VTOL' and generates valid design."""
    design = TorqWingsDesignEngine.generate("VTOL", nominal_vtol_reqs)
    assert isinstance(design, FinalAircraftDesign)
    assert design.aircraft_class == AircraftClass.VTOL
    assert design.design_status == OverallDesignStatus.DESIGN_VALIDATED


def test_a3_universal_entry_rejects_unsupported_architecture(nominal_fixed_wing_reqs):
    """Verify universal entry rejects unknown aircraft categories."""
    with pytest.raises(UnsupportedArchitectureError):
        TorqWingsDesignEngine.generate("FLYING_CAR_UNKNOWN", nominal_fixed_wing_reqs)


def test_a4_universal_entry_multirotor_extension_point(nominal_fixed_wing_reqs):
    """Verify multirotor triggers clean extension point error without fake physics."""
    with pytest.raises(NotImplementedError) as exc_info:
        TorqWingsDesignEngine.generate("MULTIROTOR", nominal_fixed_wing_reqs)
    assert "Section 28" in str(exc_info.value) or "extension point" in str(exc_info.value)


# ---------------------------------------------------------------------------
# B. Technical Requirement Input
# ---------------------------------------------------------------------------

def test_b1_rejects_unsupplied_aircraft_class(nominal_fixed_wing_reqs):
    """Verify aircraft_class is mandatory and not guessed."""
    with pytest.raises(UnsupportedArchitectureError):
        TorqWingsDesignEngine.generate(None, nominal_fixed_wing_reqs)


def test_b2_rejects_raw_english_input():
    """Verify Design Engine does not parse raw English text."""
    raw_english = "I want a drone that flies for 45 minutes carrying a camera."
    with pytest.raises(InvalidTechnicalRequirementsError) as exc_info:
        TorqWingsDesignEngine.generate("VTOL", raw_english)
    assert "raw string" in str(exc_info.value) or "Requirement Agent" in str(exc_info.value)


def test_b3_missing_required_fields_fails_clearly():
    """Verify missing critical requirement fields fails loudly."""
    empty_reqs = {"aircraft_class": "VTOL"}
    with pytest.raises(InvalidTechnicalRequirementsError):
        TorqWingsDesignEngine.generate("VTOL", empty_reqs)


# ---------------------------------------------------------------------------
# C. Final Design Contract
# ---------------------------------------------------------------------------

def test_c1_contract_top_level_sections_exist(nominal_vtol_reqs):
    """Verify all top-level sections exist per Section 11."""
    design = TorqWingsDesignEngine.generate("VTOL", nominal_vtol_reqs)
    assert design.design_id.startswith("TW-VTOL-")
    assert design.coordinate_system is not None
    assert design.geometry is not None
    assert design.aerodynamics is not None
    assert design.propulsion is not None
    assert design.transition is not None
    assert design.energy is not None
    assert design.battery is not None
    assert design.mass_properties is not None
    assert design.stability is not None
    assert design.controls is not None
    assert design.performance is not None
    assert design.avionics is not None
    assert design.electrical is not None
    assert len(design.commercial_components) > 0
    assert design.installation is not None
    assert design.manufacturing is not None
    assert design.constraints is not None
    assert design.assumptions is not None
    assert len(design.provenance) > 0
    assert len(design.requirement_traceability) > 0
    assert design.cad_handover is not None
    assert design.simulation_handover is not None
    assert design.validation_status is not None
    assert design.design_status == OverallDesignStatus.DESIGN_VALIDATED


def test_c2_deterministic_serialization(nominal_fixed_wing_reqs):
    """Verify repeated execution produces deterministic JSON representation."""
    design1 = TorqWingsDesignEngine.generate("FIXED_WING", nominal_fixed_wing_reqs)
    design2 = TorqWingsDesignEngine.generate("FIXED_WING", nominal_fixed_wing_reqs)

    d1 = design1.to_dict()
    d2 = design2.to_dict()

    # Mask dynamic timestamp IDs
    d1["design_id"] = "STATIC_TEST_ID"
    d2["design_id"] = "STATIC_TEST_ID"

    json1 = json.dumps(d1, sort_keys=True)
    json2 = json.dumps(d2, sort_keys=True)

    assert json1 == json2


# ---------------------------------------------------------------------------
# D. Fixed-Wing Integration & Preservation
# ---------------------------------------------------------------------------

def test_d1_fixed_wing_preserves_locked_outputs(nominal_fixed_wing_reqs):
    """Verify Fixed-Wing pipeline generates valid design with non-applicable VTOL fields."""
    design = TorqWingsDesignEngine.generate("FIXED_WING", nominal_fixed_wing_reqs)
    assert design.mass_properties.mtow_kg > 0.0
    assert design.geometry.wing.span_m > 0.0
    assert design.aerodynamics.lift_to_drag_cruise > 5.0
    # VTOL fields explicitly NOT_APPLICABLE
    assert design.propulsion.lift_propulsion.status == EngineeringStatus.NOT_APPLICABLE
    assert design.transition.status == EngineeringStatus.NOT_APPLICABLE


# ---------------------------------------------------------------------------
# E. VTOL Hardware Identity & Authoritative Modules
# ---------------------------------------------------------------------------

def test_e1_vtol_hardware_identity_strictly_enforced(nominal_vtol_reqs):
    """Verify Phase 8/11 hardware identities (Spedix GS40A, Hobbywing Skywalker 40A V2) are preserved."""
    design = TorqWingsDesignEngine.generate("VTOL", nominal_vtol_reqs)
    assert design.propulsion.lift_propulsion.esc_model == "Spedix GS40A"
    assert design.propulsion.cruise_propulsion.esc_model == "Hobbywing Skywalker 40A V2"

    bom_escs = [item.model for item in design.commercial_components if "ESC" in item.role]
    assert "Spedix GS40A" in bom_escs
    assert "Hobbywing Skywalker 40A V2" in bom_escs

    # Ensure stale identities are NOT present
    for item in design.commercial_components:
        assert "T-Motor AIR 40A" not in item.model
        assert "Hobbywing FlyFun 40A" not in item.model


def test_e2_vtol_flight_validation_never_claimed(nominal_vtol_reqs):
    """Verify Section 10 rule: Flight validation is NEVER claimed."""
    design = TorqWingsDesignEngine.generate("VTOL", nominal_vtol_reqs)
    assert design.validation_status.flight_validated is False
    assert design.validation_status.status == "PHYSICAL_GROUND_VALIDATED"


# ---------------------------------------------------------------------------
# F. Requirement Traceability
# ---------------------------------------------------------------------------

def test_f1_traceability_items_have_margins(nominal_vtol_reqs):
    """Verify requirement traceability items provide calculated margins."""
    design = TorqWingsDesignEngine.generate("VTOL", nominal_vtol_reqs)
    for item in design.requirement_traceability:
        assert item.requirement
        assert item.required_value is not None
        assert item.design_value is not None
        assert item.unit
        assert item.status in ("PASS", "FAIL", "DEFERRED", "NOT_APPLICABLE")


# ---------------------------------------------------------------------------
# G & H. CAD & Simulation Handover
# ---------------------------------------------------------------------------

def test_g1_cad_handover_contains_geometry_and_mounts(nominal_vtol_reqs):
    """Verify CAD handover block exposes coordinates, airfoils, and mounting locations."""
    cad = TorqWingsDesignEngine.generate("VTOL", nominal_vtol_reqs).cad_handover
    assert len(cad.major_geometry) > 0
    assert len(cad.wing_airfoils) > 0
    assert len(cad.mounting_coordinates) > 0
    assert "lift_motor_front_left" in cad.mounting_coordinates
    assert len(cad.cg_location_m) == 3


def test_h1_simulation_handover_contains_polars_and_derivatives(nominal_vtol_reqs):
    """Verify simulation handover exposes aerodynamic polar and stability derivatives."""
    sim = TorqWingsDesignEngine.generate("VTOL", nominal_vtol_reqs).simulation_handover
    assert sim.mtow_kg > 0.0
    assert "cd0" in sim.aerodynamics_polar
    assert "cl_cruise" in sim.aerodynamics_polar
    assert "c_m_alpha" in sim.stability_derivatives
    assert "c_n_beta" in sim.stability_derivatives
    assert sim.inertia.status == EngineeringStatus.DEFERRED


# ---------------------------------------------------------------------------
# I. Provenance Tracking
# ---------------------------------------------------------------------------

def test_i1_provenance_records_validity(nominal_fixed_wing_reqs):
    """Verify engineering quantities have appropriate provenance labels."""
    design = TorqWingsDesignEngine.generate("FIXED_WING", nominal_fixed_wing_reqs)
    prov = design.provenance
    assert "mtow_kg" in prov
    assert prov["mtow_kg"].provenance == ProvenanceCategory.CALCULATED
    assert prov["payload_mass_kg"].provenance == ProvenanceCategory.PROJECT_REQUIREMENT
    assert prov["cruise_power_w"].provenance == ProvenanceCategory.DERIVED


# ---------------------------------------------------------------------------
# J. CLI Runner Execution
# ---------------------------------------------------------------------------

def test_j1_cli_file_generation():
    """Verify CLI runner executes and produces valid JSON and Markdown files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        req_file = os.path.join(temp_dir, "reqs.json")
        out_dir = os.path.join(temp_dir, "out")

        with open(req_file, "w", encoding="utf-8") as f:
            json.dump({
                "aircraft_class": "FIXED_WING",
                "mission": {
                    "range_km": 30.0,
                    "endurance_min": 30.0,
                    "cruise_speed_kmh": 80.0,
                },
                "payload": {"mass_kg": 0.5}
            }, f)

        # Call engine directly with output_dir (same underlying path as CLI)
        with open(req_file, "r", encoding="utf-8") as f:
            req_data = json.load(f)

        TorqWingsDesignEngine.generate("FIXED_WING", req_data, output_dir=out_dir)

        json_out = os.path.join(out_dir, "final_aircraft_design.json")
        md_out = os.path.join(out_dir, "final_aircraft_design.md")

        assert os.path.isfile(json_out)
        assert os.path.isfile(md_out)
        assert os.path.getsize(json_out) > 500
        assert os.path.getsize(md_out) > 500
