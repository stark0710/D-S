"""
VTOL Phase 8 Commercial Hardware Selection — Domain Models and Requirements.

Purpose:
    Typed dataclasses defining hardware requirement envelopes, commercial product
    specifications, verification statuses, compatibility interfaces, and closure metrics
    for the Torq Wings Lift + Cruise (QuadPlane) hybrid VTOL.

Key Architectural Invariants:
    - Downstream of Authoritative Physics (Phases 1-7).
    - Strict provenance tagging for every requirement and manufacturer claim.
    - Explicit UNKNOWN/UNVERIFIED classification for missing specifications — zero fabrication.
    - Explicit ENGINEERING_REEVALUATION_REQUIRED triggers for hardware mass/power deltas.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Dict, List, Optional


class VerificationStatus(str, Enum):
    """Product verification status against engineering requirements."""
    VERIFIED_MATCH = "VERIFIED_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    FAILS_REQUIREMENT = "FAILS_REQUIREMENT"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNVERIFIED = "UNVERIFIED"


class CompatibilityStatus(str, Enum):
    """Subsystem-to-subsystem physical and electrical compatibility."""
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"


class SelectionStatus(str, Enum):
    """System-level commercial hardware selection completeness."""
    HARDWARE_SELECTION_COMPLETE = "HARDWARE_SELECTION_COMPLETE"
    HARDWARE_SELECTION_WITH_WARNINGS = "HARDWARE_SELECTION_WITH_WARNINGS"
    HARDWARE_SELECTION_INCOMPLETE = "HARDWARE_SELECTION_INCOMPLETE"


class ProvenanceCategory(str, Enum):
    """Authoritative parameter provenance classifications."""
    DERIVED = "DERIVED"
    PROJECT_REQUIREMENT = "PROJECT_REQUIREMENT"
    CONFIGURABLE_ASSUMPTION = "CONFIGURABLE_ASSUMPTION"
    ASSUMPTION_BASED = "ASSUMPTION_BASED"
    UNRESOLVED_INPUT = "UNRESOLVED_INPUT"
    DEFERRED = "DEFERRED"
    COMMERCIAL_DATASHEET = "COMMERCIAL_DATASHEET"
    MANUFACTURER_CLAIM = "MANUFACTURER_CLAIM"
    THIRD_PARTY_SOURCE = "THIRD_PARTY_SOURCE"


class HardwareCategory(str, Enum):
    """Subsystem hardware taxonomy for VTOL aircraft."""
    VTOL_MOTOR = "VTOL_MOTOR"
    VTOL_PROPELLER = "VTOL_PROPELLER"
    VTOL_ESC = "VTOL_ESC"
    CRUISE_MOTOR = "CRUISE_MOTOR"
    CRUISE_PROPELLER = "CRUISE_PROPELLER"
    CRUISE_ESC = "CRUISE_ESC"
    BATTERY_PACK = "BATTERY_PACK"
    POWER_DISTRIBUTION = "POWER_DISTRIBUTION"
    SERVO = "SERVO"
    FLIGHT_CONTROLLER = "FLIGHT_CONTROLLER"
    NAVIGATION_GNSS = "NAVIGATION_GNSS"
    AIRSPEED_SENSOR = "AIRSPEED_SENSOR"
    TELEMETRY_LINK = "TELEMETRY_LINK"
    RC_RECEIVER = "RC_RECEIVER"
    COMPANION_COMPUTER = "COMPANION_COMPUTER"
    MISSION_PAYLOAD = "MISSION_PAYLOAD"
    STRUCTURAL_HARDWARE = "STRUCTURAL_HARDWARE"


class PricingStatus(str, Enum):
    """Commercial pricing confidence classification."""
    VERIFIED_PRICE = "VERIFIED_PRICE"
    ESTIMATED_PRICE = "ESTIMATED_PRICE"
    UNKNOWN_PRICE = "UNKNOWN_PRICE"


@dataclass(slots=True)
class HardwareRequirement:
    """
    Authoritative engineering envelope for a specific hardware component or interface.
    """
    requirement_id: str
    category: HardwareCategory
    parameter: str
    minimum_value: Optional[float] = None
    maximum_value: Optional[float] = None
    preferred_value: Optional[float] = None
    units: str = ""
    quantity: int = 1
    source_phase: int = 0
    source_model: str = ""
    provenance: ProvenanceCategory = ProvenanceCategory.DERIVED
    hard_constraint: bool = True
    verification_method: str = "DATASHEET_NUMERICAL_COMPARISON"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "category": self.category.value,
            "parameter": self.parameter,
            "minimum_value": self.minimum_value,
            "maximum_value": self.maximum_value,
            "preferred_value": self.preferred_value,
            "units": self.units,
            "quantity": self.quantity,
            "source_phase": self.source_phase,
            "source_model": self.source_model,
            "provenance": self.provenance.value,
            "hard_constraint": self.hard_constraint,
            "verification_method": self.verification_method,
            "notes": self.notes,
        }


@dataclass(slots=True)
class CommercialProduct:
    """
    Authoritative representation of a real commercial off-the-shelf (COTS) product.
    """
    product_id: str
    manufacturer: str
    product_name: str
    model_number: str
    category: HardwareCategory
    mass_kg: Optional[float]
    specifications: Dict[str, Any]
    dimensions_mm: Dict[str, float] = field(default_factory=dict)
    voltage_min_v: Optional[float] = None
    voltage_max_v: Optional[float] = None
    continuous_power_w: Optional[float] = None
    peak_power_w: Optional[float] = None
    continuous_current_a: Optional[float] = None
    peak_current_a: Optional[float] = None
    thrust_n: Optional[float] = None
    rpm_max: Optional[float] = None
    efficiency_g_w: Optional[float] = None
    interfaces: List[str] = field(default_factory=list)
    compatible_propellers: List[str] = field(default_factory=list)
    operating_temperature_c: Optional[str] = None
    datasheet_reference: str = ""
    source_url: str = ""
    manufacturer_url: str = ""
    verified_date: str = ""
    specification_confidence: str = "MANUFACTURER_DATASHEET_VERIFIED"
    provenance: ProvenanceCategory = ProvenanceCategory.COMMERCIAL_DATASHEET
    price_usd: Optional[float] = None
    pricing_status: PricingStatus = PricingStatus.UNKNOWN_PRICE
    notes: str = ""

    def get_spec(self, key: str, default: Any = None) -> Any:
        """Safe getter for arbitrary product specifications."""
        if key in self.specifications:
            return self.specifications[key]
        if hasattr(self, key):
            return getattr(self, key, default)
        return default

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "manufacturer": self.manufacturer,
            "product_name": self.product_name,
            "model_number": self.model_number,
            "category": self.category.value,
            "mass_kg": round(self.mass_kg, 4) if self.mass_kg is not None else None,
            "specifications": dict(self.specifications),
            "dimensions_mm": dict(self.dimensions_mm),
            "voltage_min_v": self.voltage_min_v,
            "voltage_max_v": self.voltage_max_v,
            "continuous_power_w": self.continuous_power_w,
            "peak_power_w": self.peak_power_w,
            "continuous_current_a": self.continuous_current_a,
            "peak_current_a": self.peak_current_a,
            "thrust_n": self.thrust_n,
            "rpm_max": self.rpm_max,
            "efficiency_g_w": self.efficiency_g_w,
            "interfaces": list(self.interfaces),
            "compatible_propellers": list(self.compatible_propellers),
            "operating_temperature_c": self.operating_temperature_c,
            "datasheet_reference": self.datasheet_reference,
            "source_url": self.source_url,
            "manufacturer_url": self.manufacturer_url,
            "verified_date": self.verified_date,
            "specification_confidence": self.specification_confidence,
            "provenance": self.provenance.value,
            "price_usd": self.price_usd,
            "pricing_status": self.pricing_status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class RequirementVerification:
    """Detailed verification record for a product against a single requirement envelope."""
    requirement_id: str
    parameter: str
    required_min: Optional[float]
    required_max: Optional[float]
    actual_value: Optional[float]
    units: str
    status: VerificationStatus
    margin: Optional[float] = None
    margin_pct: Optional[float] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "parameter": self.parameter,
            "required_min": self.required_min,
            "required_max": self.required_max,
            "actual_value": self.actual_value,
            "units": self.units,
            "status": self.status.value,
            "margin": round(self.margin, 4) if self.margin is not None else None,
            "margin_pct": round(self.margin_pct, 2) if self.margin_pct is not None else None,
            "notes": self.notes,
        }


@dataclass(slots=True)
class ProductVerificationReport:
    """Consolidated verification report for a single commercial product candidate."""
    product: CommercialProduct
    verifications: List[RequirementVerification]
    overall_status: VerificationStatus
    hard_requirements_passed: int
    hard_requirements_failed: int
    missing_data_count: int
    rejection_reasons: List[str] = field(default_factory=list)

    @property
    def is_verified(self) -> bool:
        return self.overall_status == VerificationStatus.VERIFIED_MATCH

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product": self.product.to_dict(),
            "overall_status": self.overall_status.value,
            "hard_requirements_passed": self.hard_requirements_passed,
            "hard_requirements_failed": self.hard_requirements_failed,
            "missing_data_count": self.missing_data_count,
            "rejection_reasons": list(self.rejection_reasons),
            "verifications": [v.to_dict() for v in self.verifications],
        }


@dataclass(slots=True)
class HardwareReevaluationTrigger:
    """
    Formal record generated when commercial hardware deviations necessitate
    an upstream engineering re-evaluation (Phase 5 Mass/CG, Phase 4 Electrical, etc.).
    """
    affected_phase: int
    affected_parameter: str
    engineering_baseline_value: float
    commercial_actual_value: float
    delta_value: float
    units: str
    reason: str
    expected_impact: str
    requires_re_convergence: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "affected_phase": self.affected_phase,
            "affected_parameter": self.affected_parameter,
            "engineering_baseline_value": round(self.engineering_baseline_value, 4),
            "commercial_actual_value": round(self.commercial_actual_value, 4),
            "delta_value": round(self.delta_value, 4),
            "units": self.units,
            "reason": self.reason,
            "expected_impact": self.expected_impact,
            "requires_re_convergence": self.requires_re_convergence,
        }
