"""
Fixed-Wing Construction Configuration Data Model

Purpose:
    Defines the standard construction configurations (C1 to C6) and their structured
    specification models containing applicability, physical material requirements,
    and manufacturing metrics.

Role in Architecture:
    Enables the Construction Configuration Selection Engine and Weight & Mass Properties
    Engine to share a single, structured representation of aircraft construction architecture.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


class ConstructionConfigurationId(str, Enum):
    """
    Authoritative construction configuration identifiers (C1 through C6).
    """
    C1_FOAM_CORE_COMPOSITE = "FOAM_CORE_COMPOSITE"
    C2_BALSA_SKELETON_COMPOSITE = "BALSA_SKELETON_COMPOSITE"
    C3_BALSA_CARBON_SKELETON_FILM = "BALSA_CARBON_SKELETON_FILM"
    C4_FOAM_DEPRON_FILM = "FOAM_DEPRON_FILM"
    C5_FOLDED_FOAM_MONOCOQUE = "FOLDED_FOAM_MONOCOQUE"
    C6_WOOD_SKELETON_FILM = "WOOD_SKELETON_FILM"


class StiffnessLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class DurabilityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class ManufacturingComplexity(str, Enum):
    SIMPLE_HOBBY = "SIMPLE_HOBBY"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED_COMPOSITE = "ADVANCED_COMPOSITE"
    INDUSTRIAL_AEROSPACE = "INDUSTRIAL_AEROSPACE"


@dataclass(slots=True)
class ConstructionConfigurationSpecification:
    """
    Structured data model defining an aircraft construction architecture.
    """
    configuration_id: ConstructionConfigurationId
    name: str
    category: str  # "Professional UAV", "Professional Lightweight", "Hobby/Educational", etc.
    description: str
    
    # Applicability envelopes
    applicable_vehicle_types: List[str]
    applicable_mission_types: List[str]
    recommended_payload_range_kg: Tuple[float, float]
    recommended_wingspan_range_m: Tuple[float, float]
    recommended_speed_range_kmh: Tuple[float, float]
    recommended_range_km: Tuple[float, float]
    recommended_endurance_min: Tuple[float, float]
    
    # Structural & Manufacturing attributes
    structural_stiffness_level: StiffnessLevel
    durability_level: DurabilityLevel
    manufacturing_complexity: ManufacturingComplexity
    repairability: str  # "Field Repairable", "Shop Repairable", "Depot Repairable"
    
    # Materials & components
    material_requirements: List[str]
    required_components: List[str]
    optional_components: List[str] = field(default_factory=list)
    
    # Physical default parameters for weight calculations
    default_spar_type: str = "CF_TUBE_12MM"
    default_skin_material: str = "FABRIC_GLASS_STRUCTURAL"
    default_core_material: Optional[str] = None
    default_rib_material: Optional[str] = None
    default_sheeting_material: Optional[str] = None
    default_covering_material: Optional[str] = None
    default_bulkhead_material: str = "WOOD_AIRCRAFT_PLY"
    default_longerons_material: Optional[str] = "CF_STRIP_10X1"
    
    # Heuristic notes
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "configuration_id": self.configuration_id.value if hasattr(self.configuration_id, "value") else str(self.configuration_id),
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "applicable_vehicle_types": self.applicable_vehicle_types,
            "applicable_mission_types": self.applicable_mission_types,
            "recommended_payload_range_kg": list(self.recommended_payload_range_kg),
            "recommended_wingspan_range_m": list(self.recommended_wingspan_range_m),
            "recommended_speed_range_kmh": list(self.recommended_speed_range_kmh),
            "recommended_range_km": list(self.recommended_range_km),
            "recommended_endurance_min": list(self.recommended_endurance_min),
            "structural_stiffness_level": self.structural_stiffness_level.value if hasattr(self.structural_stiffness_level, "value") else str(self.structural_stiffness_level),
            "durability_level": self.durability_level.value if hasattr(self.durability_level, "value") else str(self.durability_level),
            "manufacturing_complexity": self.manufacturing_complexity.value if hasattr(self.manufacturing_complexity, "value") else str(self.manufacturing_complexity),
            "repairability": self.repairability,
            "material_requirements": self.material_requirements,
            "required_components": self.required_components,
            "optional_components": self.optional_components,
            "notes": self.notes,
        }


class ConstructionCatalog:
    """
    Authoritative catalog of the six fixed-wing construction configurations (C1–C6).
    """

    C1_FOAM_CORE_COMPOSITE = ConstructionConfigurationSpecification(
        configuration_id=ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE,
        name="Foam-Core Composite Shell (C1)",
        category="Professional UAV",
        description=(
            "Hot-wire cut XPS internal foam core wrapped in structural fiberglass and/or carbon fiber composite skin, "
            "supported by pultruded or roll-wrapped carbon spar tubes with local plywood/carbon hardpoints. "
            "High torsional and bending stiffness, smooth aerodynamic surface finish, and weather-proof durability."
        ),
        applicable_vehicle_types=["FIXED_WING", "HYBRID_VTOL"],
        applicable_mission_types=["SURVEY", "MAPPING", "CARGO", "DELIVERY", "SECURITY", "SURVEILLANCE"],
        recommended_payload_range_kg=(0.4, 6.0),
        recommended_wingspan_range_m=(1.5, 4.0),
        recommended_speed_range_kmh=(65.0, 160.0),
        recommended_range_km=(20.0, 150.0),
        recommended_endurance_min=(25.0, 180.0),
        structural_stiffness_level=StiffnessLevel.VERY_HIGH,
        durability_level=DurabilityLevel.VERY_HIGH,
        manufacturing_complexity=ManufacturingComplexity.ADVANCED_COMPOSITE,
        repairability="Shop Repairable (Composite patch & epoxy)",
        material_requirements=[
            "XPS Foam Core (35 kg/m3)",
            "Carbon Fiber Spar Tubes",
            "Fiberglass / Carbon Composite Fabric",
            "Laminating Epoxy Matrix",
            "Aircraft Birch Plywood Hardpoints",
        ],
        required_components=[
            "Main Carbon Spar",
            "XPS Foam Core",
            "Composite Skin",
            "Plywood Firewall / Mount Blocks",
            "Aileron / Flap Linkages",
        ],
        optional_components=[
            "Secondary Carbon Spar",
            "Kevlar Belly Skid Plate",
            "Carbon Spar Joiner Sleeve",
        ],
        default_spar_type="CF_TUBE_12MM",
        default_skin_material="FABRIC_GLASS_STRUCTURAL",
        default_core_material="FOAM_XPS",
        default_rib_material=None,
        default_sheeting_material=None,
        default_covering_material=None,
        default_bulkhead_material="WOOD_AIRCRAFT_PLY",
        default_longerons_material="CF_STRIP_10X1",
        notes="Gold standard for commercial surveying, photogrammetry, and long-range missions."
    )

    C2_BALSA_SKELETON_COMPOSITE = ConstructionConfigurationSpecification(
        configuration_id=ConstructionConfigurationId.C2_BALSA_SKELETON_COMPOSITE,
        name="Balsa Skeleton Composite D-Box (C2)",
        category="Professional Lightweight UAV",
        description=(
            "Internal skeleton formed by CNC/laser-cut balsa ribs and carbon spar tubes, sheeted with 1.0mm balsa wood, "
            "and overlaid with lightweight composite glass/carbon skin. Achieves exceptionally low structural weight "
            "while maintaining excellent aerodynamic contour accuracy and structural rigidity."
        ),
        applicable_vehicle_types=["FIXED_WING"],
        applicable_mission_types=["SURVEY", "MAPPING", "RESEARCH", "INSPECTION"],
        recommended_payload_range_kg=(0.2, 2.5),
        recommended_wingspan_range_m=(1.2, 3.2),
        recommended_speed_range_kmh=(50.0, 120.0),
        recommended_range_km=(15.0, 80.0),
        recommended_endurance_min=(25.0, 120.0),
        structural_stiffness_level=StiffnessLevel.HIGH,
        durability_level=DurabilityLevel.HIGH,
        manufacturing_complexity=ManufacturingComplexity.ADVANCED_COMPOSITE,
        repairability="Shop Repairable",
        material_requirements=[
            "Balsa Rib Stock (130 kg/m3)",
            "1.0mm Balsa Sheet Sheeting",
            "Carbon Fiber Spar Tubes",
            "Light E-Glass / Carbon Fabric (80g)",
            "Epoxy Resin",
        ],
        required_components=[
            "Carbon Main Spar",
            "Balsa Ribs",
            "Balsa 1mm Skin",
            "Composite Skin Over Balsa",
            "Plywood Bulkheads",
        ],
        optional_components=[
            "Secondary Carbon Spar",
            "Balsa Sub-Spars",
            "Leading Edge Carbon Strip",
        ],
        default_spar_type="CF_TUBE_8MM",
        default_skin_material="FABRIC_GLASS_LIGHT",
        default_core_material=None,
        default_rib_material="WOOD_BALSA",
        default_sheeting_material="WOOD_BALSA",
        default_covering_material=None,
        default_bulkhead_material="WOOD_AIRCRAFT_PLY",
        default_longerons_material="CF_STRIP_10X1",
        notes="Optimal balance of minimum empty weight and high aerodynamic efficiency for high-aspect-ratio gliders and light survey UAVs."
    )

    C3_BALSA_CARBON_SKELETON_FILM = ConstructionConfigurationSpecification(
        configuration_id=ConstructionConfigurationId.C3_BALSA_CARBON_SKELETON_FILM,
        name="Balsa-Carbon Skeleton Film (C3)",
        category="Lightweight Professional / Advanced Hobby",
        description=(
            "Lightweight skeleton of balsa ribs and carbon spar, covered with heat-shrink film. "
            "Eliminates composite skin and sheeting weight, providing the highest payload-to-empty-weight fraction "
            "for gentle weather and low-speed endurance flights."
        ),
        applicable_vehicle_types=["FIXED_WING"],
        applicable_mission_types=["SECURITY", "SURVEILLANCE", "RESEARCH", "INSPECTION"],
        recommended_payload_range_kg=(0.1, 1.2),
        recommended_wingspan_range_m=(1.0, 2.5),
        recommended_speed_range_kmh=(40.0, 85.0),
        recommended_range_km=(5.0, 40.0),
        recommended_endurance_min=(20.0, 60.0),
        structural_stiffness_level=StiffnessLevel.MEDIUM,
        durability_level=DurabilityLevel.MEDIUM,
        manufacturing_complexity=ManufacturingComplexity.INTERMEDIATE,
        repairability="Field Repairable (Film iron & CA glue)",
        material_requirements=[
            "Balsa Ribs (100 - 130 kg/m3)",
            "Carbon Tube Spar",
            "Lightweight Heat-Shrink Covering Film (25 g/m2)",
            "CA and Wood Adhesive",
            "Lite-Ply Formers",
        ],
        required_components=[
            "Carbon Main Spar",
            "Balsa Ribs",
            "Heat-Shrink Film Covering",
            "Lite-Ply Formers",
        ],
        optional_components=[
            "Balsa Leading Edge D-Box",
            "Carbon Trailing Edge Strip",
        ],
        default_spar_type="CF_TUBE_8MM",
        default_skin_material=None,
        default_core_material=None,
        default_rib_material="WOOD_BALSA",
        default_sheeting_material=None,
        default_covering_material="FILM_HEAT_SHRINK",
        default_bulkhead_material="WOOD_LITE_PLY",
        default_longerons_material="WOOD_BALSA",
        notes="Very low MTOW, high thermal endurance, easily field-repaired."
    )

    C4_FOAM_DEPRON_FILM = ConstructionConfigurationSpecification(
        configuration_id=ConstructionConfigurationId.C4_FOAM_DEPRON_FILM,
        name="Depron Foam Sheet with Film (C4)",
        category="Hobby / Educational",
        description=(
            "Depron closed-cell foam sheet airframe reinforced with carbon rod spars and covered with tape/film. "
            "Low-cost, rapid-build architecture suited for universities, flight training, and low-cost surveillance."
        ),
        applicable_vehicle_types=["FIXED_WING"],
        applicable_mission_types=["RESEARCH", "INSPECTION", "AGRICULTURE"],
        recommended_payload_range_kg=(0.05, 0.6),
        recommended_wingspan_range_m=(0.8, 1.6),
        recommended_speed_range_kmh=(35.0, 75.0),
        recommended_range_km=(2.0, 20.0),
        recommended_endurance_min=(15.0, 45.0),
        structural_stiffness_level=StiffnessLevel.LOW,
        durability_level=DurabilityLevel.MEDIUM,
        manufacturing_complexity=ManufacturingComplexity.SIMPLE_HOBBY,
        repairability="Field Repairable (Hot glue / tape)",
        material_requirements=[
            "Depron Foam Sheets (3mm / 6mm)",
            "Carbon Fiber Rod 3mm",
            "Covering Film or Reinforced Tape",
            "UHU Por or Foam-Safe CA",
            "Lite-Ply Motor Mount",
        ],
        required_components=[
            "Depron Wing Panels",
            "Carbon Spar Rod",
            "Film/Tape Skin",
            "Foam Box Fuselage",
            "Firewall Plate",
        ],
        optional_components=[
            "Bamboo Skid Skegs",
            "Plywood Control Horns",
        ],
        default_spar_type="CF_ROD_3MM",
        default_skin_material=None,
        default_core_material="FOAM_DEPRON",
        default_rib_material=None,
        default_sheeting_material=None,
        default_covering_material="FILM_HEAT_SHRINK",
        default_bulkhead_material="WOOD_LITE_PLY",
        default_longerons_material=None,
        notes="Ultra low-cost and quick turnaround."
    )

    C5_FOLDED_FOAM_MONOCOQUE = ConstructionConfigurationSpecification(
        configuration_id=ConstructionConfigurationId.C5_FOLDED_FOAM_MONOCOQUE,
        name="Folded Foam Board Monocoque (C5)",
        category="Hobby / Educational Rapid Prototype",
        description=(
            "Paper-faced foam board scored and folded along camber lines to form a semi-monocoque wing and fuselage. "
            "The folded sheet material itself acts as the primary structure with minimal internal reinforcement. "
            "No traditional ribs or full-length composite spars required."
        ),
        applicable_vehicle_types=["FIXED_WING"],
        applicable_mission_types=["RESEARCH", "INSPECTION"],
        recommended_payload_range_kg=(0.05, 0.5),
        recommended_wingspan_range_m=(0.7, 1.4),
        recommended_speed_range_kmh=(30.0, 70.0),
        recommended_range_km=(1.0, 15.0),
        recommended_endurance_min=(10.0, 35.0),
        structural_stiffness_level=StiffnessLevel.LOW,
        durability_level=DurabilityLevel.LOW,
        manufacturing_complexity=ManufacturingComplexity.SIMPLE_HOBBY,
        repairability="Easily Replaced / Disposable",
        material_requirements=[
            "Paper-Faced Foam Board (5mm)",
            "Hot Melt Glue",
            "Packing Tape Hinges",
            "Plywood Motor Mount Plate",
        ],
        required_components=[
            "Folded Foam Board Shell",
            "Folded Fuselage Box",
            "Plywood Firewall",
            "Steel Pushrods",
        ],
        optional_components=[
            "Single Wood / Bamboo Spar",
        ],
        default_spar_type="WOOD_BALSA",
        default_skin_material=None,
        default_core_material="FOAM_BOARD",
        default_rib_material=None,
        default_sheeting_material=None,
        default_covering_material=None,
        default_bulkhead_material="WOOD_LITE_PLY",
        default_longerons_material=None,
        notes="Flite-Test style construction, ideal for classroom education and expendable testbeds."
    )

    C6_WOOD_SKELETON_FILM = ConstructionConfigurationSpecification(
        configuration_id=ConstructionConfigurationId.C6_WOOD_SKELETON_FILM,
        name="Traditional Wood Skeleton Film (C6)",
        category="Traditional RC / Hobby",
        description=(
            "Classic laser-cut balsa ribs with spruce/balsa beam spars, lite-ply fuselage formers and balsa longerons, "
            "covered in heat-shrink polyester film. No composite resins or specialized vacuum equipment required."
        ),
        applicable_vehicle_types=["FIXED_WING"],
        applicable_mission_types=["RESEARCH", "SECURITY"],
        recommended_payload_range_kg=(0.1, 1.5),
        recommended_wingspan_range_m=(1.0, 2.4),
        recommended_speed_range_kmh=(40.0, 90.0),
        recommended_range_km=(3.0, 30.0),
        recommended_endurance_min=(15.0, 50.0),
        structural_stiffness_level=StiffnessLevel.MEDIUM,
        durability_level=DurabilityLevel.MEDIUM,
        manufacturing_complexity=ManufacturingComplexity.INTERMEDIATE,
        repairability="Shop Repairable (Wood splices & patch film)",
        material_requirements=[
            "Balsa Wood (130 kg/m3)",
            "Spruce or Basswood Spar Caps (480 kg/m3)",
            "Lite-Ply / Birch Plywood (350 - 680 kg/m3)",
            "Heat-Shrink Film (25 g/m2)",
            "Aliphatic / PVA / CA Wood Glue",
        ],
        required_components=[
            "Wood Spars",
            "Balsa Ribs",
            "Heat-Shrink Film",
            "Plywood Formers",
            "Balsa Longerons",
        ],
        optional_components=[
            "Balsa Shear Webs",
            "Balsa Nose Cone",
        ],
        default_spar_type="WOOD_SPRUCE",
        default_skin_material=None,
        default_core_material=None,
        default_rib_material="WOOD_BALSA",
        default_sheeting_material=None,
        default_covering_material="FILM_HEAT_SHRINK",
        default_bulkhead_material="WOOD_LITE_PLY",
        default_longerons_material="WOOD_BASSWOOD",
        notes="Traditional aeromodelling craft construction with excellent aesthetic appeal and moderate weight."
    )

    _ALL_CONFIGS = [
        C1_FOAM_CORE_COMPOSITE,
        C2_BALSA_SKELETON_COMPOSITE,
        C3_BALSA_CARBON_SKELETON_FILM,
        C4_FOAM_DEPRON_FILM,
        C5_FOLDED_FOAM_MONOCOQUE,
        C6_WOOD_SKELETON_FILM,
    ]

    @classmethod
    def get_all(cls) -> List[ConstructionConfigurationSpecification]:
        return list(cls._ALL_CONFIGS)

    @classmethod
    def get(cls, config_id: ConstructionConfigurationId | str) -> ConstructionConfigurationSpecification:
        str_id = config_id.value if isinstance(config_id, ConstructionConfigurationId) else str(config_id)
        for cfg in cls._ALL_CONFIGS:
            if cfg.configuration_id.value == str_id or cfg.configuration_id.name == str_id:
                return cfg
        raise KeyError(f"Construction configuration '{config_id}' not found in ConstructionCatalog.")
