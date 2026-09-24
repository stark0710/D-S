"""
Unit Tests for Physical Material and Structural Component Databases.
"""
import pytest
from backend.design.fixed_wing.materials.material_database import (
    PhysicalMaterialDatabase,
    FoamMaterial,
    WoodMaterial,
    CompositeFabric,
    CarbonReinforcement,
    MetalReinforcement,
    AdhesiveFinish,
)
from backend.design.fixed_wing.materials.component_database import (
    StructuralComponentDatabase,
    ServoComponent,
    LinkageHardware,
    WheelComponent,
    StructuralMountItem,
)


class TestPhysicalMaterialDatabase:
    def test_foam_materials(self):
        """Verify foam properties, non-zero densities, and volume/sheet mass equations."""
        for foam_id in ["FOAM_XPS", "FOAM_DEPRON", "FOAM_EPP", "FOAM_EPS", "FOAM_BOARD", "FOAM_PU"]:
            foam = PhysicalMaterialDatabase.get_foam(foam_id)
            assert foam is not None
            assert foam.density_kg_m3 > 0.0
            
            # mass = volume * density
            vol = 0.01  # 0.01 m3
            mass = foam.calculate_mass_kg(vol)
            assert mass == pytest.approx(vol * foam.density_kg_m3, rel=1e-5)
            
            # mass = area * thickness * density
            area = 0.5
            thick = 0.01
            sheet_mass = foam.calculate_sheet_mass_kg(area, thick)
            assert sheet_mass == pytest.approx(area * thick * foam.density_kg_m3, rel=1e-5)

    def test_wood_materials(self):
        """Verify wood densities and physics equations."""
        for wood_id in ["WOOD_BALSA", "WOOD_LITE_PLY", "WOOD_AIRCRAFT_PLY", "WOOD_BIRCH_PLY", "WOOD_POPLAR_PLY", "WOOD_BASSWOOD", "WOOD_SPRUCE"]:
            wood = PhysicalMaterialDatabase.get_wood(wood_id)
            assert wood is not None
            assert wood.density_kg_m3 > 0.0
            
            # Balsa should be lighter than aircraft birch ply
            balsa = PhysicalMaterialDatabase.get_wood("WOOD_BALSA")
            ply = PhysicalMaterialDatabase.get_wood("WOOD_AIRCRAFT_PLY")
            assert balsa.density_kg_m3 < ply.density_kg_m3

            # Volume calculation
            vol = 0.002
            mass = wood.calculate_mass_kg(vol)
            assert mass == pytest.approx(vol * wood.density_kg_m3, rel=1e-5)

    def test_composite_fabrics_and_resin(self):
        """Verify fabric areal density and composite resin calculation."""
        for comp_id in ["FABRIC_GLASS_LIGHT", "FABRIC_GLASS_STRUCTURAL", "FABRIC_CARBON_LIGHT", "FABRIC_CARBON_STRUCTURAL", "FABRIC_KEVLAR"]:
            comp = PhysicalMaterialDatabase.get_composite(comp_id)
            assert comp is not None
            assert comp.areal_density_g_m2 > 0.0
            assert 0.0 < comp.resin_fraction < 1.0

            area = 1.5  # 1.5 m2
            plies = 2
            fib_m, res_m, tot_m = comp.calculate_laminate_mass_kg(area, plies=plies)
            
            # Fiber mass must equal area * plies * (areal_density / 1000)
            expected_fib = area * plies * (comp.areal_density_g_m2 / 1000.0)
            assert fib_m == pytest.approx(expected_fib, rel=1e-5)
            
            # Resin mass must be non-zero and satisfy resin_fraction = resin / (fiber + resin)
            assert res_m > 0.0
            assert res_m / tot_m == pytest.approx(comp.resin_fraction, rel=1e-5)
            assert tot_m == pytest.approx(fib_m + res_m, rel=1e-5)

    def test_carbon_and_metal_stocks(self):
        """Verify rod/tube linear mass and mass conservation across length."""
        for stock_id in ["CF_TUBE_8MM", "CF_TUBE_12MM", "CF_TUBE_16MM", "CF_ROD_3MM", "CF_ROD_5MM", "CF_STRIP_10X1"]:
            stock = PhysicalMaterialDatabase.get_carbon_stock(stock_id)
            assert stock is not None
            lin_mass = stock.get_linear_mass_kg_m()
            assert lin_mass > 0.0
            
            length = 2.5  # 2.5 meters
            mass = stock.calculate_mass_kg(length)
            assert mass == pytest.approx(length * lin_mass, rel=1e-5)

        for metal_id in ["ALU_TUBE_10MM", "ALU_STRIP_15X2", "STEEL_WIRE_2MM"]:
            metal = PhysicalMaterialDatabase.get_metal(metal_id)
            assert metal is not None
            assert metal.get_linear_mass_kg_m() > 0.0

    def test_adhesives_and_films(self):
        """Verify covering film areal density and glues."""
        film = PhysicalMaterialDatabase.get_adhesive("FILM_HEAT_SHRINK")
        assert film.areal_density_g_m2 == 25.0
        assert film.calculate_surface_mass_kg(2.0) == pytest.approx(2.0 * 0.025, rel=1e-5)


class TestStructuralComponentDatabase:
    def test_servo_components(self):
        """Verify servo database masses and classes."""
        micro = StructuralComponentDatabase.get_servo_for_class("micro_9g")
        mini = StructuralComponentDatabase.get_servo_for_class("mini_17g")
        std = StructuralComponentDatabase.get_servo_for_class("standard_45g")

        assert micro.mass_kg < mini.mass_kg < std.mass_kg
        assert micro.mass_kg == pytest.approx(0.012, rel=1e-3)
        assert std.mass_kg == pytest.approx(0.055, rel=1e-3)

    def test_linkages_and_wheels(self):
        """Verify linkage sets, wheels, and mounts."""
        linkages = StructuralComponentDatabase.LINKAGES
        assert "PUSHROD_CARBON_STEEL" in linkages
        assert "CONTROL_HORN_FIBER" in linkages
        assert "CLEVIS_BALL_LINK" in linkages

        for wheel_id, wheel in StructuralComponentDatabase.WHEELS.items():
            assert wheel.mass_kg > 0.0

        for mount_id, mount in StructuralComponentDatabase.MOUNTS_AND_TRAYS.items():
            assert mount.typical_mass_kg > 0.0
