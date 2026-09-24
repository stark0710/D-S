"""
Provenance Subsystem for Phase 13 Final Design Assembly.

Defines provenance categories, provenance item models, and helpers to ensure
complete engineering traceability without mislabeling assumptions or calculations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Dict


class ProvenanceCategory(str, Enum):
    """Supported provenance categories per Section 15 of Phase 13 specification."""
    PROJECT_REQUIREMENT = "PROJECT_REQUIREMENT"
    CALCULATED = "CALCULATED"
    DERIVED = "DERIVED"
    CONFIGURABLE_ASSUMPTION = "CONFIGURABLE_ASSUMPTION"
    COMMERCIAL_VERIFIED = "COMMERCIAL_VERIFIED"
    PHYSICAL_GROUND_MEASUREMENT = "PHYSICAL_GROUND_MEASUREMENT"
    PHYSICAL_BENCH_MEASUREMENT = "PHYSICAL_BENCH_MEASUREMENT"
    DEFERRED = "DEFERRED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class EngineeringStatus(str, Enum):
    """Status flags for engineering values and sections."""
    VALID = "VALID"
    DEFERRED = "DEFERRED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class ProvenanceRecord:
    """Represents a traceable provenance record for an engineering field or value."""
    field_name: str
    value: Any
    unit: str
    provenance: ProvenanceCategory
    source_module: str
    status: EngineeringStatus = EngineeringStatus.VALID
    reason: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_name": self.field_name,
            "value": self.value,
            "unit": self.unit,
            "provenance": self.provenance.value if isinstance(self.provenance, Enum) else str(self.provenance),
            "source_module": self.source_module,
            "status": self.status.value if isinstance(self.status, Enum) else str(self.status),
            "reason": self.reason,
            "notes": self.notes,
        }
