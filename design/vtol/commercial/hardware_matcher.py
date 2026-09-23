"""
VTOL Phase 8 Commercial Hardware Matching and Verification Orchestrator.

Purpose:
    Top-level orchestration engine coordinating engineering requirement extraction,
    commercial product catalog searching, specification verification, system compatibility,
    Bill of Materials (BOM) synthesis, mass closure, and power closure.

Standards:
    - Downstream of Authoritative Physics (Phases 1-7).
    - Preserves all rejected candidates and reports exact rejection reasons.
    - If no product satisfies an envelope, reports NO_VERIFIED_COMMERCIAL_MATCH.
    - Full traceability linking requirement -> specification -> source -> verification.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import datetime
from typing import Any, Dict, List, Optional

from .product_models import (
    CommercialProduct,
    HardwareCategory,
    HardwareRequirement,
    ProductVerificationReport,
    SelectionStatus,
    VerificationStatus,
    HardwareReevaluationTrigger,
)
from .product_catalog import ProductCatalog, CATALOG
from .product_verifier import ProductVerifier
from .compatibility import SystemCompatibilityChecker, HardwareCompatibilityMatrix
from .requirement_extractor import HardwareRequirementExtractor
from .closure_engine import (
    MassClosureEngine,
    MassClosureResult,
    PowerClosureEngine,
    PowerClosureResult,
)
from .bom import CommercialBillOfMaterials, BillOfMaterialsItem


@dataclass(slots=True)
class TraceabilityEntry:
    """Requirement-to-product traceability record."""
    requirement_id: str
    parameter: str
    required_value: str
    provenance: str
    product_matched: str
    datasheet_specification: str
    datasheet_source: str
    verification_status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "parameter": self.parameter,
            "required_value": self.required_value,
            "provenance": self.provenance,
            "product_matched": self.product_matched,
            "datasheet_specification": self.datasheet_specification,
            "datasheet_source": self.datasheet_source,
            "verification_status": self.verification_status,
        }


@dataclass(slots=True)
class HardwareSelectionResult:
    """
    Consolidated Phase 8 commercial hardware selection and verification payload.
    """
    selection_status: SelectionStatus
    engineering_requirements: List[HardwareRequirement]
    selected_products: Dict[HardwareCategory, CommercialProduct]
    verified_reports: Dict[str, ProductVerificationReport]
    rejected_reports: Dict[str, ProductVerificationReport]
    compatibility_matrix: HardwareCompatibilityMatrix
    selected_bom: CommercialBillOfMaterials
    mass_closure: MassClosureResult
    power_closure: PowerClosureResult
    traceability_matrix: List[TraceabilityEntry]
    unresolved_requirements: List[str]
    no_match_requirements: List[str]
    reevaluation_triggers: List[HardwareReevaluationTrigger]
    verification_date: str
    warnings: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return self.selection_status == SelectionStatus.HARDWARE_SELECTION_COMPLETE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selection_status": self.selection_status.value,
            "verification_date": self.verification_date,
            "is_complete": self.is_complete,
            "selected_bom": self.selected_bom.to_dict(),
            "mass_closure": self.mass_closure.to_dict(),
            "power_closure": self.power_closure.to_dict(),
            "compatibility_matrix": self.compatibility_matrix.to_dict(),
            "unresolved_requirements": list(self.unresolved_requirements),
            "no_match_requirements": list(self.no_match_requirements),
            "warnings": list(self.warnings),
            "reevaluation_triggers": [t.to_dict() for t in self.reevaluation_triggers],
            "traceability_matrix": [t.to_dict() for t in self.traceability_matrix],
            "engineering_requirements": [r.to_dict() for r in self.engineering_requirements],
            "selected_products": {k.value: v.to_dict() for k, v in self.selected_products.items()},
        }


class HardwareMatcher:
    """
    Coordinates hardware requirement mapping, commercial product searching,
    filtering, compatibility checks, and BOM generation.
    """

    def __init__(self, catalog: Optional[ProductCatalog] = None) -> None:
        self.catalog = catalog or CATALOG

    def match_hardware(
        self,
        design_result: Optional[Any] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> HardwareSelectionResult:
        overrides = overrides or {}
        today_str = datetime.date.today().isoformat()

        # 1. Extract engineering requirement envelopes
        requirements = HardwareRequirementExtractor.extract_requirements(design_result, overrides)

        # Group requirements by hardware category
        reqs_by_cat: Dict[HardwareCategory, List[HardwareRequirement]] = {}
        for req in requirements:
            reqs_by_cat.setdefault(req.category, []).append(req)

        selected_products: Dict[HardwareCategory, CommercialProduct] = {}
        verified_reports: Dict[str, ProductVerificationReport] = {}
        rejected_reports: Dict[str, ProductVerificationReport] = {}
        unresolved_reqs: List[str] = []
        no_match_reqs: List[str] = []
        warnings: List[str] = []

        # 2. Match each hardware category against catalog
        for cat, cat_reqs in reqs_by_cat.items():
            candidates = self.catalog.get_by_category(cat)

            if not candidates:
                no_match_reqs.append(f"Category {cat.value}: No candidates available in catalog.")
                continue

            cat_verified: List[ProductVerificationReport] = []

            for cand in candidates:
                report = ProductVerifier.verify_product(cand, cat_reqs)
                if report.is_verified:
                    cat_verified.append(report)
                    verified_reports[cand.product_id] = report
                else:
                    rejected_reports[cand.product_id] = report

            if cat_verified:
                # Deterministic selection: prioritize lightest verified candidate to protect MTOW
                cat_verified.sort(key=lambda r: (r.product.mass_kg or 999.0))
                best_rep = cat_verified[0]
                selected_products[cat] = best_rep.product
            else:
                no_match_reqs.append(f"NO_VERIFIED_COMMERCIAL_MATCH for {cat.value} across {len(candidates)} evaluated candidates.")
                warnings.append(f"No commercial candidate fully verified for {cat.value}.")

        # Handle explicit deferred parameters (e.g. Servo torque)
        for req in requirements:
            if req.provenance.value in ("DEFERRED", "UNRESOLVED_INPUT") or not req.hard_constraint:
                unresolved_reqs.append(f"Requirement [{req.requirement_id}]: {req.notes}")

        # 3. System-level Interface Compatibility Matrix (14 interface pairs)
        compat_matrix = SystemCompatibilityChecker.check_all_interfaces(selected_products)

        # 4. Compile Commercial Bill of Materials (BOM)
        bom = CommercialBillOfMaterials.compile_bom(selected_products)

        # 5. Mass Closure
        baseline_mtow = getattr(design_result, "mtow_kg", None) if design_result else None
        mass_closure = MassClosureEngine.evaluate_mass_closure(
            selected_hardware_mass_kg=bom.total_commercial_mass_kg,
            baseline_mtow_kg=baseline_mtow,
        )

        # 6. Electrical Power Closure
        power_closure = PowerClosureEngine.evaluate_power_closure(selected_products)

        # 7. Requirement-to-Product Traceability Matrix
        traceability: List[TraceabilityEntry] = []
        for req in requirements:
            matched_prod = selected_products.get(req.category)
            if matched_prod:
                val_str = str(matched_prod.get_spec(req.parameter, "N/A"))
                traceability.append(TraceabilityEntry(
                    requirement_id=req.requirement_id,
                    parameter=req.parameter,
                    required_value=f"{req.minimum_value or ''} .. {req.maximum_value or ''} {req.units}".strip(),
                    provenance=req.provenance.value,
                    product_matched=f"{matched_prod.manufacturer} {matched_prod.product_name}",
                    datasheet_specification=f"{req.parameter} = {val_str} {req.units}",
                    datasheet_source=matched_prod.datasheet_reference,
                    verification_status=VerificationStatus.VERIFIED_MATCH.value,
                ))
            else:
                traceability.append(TraceabilityEntry(
                    requirement_id=req.requirement_id,
                    parameter=req.parameter,
                    required_value=f"{req.minimum_value or ''} .. {req.maximum_value or ''} {req.units}".strip(),
                    provenance=req.provenance.value,
                    product_matched="NONE",
                    datasheet_specification="UNVERIFIED",
                    datasheet_source="N/A",
                    verification_status=VerificationStatus.FAILS_REQUIREMENT.value,
                ))

        # 8. Determine Overall Status
        if len(no_match_reqs) == 0 and compat_matrix.is_fully_compatible and mass_closure.is_mass_closed and power_closure.is_power_closed:
            selection_status = SelectionStatus.HARDWARE_SELECTION_COMPLETE
        elif len(no_match_reqs) == 0:
            selection_status = SelectionStatus.HARDWARE_SELECTION_WITH_WARNINGS
        else:
            selection_status = SelectionStatus.HARDWARE_SELECTION_INCOMPLETE

        return HardwareSelectionResult(
            selection_status=selection_status,
            engineering_requirements=requirements,
            selected_products=selected_products,
            verified_reports=verified_reports,
            rejected_reports=rejected_reports,
            compatibility_matrix=compat_matrix,
            selected_bom=bom,
            mass_closure=mass_closure,
            power_closure=power_closure,
            traceability_matrix=traceability,
            unresolved_requirements=unresolved_reqs,
            no_match_requirements=no_match_reqs,
            reevaluation_triggers=mass_closure.reevaluation_triggers,
            verification_date=today_str,
            warnings=warnings + compat_matrix.warnings + power_closure.warnings,
        )
