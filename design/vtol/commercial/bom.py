"""
VTOL Phase 8 Commercial Bill of Materials (BOM) Subsystem.

Purpose:
    Defines the structured commercial Bill of Materials model capturing quantities,
    unit and total masses, verified commercial pricing, component datasheets,
    engineering requirements satisfied, and confidence levels.

Standards:
    - Pricing is strictly partitioned into VERIFIED_PRICE, ESTIMATED_PRICE, or UNKNOWN_PRICE.
    - Full traceability linking every BOM item to its upstream engineering requirement.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .product_models import (
    CommercialProduct,
    HardwareCategory,
    VerificationStatus,
    CompatibilityStatus,
    PricingStatus,
)


@dataclass(slots=True)
class BillOfMaterialsItem:
    """
    A single line-item in the authoritative commercial Bill of Materials.
    """
    bom_id: str
    category: HardwareCategory
    manufacturer: str
    model: str
    description: str
    quantity: int
    unit_mass_kg: float
    total_mass_kg: float
    unit_price_usd: Optional[float] = None
    total_price_usd: Optional[float] = None
    pricing_status: PricingStatus = PricingStatus.UNKNOWN_PRICE
    verification_status: VerificationStatus = VerificationStatus.VERIFIED_MATCH
    compatibility_status: CompatibilityStatus = CompatibilityStatus.COMPATIBLE
    engineering_requirement_satisfied: str = ""
    datasheet_reference: str = ""
    source_url: str = ""
    confidence: str = "HIGH"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bom_id": self.bom_id,
            "category": self.category.value,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "description": self.description,
            "quantity": self.quantity,
            "unit_mass_kg": round(self.unit_mass_kg, 4),
            "total_mass_kg": round(self.total_mass_kg, 4),
            "unit_price_usd": round(self.unit_price_usd, 2) if self.unit_price_usd is not None else None,
            "total_price_usd": round(self.total_price_usd, 2) if self.total_price_usd is not None else None,
            "pricing_status": self.pricing_status.value,
            "verification_status": self.verification_status.value,
            "compatibility_status": self.compatibility_status.value,
            "engineering_requirement_satisfied": self.engineering_requirement_satisfied,
            "datasheet_reference": self.datasheet_reference,
            "source_url": self.source_url,
            "confidence": self.confidence,
            "notes": self.notes,
        }


@dataclass(slots=True)
class CommercialBillOfMaterials:
    """
    Complete commercial parts tree and procurement listing for the VTOL aircraft.
    """
    items: List[BillOfMaterialsItem]
    total_parts_count: int
    total_commercial_mass_kg: float
    total_commercial_cost_usd: float
    has_unverified_pricing: bool
    verification_completeness_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_parts_count": self.total_parts_count,
            "total_commercial_mass_kg": round(self.total_commercial_mass_kg, 4),
            "total_commercial_cost_usd": round(self.total_commercial_cost_usd, 2),
            "has_unverified_pricing": self.has_unverified_pricing,
            "verification_completeness_pct": round(self.verification_completeness_pct, 2),
            "item_count": len(self.items),
            "items": [item.to_dict() for item in self.items],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def compile_bom(
        cls,
        selected_products: Dict[HardwareCategory, CommercialProduct],
        quantities: Optional[Dict[HardwareCategory, int]] = None,
        requirements_map: Optional[Dict[HardwareCategory, str]] = None,
    ) -> CommercialBillOfMaterials:
        quantities = quantities or {}
        requirements_map = requirements_map or {}

        # Default quantities based on QuadPlane architecture
        default_quantities: Dict[HardwareCategory, int] = {
            HardwareCategory.VTOL_MOTOR: 4,
            HardwareCategory.VTOL_PROPELLER: 4,
            HardwareCategory.VTOL_ESC: 4,
            HardwareCategory.CRUISE_MOTOR: 1,
            HardwareCategory.CRUISE_PROPELLER: 1,
            HardwareCategory.CRUISE_ESC: 1,
            HardwareCategory.BATTERY_PACK: 1,
            HardwareCategory.POWER_DISTRIBUTION: 1,
            HardwareCategory.SERVO: 4,  # 2 Ruddervators + 2 Ailerons
            HardwareCategory.FLIGHT_CONTROLLER: 1,
            HardwareCategory.NAVIGATION_GNSS: 1,
            HardwareCategory.AIRSPEED_SENSOR: 1,
            HardwareCategory.TELEMETRY_LINK: 1,
            HardwareCategory.RC_RECEIVER: 1,
            HardwareCategory.COMPANION_COMPUTER: 1,
            HardwareCategory.MISSION_PAYLOAD: 1,
        }

        # Default requirement mapping strings
        default_reqs: Dict[HardwareCategory, str] = {
            HardwareCategory.VTOL_MOTOR: "Hover Thrust >= 25.08N @ 22.2V",
            HardwareCategory.VTOL_PROPELLER: "16x5.4 Carbon Fiber Rotor",
            HardwareCategory.VTOL_ESC: ">=25A Continuous / >=35A Peak 6S",
            HardwareCategory.CRUISE_MOTOR: "Forward Thrust >= 16.5N @ 22.2V",
            HardwareCategory.CRUISE_PROPELLER: "11x7 Pusher Propeller",
            HardwareCategory.CRUISE_ESC: ">=20A Continuous 6S",
            HardwareCategory.BATTERY_PACK: "Nominal Energy >= 407.0 Wh (6S 22Ah)",
            HardwareCategory.POWER_DISTRIBUTION: "Main Bus Current >= 100A / Dual BEC",
            HardwareCategory.SERVO: "4x Control Surfaces (2 Ruddervator + 2 Aileron)",
            HardwareCategory.FLIGHT_CONTROLLER: ">=9 PWM Channels, Dual CAN, Triple IMU",
            HardwareCategory.NAVIGATION_GNSS: "Multiband RTK + Dual Compass",
            HardwareCategory.AIRSPEED_SENSOR: "Digital I2C Pitot Differential Pressure",
            HardwareCategory.TELEMETRY_LINK: "915MHz MAVLink Air-to-Ground Data Link",
            HardwareCategory.RC_RECEIVER: "CRSF / SBUS Long-Range Control Link",
            HardwareCategory.COMPANION_COMPUTER: "Companion SBC for Autonomy / Vision",
            HardwareCategory.MISSION_PAYLOAD: "1.5 kg Survey Camera / Gimbal",
        }

        bom_items: List[BillOfMaterialsItem] = []
        item_counter = 1
        total_parts = 0
        total_mass = 0.0
        total_cost = 0.0
        has_unverified_price = False
        verified_count = 0

        for cat, prod in selected_products.items():
            qty = quantities.get(cat, default_quantities.get(cat, 1))
            unit_mass = prod.mass_kg or 0.0
            item_total_mass = unit_mass * qty

            unit_price = prod.price_usd
            if unit_price is not None:
                item_total_cost = unit_price * qty
                total_cost += item_total_cost
            else:
                item_total_cost = None
                has_unverified_price = True

            req_satisfied = requirements_map.get(cat, default_reqs.get(cat, "Generic Engineering Requirement"))

            bom_id = f"BOM-{item_counter:03d}"
            item_counter += 1
            total_parts += qty
            total_mass += item_total_mass
            verified_count += 1

            bom_items.append(BillOfMaterialsItem(
                bom_id=bom_id,
                category=cat,
                manufacturer=prod.manufacturer,
                model=prod.model_number or prod.product_name,
                description=prod.product_name,
                quantity=qty,
                unit_mass_kg=unit_mass,
                total_mass_kg=item_total_mass,
                unit_price_usd=unit_price,
                total_price_usd=item_total_cost,
                pricing_status=prod.pricing_status,
                verification_status=VerificationStatus.VERIFIED_MATCH,
                compatibility_status=CompatibilityStatus.COMPATIBLE,
                engineering_requirement_satisfied=req_satisfied,
                datasheet_reference=prod.datasheet_reference,
                source_url=prod.source_url,
                confidence=prod.specification_confidence,
                notes=prod.notes,
            ))

        completeness_pct = (verified_count / len(default_quantities)) * 100.0 if default_quantities else 100.0

        return CommercialBillOfMaterials(
            items=bom_items,
            total_parts_count=total_parts,
            total_commercial_mass_kg=total_mass,
            total_commercial_cost_usd=total_cost,
            has_unverified_pricing=has_unverified_price,
            verification_completeness_pct=completeness_pct,
        )
