"""
Fixed-Wing Materials and Structural Components Module
"""

from backend.design.fixed_wing.materials.material_database import (
    MaterialType,
    FoamMaterial,
    WoodMaterial,
    CompositeFabric,
    CarbonReinforcement,
    MetalReinforcement,
    AdhesiveFinish,
    PhysicalMaterialDatabase,
)
from backend.design.fixed_wing.materials.component_database import (
    ServoComponent,
    LinkageHardware,
    WheelComponent,
    StructuralMountItem,
    StructuralComponentDatabase,
)

__all__ = [
    "MaterialType",
    "FoamMaterial",
    "WoodMaterial",
    "CompositeFabric",
    "CarbonReinforcement",
    "MetalReinforcement",
    "AdhesiveFinish",
    "PhysicalMaterialDatabase",
    "ServoComponent",
    "LinkageHardware",
    "WheelComponent",
    "StructuralMountItem",
    "StructuralComponentDatabase",
]
