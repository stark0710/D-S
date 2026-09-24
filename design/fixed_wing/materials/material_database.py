"""
Fixed-Wing Physical Material Database Subsystem

Purpose:
    Defines physical materials (foams, woods, composite fabrics, carbon reinforcements,
    metals, adhesives, and finishes) with true physical properties (density in kg/m³,
    areal density in g/m², thicknesses, linear mass, and notes).

Role in Architecture:
    Provides authoritative, centralized physical material data for the Physical Weight &
    Mass Properties Engine and Construction Selection Engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class MaterialType(Enum):
    FOAM = "FOAM"
    WOOD = "WOOD"
    COMPOSITE_FABRIC = "COMPOSITE_FABRIC"
    CARBON_REINFORCEMENT = "CARBON_REINFORCEMENT"
    METAL_REINFORCEMENT = "METAL_REINFORCEMENT"
    ADHESIVE_FINISH = "ADHESIVE_FINISH"


@dataclass(slots=True)
class FoamMaterial:
    """
    Physical foam material definition.
    
    Mass calculation:
        mass = volume_m3 * density_kg_m3
        or mass = area_m2 * thickness_m * density_kg_m3
    """
    material_id: str
    name: str
    density_kg_m3: float
    available_thicknesses_mm: List[float]
    sheet_dimensions_mm: Tuple[float, float]
    cost_per_m2_usd: float
    notes: str = ""

    def calculate_mass_kg(self, volume_m3: float) -> float:
        return volume_m3 * self.density_kg_m3

    def calculate_sheet_mass_kg(self, area_m2: float, thickness_m: float) -> float:
        return area_m2 * thickness_m * self.density_kg_m3


@dataclass(slots=True)
class WoodMaterial:
    """
    Physical wood and plywood material definition.
    
    Mass calculation:
        mass = volume_m3 * density_kg_m3
        or mass = area_m2 * thickness_m * density_kg_m3
    """
    material_id: str
    name: str
    density_kg_m3: float
    available_thicknesses_mm: List[float]
    sheet_dimensions_mm: Tuple[float, float]
    cost_per_m2_usd: float
    notes: str = ""

    def calculate_mass_kg(self, volume_m3: float) -> float:
        return volume_m3 * self.density_kg_m3

    def calculate_sheet_mass_kg(self, area_m2: float, thickness_m: float) -> float:
        return area_m2 * thickness_m * self.density_kg_m3


@dataclass(slots=True)
class CompositeFabric:
    """
    Dry composite fabric plus configured resin matrix definition.
    
    Mass calculation:
        fiber_mass_kg = area_m2 * (areal_density_g_m2 / 1000.0) * plies
        resin_mass_kg = fiber_mass_kg * (resin_fraction / (1.0 - resin_fraction))
        total_mass_kg = fiber_mass_kg + resin_mass_kg
    """
    material_id: str
    name: str
    areal_density_g_m2: float  # dry fiber areal weight
    nominal_thickness_mm: float
    fiber_type: str  # "Carbon", "Glass", "Kevlar"
    resin_fraction: float = 0.50  # 50% resin by weight in standard wet/vacuum layup
    cost_per_m2_usd: float = 25.0
    notes: str = ""

    def calculate_laminate_mass_kg(self, area_m2: float, plies: int = 1, resin_fraction_override: Optional[float] = None) -> Tuple[float, float, float]:
        """
        Calculates (fiber_mass_kg, resin_mass_kg, total_laminate_mass_kg).
        """
        r_frac = resin_fraction_override if resin_fraction_override is not None else self.resin_fraction
        fiber_mass = area_m2 * (self.areal_density_g_m2 / 1000.0) * plies
        if r_frac >= 1.0 or r_frac <= 0.0:
            resin_mass = fiber_mass * 0.50
        else:
            resin_mass = fiber_mass * (r_frac / (1.0 - r_frac))
        return fiber_mass, resin_mass, fiber_mass + resin_mass


@dataclass(slots=True)
class CarbonReinforcement:
    """
    Pultruded or rolled carbon fiber tube, rod, strip, or plate.
    
    Mass calculation:
        linear_mass_g_m / 1000.0 * length_m
        or cross_section_m2 * length_m * density_kg_m3
    """
    material_id: str
    name: str
    shape: str  # "rod", "tube", "square_tube", "rectangular_tube", "strip", "plate"
    outer_dim_mm: Tuple[float, ...]  # (diameter,) or (width, height) or (width, thickness)
    inner_dim_mm: Optional[Tuple[float, ...]] = None  # (inner_diameter,) or (inner_w, inner_h)
    linear_mass_g_m: Optional[float] = None
    density_kg_m3: float = 1600.0
    cost_per_m_usd: float = 15.0
    notes: str = ""

    def get_linear_mass_kg_m(self) -> float:
        if self.linear_mass_g_m is not None and self.linear_mass_g_m > 0:
            return self.linear_mass_g_m / 1000.0
        
        # Calculate cross-sectional area in m2
        import math
        if self.shape in ("rod", "tube"):
            od = self.outer_dim_mm[0] / 1000.0
            id_val = (self.inner_dim_mm[0] / 1000.0) if (self.inner_dim_mm and len(self.inner_dim_mm) > 0) else 0.0
            area = (math.pi / 4.0) * (od**2 - id_val**2)
        elif self.shape in ("square_tube", "rectangular_tube"):
            w = self.outer_dim_mm[0] / 1000.0
            h = self.outer_dim_mm[1] / 1000.0 if len(self.outer_dim_mm) > 1 else w
            iw = (self.inner_dim_mm[0] / 1000.0) if (self.inner_dim_mm and len(self.inner_dim_mm) > 0) else 0.0
            ih = (self.inner_dim_mm[1] / 1000.0) if (self.inner_dim_mm and len(self.inner_dim_mm) > 1) else iw
            area = (w * h) - (iw * ih)
        else:  # strip or plate
            w = self.outer_dim_mm[0] / 1000.0
            t = self.outer_dim_mm[1] / 1000.0 if len(self.outer_dim_mm) > 1 else 0.001
            area = w * t
        
        return area * self.density_kg_m3

    def calculate_mass_kg(self, length_m: float) -> float:
        return self.get_linear_mass_kg_m() * length_m


@dataclass(slots=True)
class MetalReinforcement:
    """
    Metal structural reinforcement (aluminum tubes, steel landing wire, etc.).
    """
    material_id: str
    name: str
    metal_type: str  # "Aluminum 6061-T6", "Steel"
    density_kg_m3: float
    outer_dim_mm: Tuple[float, ...]
    inner_dim_mm: Optional[Tuple[float, ...]] = None
    linear_mass_g_m: Optional[float] = None
    notes: str = ""

    def get_linear_mass_kg_m(self) -> float:
        if self.linear_mass_g_m is not None and self.linear_mass_g_m > 0:
            return self.linear_mass_g_m / 1000.0
        import math
        od = self.outer_dim_mm[0] / 1000.0
        id_val = (self.inner_dim_mm[0] / 1000.0) if (self.inner_dim_mm and len(self.inner_dim_mm) > 0) else 0.0
        area = (math.pi / 4.0) * (od**2 - id_val**2)
        return area * self.density_kg_m3

    def calculate_mass_kg(self, length_m: float) -> float:
        return self.get_linear_mass_kg_m() * length_m


@dataclass(slots=True)
class AdhesiveFinish:
    """
    Adhesives, films, paints, and surface finishes.
    """
    material_id: str
    name: str
    category: str  # "film", "adhesive", "paint", "tape"
    areal_density_g_m2: Optional[float] = None
    density_kg_m3: Optional[float] = None
    typical_allowance_pct: float = 0.03  # percentage of structural mass
    notes: str = ""

    def calculate_surface_mass_kg(self, area_m2: float) -> float:
        """Calculate mass of film or paint covering a given surface area."""
        if self.areal_density_g_m2 is not None:
            return area_m2 * (self.areal_density_g_m2 / 1000.0)
        return 0.0


class PhysicalMaterialDatabase:
    """
    Authoritative repository of verified physical materials for aerospace and UAV construction.
    All properties are physical constants or catalog manufacturer ratings.
    """

    FOAMS: Dict[str, FoamMaterial] = {
        "FOAM_XPS": FoamMaterial(
            material_id="FOAM_XPS",
            name="Extruded Polystyrene (XPS)",
            density_kg_m3=35.0,  # Standard blue/pink insulation XPS core
            available_thicknesses_mm=[20.0, 30.0, 50.0, 75.0],
            sheet_dimensions_mm=(1200.0, 600.0),
            cost_per_m2_usd=12.0,
            notes="Ideal high-compressive-strength hot-wire cut core for composite skin wings."
        ),
        "FOAM_DEPRON": FoamMaterial(
            material_id="FOAM_DEPRON",
            name="Depron Aero Closed-Cell Polystyrene Sheet",
            density_kg_m3=33.0,
            available_thicknesses_mm=[2.0, 3.0, 6.0],
            sheet_dimensions_mm=(1000.0, 700.0),
            cost_per_m2_usd=8.0,
            notes="Lightweight extruded foam sheet for rapid prototyping and shock flyers."
        ),
        "FOAM_EPP": FoamMaterial(
            material_id="FOAM_EPP",
            name="Expanded Polypropylene (EPP)",
            density_kg_m3=30.0,
            available_thicknesses_mm=[20.0, 30.0, 50.0],
            sheet_dimensions_mm=(900.0, 600.0),
            cost_per_m2_usd=18.0,
            notes="Extremely durable, impact-resilient, shape-memory foam for tactical and trainer UAVs."
        ),
        "FOAM_EPS": FoamMaterial(
            material_id="FOAM_EPS",
            name="Expanded Polystyrene (EPS)",
            density_kg_m3=20.0,
            available_thicknesses_mm=[25.0, 50.0, 100.0],
            sheet_dimensions_mm=(1000.0, 500.0),
            cost_per_m2_usd=6.0,
            notes="Ultra-lightweight white beadboard core, low cost, requires epoxy (melts with solvent/CA)."
        ),
        "FOAM_BOARD": FoamMaterial(
            material_id="FOAM_BOARD",
            name="Paper-Faced Foam Board (Flite Test style)",
            density_kg_m3=75.0,  # includes dual paper facing
            available_thicknesses_mm=[5.0],
            sheet_dimensions_mm=(762.0, 508.0),
            cost_per_m2_usd=5.0,
            notes="Paper-faced polystyrene board for folded monocoque construction."
        ),
        "FOAM_PU": FoamMaterial(
            material_id="FOAM_PU",
            name="Polyurethane Rigid Structural Foam",
            density_kg_m3=40.0,
            available_thicknesses_mm=[25.0, 50.0],
            sheet_dimensions_mm=(1000.0, 500.0),
            cost_per_m2_usd=22.0,
            notes="Solvent resistant, easy to sand and machine."
        ),
    }

    WOODS: Dict[str, WoodMaterial] = {
        "WOOD_BALSA": WoodMaterial(
            material_id="WOOD_BALSA",
            name="Aero Grade Balsa Wood (Medium Density)",
            density_kg_m3=130.0,  # standard medium contest grade balsa (8 lb/cu.ft)
            available_thicknesses_mm=[1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 10.0],
            sheet_dimensions_mm=(915.0, 100.0),
            cost_per_m2_usd=30.0,
            notes="High strength-to-weight natural cellular wood for ribs, sheeting, and spars."
        ),
        "WOOD_BALSA_LIGHT": WoodMaterial(
            material_id="WOOD_BALSA_LIGHT",
            name="Contest Grade Light Balsa Wood",
            density_kg_m3=100.0,  # light contest balsa (6 lb/cu.ft)
            available_thicknesses_mm=[1.0, 1.5, 2.0, 3.0],
            sheet_dimensions_mm=(915.0, 100.0),
            cost_per_m2_usd=40.0,
            notes="Ultra-light balsa for non-structural ribs and light covering supports."
        ),
        "WOOD_LITE_PLY": WoodMaterial(
            material_id="WOOD_LITE_PLY",
            name="Lite-Plywood (Poplar Core)",
            density_kg_m3=350.0,
            available_thicknesses_mm=[2.0, 3.0, 4.0, 5.0],
            sheet_dimensions_mm=(1200.0, 300.0),
            cost_per_m2_usd=22.0,
            notes="Low-density multi-ply wood for non-firewall bulkheads and formers."
        ),
        "WOOD_AIRCRAFT_PLY": WoodMaterial(
            material_id="WOOD_AIRCRAFT_PLY",
            name="Aircraft Grade Birch Plywood (Aeroply)",
            density_kg_m3=680.0,  # dense, 5-ply to 12-ply Finnish birch
            available_thicknesses_mm=[0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0],
            sheet_dimensions_mm=(1220.0, 610.0),
            cost_per_m2_usd=65.0,
            notes="High structural strength for firewalls, wing spar joiners, and landing gear mounts."
        ),
        "WOOD_BIRCH_PLY": WoodMaterial(
            material_id="WOOD_BIRCH_PLY",
            name="Finnish Birch Aviation Plywood",
            density_kg_m3=680.0,
            available_thicknesses_mm=[1.0, 1.5, 2.0, 3.0, 4.0, 6.0],
            sheet_dimensions_mm=(1220.0, 610.0),
            cost_per_m2_usd=65.0,
            notes="Standard aircraft birch plywood for high shear bulkheads and landing gear hardpoints."
        ),
        "WOOD_POPLAR_PLY": WoodMaterial(
            material_id="WOOD_POPLAR_PLY",
            name="Poplar Lite-Plywood",
            density_kg_m3=350.0,
            available_thicknesses_mm=[2.0, 3.0, 4.0, 5.0],
            sheet_dimensions_mm=(1200.0, 300.0),
            cost_per_m2_usd=22.0,
            notes="Low-density multi-ply poplar sheet for fuselage formers."
        ),
        "WOOD_BASSWOOD": WoodMaterial(
            material_id="WOOD_BASSWOOD",
            name="Basswood Structural Spar Stock",
            density_kg_m3=420.0,
            available_thicknesses_mm=[3.0, 5.0, 6.0, 8.0],
            sheet_dimensions_mm=(915.0, 100.0),
            cost_per_m2_usd=35.0,
            notes="Consistent grain and higher splinter resistance than balsa for heavy-duty spars."
        ),
        "WOOD_SPRUCE": WoodMaterial(
            material_id="WOOD_SPRUCE",
            name="Sitka Spruce Spar Stock",
            density_kg_m3=480.0,
            available_thicknesses_mm=[3.0, 5.0, 6.0, 10.0],
            sheet_dimensions_mm=(1000.0, 20.0),
            cost_per_m2_usd=45.0,
            notes="Aviation-standard spar material with high modulus of elasticity."
        ),
    }

    COMPOSITES: Dict[str, CompositeFabric] = {
        "FABRIC_GLASS_LIGHT": CompositeFabric(
            material_id="FABRIC_GLASS_LIGHT",
            name="Light E-Glass Plain Weave Fabric 80g",
            areal_density_g_m2=80.0,
            nominal_thickness_mm=0.08,
            fiber_type="Glass",
            resin_fraction=0.50,
            cost_per_m2_usd=8.0,
            notes="Surface finishing and ding-resistance skin over balsa or foam."
        ),
        "FABRIC_GLASS_STRUCTURAL": CompositeFabric(
            material_id="FABRIC_GLASS_STRUCTURAL",
            name="Structural E-Glass Twill Fabric 160g",
            areal_density_g_m2=160.0,
            nominal_thickness_mm=0.15,
            fiber_type="Glass",
            resin_fraction=0.50,
            cost_per_m2_usd=12.0,
            notes="Primary fuselage and wing structural skin."
        ),
        "FABRIC_CARBON_LIGHT": CompositeFabric(
            material_id="FABRIC_CARBON_LIGHT",
            name="Aero Carbon Fiber Plain Weave 120g",
            areal_density_g_m2=120.0,
            nominal_thickness_mm=0.12,
            fiber_type="Carbon",
            resin_fraction=0.48,
            cost_per_m2_usd=35.0,
            notes="High-modulus, ultra-light composite skin for professional UAV wings."
        ),
        "FABRIC_CARBON_STRUCTURAL": CompositeFabric(
            material_id="FABRIC_CARBON_STRUCTURAL",
            name="Structural Carbon Fiber 2x2 Twill 200g",
            areal_density_g_m2=200.0,
            nominal_thickness_mm=0.20,
            fiber_type="Carbon",
            resin_fraction=0.48,
            cost_per_m2_usd=48.0,
            notes="High torsional stiffness and bending strength for fuselage monocoques and wing spars."
        ),
        "FABRIC_KEVLAR": CompositeFabric(
            material_id="FABRIC_KEVLAR",
            name="Aramid / Kevlar 29 Fabric 110g",
            areal_density_g_m2=110.0,
            nominal_thickness_mm=0.14,
            fiber_type="Kevlar",
            resin_fraction=0.52,
            cost_per_m2_usd=42.0,
            notes="Impact and abrasion resistant belly skid and nose reinforcements."
        ),
    }

    CARBON_STOCK: Dict[str, CarbonReinforcement] = {
        "CF_ROD_3MM": CarbonReinforcement(
            material_id="CF_ROD_3MM",
            name="Pultruded Carbon Fiber Solid Rod 3mm",
            shape="rod",
            outer_dim_mm=(3.0,),
            linear_mass_g_m=11.3,
            notes="Trailing edge, elevator joiner, and foam wing leading edge reinforcement."
        ),
        "CF_ROD_5MM": CarbonReinforcement(
            material_id="CF_ROD_5MM",
            name="Pultruded Carbon Fiber Solid Rod 5mm",
            shape="rod",
            outer_dim_mm=(5.0,),
            linear_mass_g_m=31.4,
            notes="Leading edge or tail spar rod."
        ),
        "CF_TUBE_8MM": CarbonReinforcement(
            material_id="CF_TUBE_8MM",
            name="Roll-Wrapped Carbon Fiber Tube 8x6mm",
            shape="tube",
            outer_dim_mm=(8.0,),
            inner_dim_mm=(6.0,),
            linear_mass_g_m=35.2,
            notes="Primary main spar for 1.2m-1.8m wingspan or tail boom."
        ),
        "CF_TUBE_12MM": CarbonReinforcement(
            material_id="CF_TUBE_12MM",
            name="Roll-Wrapped Carbon Fiber Tube 12x10mm",
            shape="tube",
            outer_dim_mm=(12.0,),
            inner_dim_mm=(10.0,),
            linear_mass_g_m=55.3,
            notes="Heavy main spar for 1.8m-2.8m wingspan survey UAVs."
        ),
        "CF_TUBE_16MM": CarbonReinforcement(
            material_id="CF_TUBE_16MM",
            name="Heavy Carbon Fiber Tube 16x14mm",
            shape="tube",
            outer_dim_mm=(16.0,),
            inner_dim_mm=(14.0,),
            linear_mass_g_m=75.4,
            notes="Central spar / wing joiner for large professional UAVs."
        ),
        "CF_STRIP_10X1": CarbonReinforcement(
            material_id="CF_STRIP_10X1",
            name="Pultruded Carbon Fiber Spar Cap Strip 10x1mm",
            shape="strip",
            outer_dim_mm=(10.0, 1.0),
            linear_mass_g_m=16.0,
            notes="Upper and lower spar caps for balsa-web I-beam spars."
        ),
        "CF_PLATE_2MM": CarbonReinforcement(
            material_id="CF_PLATE_2MM",
            name="Solid Carbon Fiber Plate 2.0mm",
            shape="plate",
            outer_dim_mm=(100.0, 2.0),
            density_kg_m3=1600.0,
            notes="CNC-cut motor mounts, control horns, and landing gear hardpoints."
        ),
    }

    METALS: Dict[str, MetalReinforcement] = {
        "ALU_TUBE_10MM": MetalReinforcement(
            material_id="ALU_TUBE_10MM",
            name="Aluminum 6061-T6 Tube 10x8mm",
            metal_type="Aluminum 6061-T6",
            density_kg_m3=2700.0,
            outer_dim_mm=(10.0,),
            inner_dim_mm=(8.0,),
            linear_mass_g_m=76.3,
            notes="Wing joiner sleeve or lightweight strut."
        ),
        "ALUM_TUBE_12MM": MetalReinforcement(
            material_id="ALUM_TUBE_12MM",
            name="Aluminum 6061-T6 Spar Sleeve / Joiner 12x10mm",
            metal_type="Aluminum 6061-T6",
            density_kg_m3=2700.0,
            outer_dim_mm=(12.0,),
            inner_dim_mm=(10.0,),
            linear_mass_g_m=93.3,
            notes="Fuselage-through wing joiner sleeve."
        ),
        "ALU_STRIP_15X2": MetalReinforcement(
            material_id="ALU_STRIP_15X2",
            name="Aluminum 6061 Flat Strip 15x2mm",
            metal_type="Aluminum 6061-T6",
            density_kg_m3=2700.0,
            outer_dim_mm=(15.0, 2.0),
            linear_mass_g_m=81.0,
            notes="Mounting bracket or stiffener strip."
        ),
        "STEEL_WIRE_2MM": MetalReinforcement(
            material_id="STEEL_WIRE_2MM",
            name="Spring Tempered Steel Wire 2.0mm",
            metal_type="Steel",
            density_kg_m3=7850.0,
            outer_dim_mm=(2.0,),
            linear_mass_g_m=24.7,
            notes="Light landing gear and pushrods."
        ),
        "STEEL_WIRE_3MM": MetalReinforcement(
            material_id="STEEL_WIRE_3MM",
            name="Spring Tempered Steel Landing Gear Wire 3.0mm",
            metal_type="Steel",
            density_kg_m3=7850.0,
            outer_dim_mm=(3.0,),
            linear_mass_g_m=55.5,
            notes="Bent wire main gear and nose wheel strut."
        ),
        "STEEL_WIRE_4MM": MetalReinforcement(
            material_id="STEEL_WIRE_4MM",
            name="Heavy Spring Steel Landing Gear Wire 4.0mm",
            metal_type="Steel",
            density_kg_m3=7850.0,
            outer_dim_mm=(4.0,),
            linear_mass_g_m=98.6,
            notes="Heavy runway landing gear for 6-12 kg MTOW fixed-wing aircraft."
        ),
    }

    ADHESIVES_AND_FINISHES: Dict[str, AdhesiveFinish] = {
        "FILM_HEAT_SHRINK": AdhesiveFinish(
            material_id="FILM_HEAT_SHRINK",
            name="Lightweight Heat-Shrink Polyester Covering Film (e.g. Oracover / Monokote)",
            category="film",
            areal_density_g_m2=25.0,  # ~25 g/m2 typical for lightweight model aircraft film
            notes="Standard heat-shrink film covering for open rib/skeleton wing structures."
        ),
        "PAINT_POLYURETHANE": AdhesiveFinish(
            material_id="PAINT_POLYURETHANE",
            name="Standard 2K Polyurethane Spray Primer & Topcoat",
            category="paint",
            areal_density_g_m2=25.0,  # ~25 g/m2 for single solid coat
            notes="Aero-grade exterior UV, moisture, and fuel resistant paint."
        ),
        "ADHESIVE_EPOXY": AdhesiveFinish(
            material_id="ADHESIVE_EPOXY",
            name="Structural Laminating & Thixotropic Epoxy System",
            category="adhesive",
            density_kg_m3=1150.0,
            typical_allowance_pct=0.035,
            notes="High-strength room-temperature epoxy for structural joins, spar bonding, and glassing."
        ),
        "ADHESIVE_CA": AdhesiveFinish(
            material_id="ADHESIVE_CA",
            name="Cyanoacrylate (CA) Rapid Adhesive",
            category="adhesive",
            density_kg_m3=1050.0,
            typical_allowance_pct=0.015,
            notes="Fast assembly of balsa ribs and lightweight joints."
        ),
        "ADHESIVE_PU": AdhesiveFinish(
            material_id="ADHESIVE_PU",
            name="Polyurethane Expanding Wood/Foam Glue (Gorilla style)",
            category="adhesive",
            density_kg_m3=1100.0,
            typical_allowance_pct=0.020,
            notes="Gap-filling solvent-free glue for foam-to-wood bonding."
        ),
    }

    @classmethod
    def get_foam(cls, material_id: str) -> FoamMaterial:
        if material_id not in cls.FOAMS:
            raise KeyError(f"Foam '{material_id}' not found in PhysicalMaterialDatabase.")
        return cls.FOAMS[material_id]

    @classmethod
    def get_wood(cls, material_id: str) -> WoodMaterial:
        if material_id not in cls.WOODS:
            raise KeyError(f"Wood '{material_id}' not found in PhysicalMaterialDatabase.")
        return cls.WOODS[material_id]

    @classmethod
    def get_composite(cls, material_id: str) -> CompositeFabric:
        if material_id not in cls.COMPOSITES:
            raise KeyError(f"Composite '{material_id}' not found in PhysicalMaterialDatabase.")
        return cls.COMPOSITES[material_id]

    @classmethod
    def get_carbon_stock(cls, material_id: str) -> CarbonReinforcement:
        if material_id not in cls.CARBON_STOCK:
            raise KeyError(f"Carbon stock '{material_id}' not found in PhysicalMaterialDatabase.")
        return cls.CARBON_STOCK[material_id]

    @classmethod
    def get_metal(cls, material_id: str) -> MetalReinforcement:
        if material_id not in cls.METALS:
            raise KeyError(f"Metal '{material_id}' not found in PhysicalMaterialDatabase.")
        return cls.METALS[material_id]

    @classmethod
    def get_adhesive(cls, material_id: str) -> AdhesiveFinish:
        if material_id not in cls.ADHESIVES_AND_FINISHES:
            raise KeyError(f"Adhesive/Finish '{material_id}' not found in PhysicalMaterialDatabase.")
        return cls.ADHESIVES_AND_FINISHES[material_id]
