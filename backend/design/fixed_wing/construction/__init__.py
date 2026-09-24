"""
Fixed-Wing Construction Architecture Module
"""

from backend.design.fixed_wing.construction.construction_types import (
    ConstructionConfigurationId,
    StiffnessLevel,
    DurabilityLevel,
    ManufacturingComplexity,
    ConstructionConfigurationSpecification,
    ConstructionCatalog,
)
from backend.design.fixed_wing.construction.construction_engine import (
    ConstructionSelectionResult,
    ConstructionConfigurationSelectionEngine,
)

__all__ = [
    "ConstructionConfigurationId",
    "StiffnessLevel",
    "DurabilityLevel",
    "ManufacturingComplexity",
    "ConstructionConfigurationSpecification",
    "ConstructionCatalog",
    "ConstructionSelectionResult",
    "ConstructionConfigurationSelectionEngine",
]
