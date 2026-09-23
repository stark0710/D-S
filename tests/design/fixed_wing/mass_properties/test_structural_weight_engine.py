"""
Unit Tests for Physical Structural Weight & Mass Properties Engine (C1 to C6).
"""
from unittest.mock import MagicMock
import pytest
from backend.design.fixed_wing.construction.construction_types import (
    ConstructionConfigurationId,
    ConstructionCatalog,
)
from backend.design.fixed_wing.mass_properties.structural_weight_engine import (
    StructuralWeightEngine,
    StructuralMassBreakdown,
)
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail


@pytest.fixture
def test_geometry():
    wing = WingGeometry(
        span_m=2.2,
        area_m2=0.55,
        aspect_ratio=8.8,
        wing_loading_kg_m2=15.0,
        root_chord_m=0.32,
        tip_chord_m=0.18,
        taper_ratio=0.56,
        sweep_angle_deg=0.0,
        dihedral_angle_deg=2.0,
        wing_incidence_deg=1.5,
        mean_aerodynamic_chord_m=0.256,
        quarter_chord_x_m=0.07,
        reference_area_m2=0.55,
    )
    fuse = FuselageGeometry(
        length_m=1.35,
        width_m=0.18,
        height_m=0.16,
        nose_length_m=0.25,
        tail_cone_length_m=0.55,
        cross_section_type="Rectangular",
        wing_attachment_x_m=0.45,
        tail_attachment_x_m=1.25,
        payload_bay_length_m=0.30,
        payload_bay_width_m=0.15,
        payload_bay_height_m=0.12,
        payload_bay_volume_m3=0.0054,
        battery_bay_length_m=0.22,
        battery_bay_width_m=0.10,
        battery_bay_height_m=0.08,
        battery_bay_volume_m3=0.00176,
        avionics_bay_length_m=0.15,
        avionics_bay_width_m=0.10,
        avionics_bay_height_m=0.06,
        total_volume_m3=0.038,
    )
    tail = MagicMock()
    tail.horizontal_tail = MagicMock()
    tail.horizontal_tail.area_m2 = 0.09
    tail.horizontal_tail.span_m = 0.65
    tail.vertical_tail = MagicMock()
    tail.vertical_tail.area_m2 = 0.05
    tail.vertical_tail.height_m = 0.26
    return wing, fuse, tail


class TestStructuralWeightCalculations:
    @pytest.fixture
    def engine(self):
        return StructuralWeightEngine(manufacturing_allowance_pct=0.04)

    def test_c1_foam_core_composite(self, engine, test_geometry):
        """Verify C1 FOAM_CORE_COMPOSITE mass build-up and conservation."""
        wing, fuse, tail = test_geometry
        cfg = ConstructionCatalog.C1_FOAM_CORE_COMPOSITE
        bd = engine.calculate_structural_mass(
            wing_geometry=wing,
            fuselage_geometry=fuse,
            tail_result=tail,
            construction_config=cfg,
        )

        assert isinstance(bd, StructuralMassBreakdown)
        assert bd.wing_structural_mass_kg > 0.0
        assert bd.fuselage_structural_mass_kg > 0.0
        assert bd.tail_structural_mass_kg > 0.0
        assert bd.landing_gear_mass_kg > 0.0
        assert bd.manufacturing_allowance_kg > 0.0

        # Verify mass conservation: total must equal sum of contributors
        expected_total = (
            bd.wing_structural_mass_kg +
            bd.fuselage_structural_mass_kg +
            bd.tail_structural_mass_kg +
            bd.landing_gear_mass_kg +
            bd.controls_mechanism_mass_kg +
            bd.fasteners_mass_kg +
            bd.adhesive_mass_kg +
            bd.paint_finish_mass_kg +
            bd.manufacturing_allowance_kg
        )
        assert bd.estimated_finished_structural_mass_kg == pytest.approx(expected_total, rel=1e-3)

        # C1 wing must contain XPS Foam Core and Carbon Spar
        names = [it.name for it in bd.items]
        assert any("XPS Foam Core" in n for n in names)
        assert any("Main Spar" in n for n in names)
        assert any("Composite Skin Resin" in n for n in names)

    def test_c2_balsa_skeleton_composite(self, engine, test_geometry):
        """Verify C2 BALSA_SKELETON_COMPOSITE separates ribs, sheeting, and glass skin."""
        wing, fuse, tail = test_geometry
        cfg = ConstructionCatalog.C2_BALSA_SKELETON_COMPOSITE
        bd = engine.calculate_structural_mass(
            wing_geometry=wing,
            fuselage_geometry=fuse,
            tail_result=tail,
            construction_config=cfg,
        )

        names = [it.name for it in bd.items]
        assert any("Balsa Ribs" in n for n in names)
        assert any("1.0mm Balsa Sheet" in n for n in names)
        assert any("Light E-Glass Skin" in n for n in names)
        assert any("Main Spar" in n for n in names)
        assert bd.estimated_finished_structural_mass_kg > 0.0

    def test_c3_balsa_carbon_skeleton_film(self, engine, test_geometry):
        """Verify C3 BALSA_CARBON_SKELETON_FILM uses film covering and is lighter than C1/C2."""
        wing, fuse, tail = test_geometry
        cfg1 = ConstructionCatalog.C1_FOAM_CORE_COMPOSITE
        cfg3 = ConstructionCatalog.C3_BALSA_CARBON_SKELETON_FILM

        bd1 = engine.calculate_structural_mass(wing, fuse, tail, construction_config=cfg1)
        bd3 = engine.calculate_structural_mass(wing, fuse, tail, construction_config=cfg3)

        assert bd3.wing_structural_mass_kg < bd1.wing_structural_mass_kg
        assert bd3.estimated_finished_structural_mass_kg < bd1.estimated_finished_structural_mass_kg

        names = [it.name for it in bd3.items]
        assert any("Balsa Ribs" in n for n in names)
        assert any("Covering Film" in n for n in names)

    def test_c4_foam_depron_film(self, engine, test_geometry):
        """Verify C4 FOAM_DEPRON_FILM uses Depron foam panels."""
        wing, fuse, tail = test_geometry
        cfg = ConstructionCatalog.C4_FOAM_DEPRON_FILM
        bd = engine.calculate_structural_mass(wing, fuse, tail, construction_config=cfg)

        names = [it.name for it in bd.items]
        assert any("Depron" in n for n in names)
        assert bd.estimated_finished_structural_mass_kg > 0.0

    def test_c5_folded_foam_monocoque(self, engine, test_geometry):
        """Verify C5 FOLDED_FOAM_MONOCOQUE uses foam board shell without ribs."""
        wing, fuse, tail = test_geometry
        cfg = ConstructionCatalog.C5_FOLDED_FOAM_MONOCOQUE
        bd = engine.calculate_structural_mass(wing, fuse, tail, construction_config=cfg)

        names = [it.name for it in bd.items]
        assert any("Foam Board" in n for n in names)
        # Ensure no ribs were fabricated
        assert not any("Ribs" in n for n in names)
        assert bd.estimated_finished_structural_mass_kg > 0.0

    def test_c6_wood_skeleton_film(self, engine, test_geometry):
        """Verify C6 WOOD_SKELETON_FILM uses spruce spar caps and balsa ribs."""
        wing, fuse, tail = test_geometry
        cfg = ConstructionCatalog.C6_WOOD_SKELETON_FILM
        bd = engine.calculate_structural_mass(wing, fuse, tail, construction_config=cfg)

        names = [it.name for it in bd.items]
        assert any("Balsa Ribs" in n for n in names)
        assert any("Spruce Spar Caps" in n for n in names)
        assert bd.estimated_finished_structural_mass_kg > 0.0

    def test_allowance_and_material_sum_transparency(self, engine, test_geometry):
        """Verify calculated_material_mass + manufacturing_allowance = estimated_finished_mass."""
        wing, fuse, tail = test_geometry
        cfg = ConstructionCatalog.C1_FOAM_CORE_COMPOSITE
        bd = engine.calculate_structural_mass(wing, fuse, tail, construction_config=cfg)

        assert bd.calculated_material_mass_kg + bd.manufacturing_allowance_kg == pytest.approx(
            bd.estimated_finished_structural_mass_kg, rel=1e-4
        )
        assert bd.manufacturing_allowance_kg == pytest.approx(
            bd.calculated_material_mass_kg * 0.04, rel=1e-3
        )
