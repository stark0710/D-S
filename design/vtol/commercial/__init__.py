"""
VTOL Phase 8 Commercial Hardware Selection, Verification & BOM Mapping Subsystem.

Provides:
    - Product models, hardware requirement envelopes, and verification reports
    - Curated commercial hardware catalog with authentic manufacturer datasheets
    - Numerical product verifier and missing data handler
    - System-level 14-pair interface compatibility matrix
    - Authoritative requirement extractor consuming Phases 1-7
    - Mass closure, electrical power closure, and re-evaluation triggers
    - Commercial Bill of Materials (BOM) synthesis
    - HardwareMatcher top-level orchestrator
"""

from .product_models import (
    VerificationStatus,
    CompatibilityStatus,
    SelectionStatus,
    ProvenanceCategory,
    HardwareCategory,
    PricingStatus,
    HardwareRequirement,
    CommercialProduct,
    RequirementVerification,
    ProductVerificationReport,
    HardwareReevaluationTrigger,
)

from .product_catalog import (
    ProductCatalog,
    CATALOG,
)

from .product_verifier import (
    ProductVerifier,
)

from .compatibility import (
    InterfaceCompatibilityRecord,
    HardwareCompatibilityMatrix,
    SystemCompatibilityChecker,
)

from .requirement_extractor import (
    HardwareRequirementExtractor,
)

from .closure_engine import (
    MassClosureResult,
    PowerClosureResult,
    MassClosureEngine,
    PowerClosureEngine,
)

from .bom import (
    BillOfMaterialsItem,
    CommercialBillOfMaterials,
)

from .hardware_matcher import (
    TraceabilityEntry,
    HardwareSelectionResult,
    HardwareMatcher,
)

__all__ = [
    "VerificationStatus",
    "CompatibilityStatus",
    "SelectionStatus",
    "ProvenanceCategory",
    "HardwareCategory",
    "PricingStatus",
    "HardwareRequirement",
    "CommercialProduct",
    "RequirementVerification",
    "ProductVerificationReport",
    "HardwareReevaluationTrigger",
    "ProductCatalog",
    "CATALOG",
    "ProductVerifier",
    "InterfaceCompatibilityRecord",
    "HardwareCompatibilityMatrix",
    "SystemCompatibilityChecker",
    "HardwareRequirementExtractor",
    "MassClosureResult",
    "PowerClosureResult",
    "MassClosureEngine",
    "PowerClosureEngine",
    "BillOfMaterialsItem",
    "CommercialBillOfMaterials",
    "TraceabilityEntry",
    "HardwareSelectionResult",
    "HardwareMatcher",
]
