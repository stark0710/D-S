"""
VTOL Phase 8 Commercial Product Verifier.

Purpose:
    Compares candidate commercial product specifications against authoritative
    engineering requirement envelopes. Evaluates numerical constraints, margins,
    and missing data handling.

Standards:
    - Never fabricates specifications: if missing from datasheet, returns INSUFFICIENT_DATA / UNVERIFIED.
    - Explicit margins and violation tracking for every evaluated parameter.
"""

from typing import List, Optional
from .product_models import (
    CommercialProduct,
    HardwareRequirement,
    RequirementVerification,
    ProductVerificationReport,
    VerificationStatus,
)


class ProductVerifier:
    """
    Evaluates individual commercial products against formal engineering envelopes.
    """

    @classmethod
    def verify_parameter(
        cls,
        product: CommercialProduct,
        requirement: HardwareRequirement,
    ) -> RequirementVerification:
        """
        Evaluates a single requirement parameter against a product's verified specifications.
        """
        param_name = requirement.parameter
        actual = product.get_spec(param_name, None)

        # Handle numeric conversion if possible
        actual_float: Optional[float] = None
        if actual is not None:
            try:
                actual_float = float(actual)
            except (ValueError, TypeError):
                actual_float = None

        req_min = requirement.minimum_value
        req_max = requirement.maximum_value

        # Missing specification handling
        if actual_float is None:
            status = (
                VerificationStatus.INSUFFICIENT_DATA
                if requirement.hard_constraint
                else VerificationStatus.UNVERIFIED
            )
            return RequirementVerification(
                requirement_id=requirement.requirement_id,
                parameter=param_name,
                required_min=req_min,
                required_max=req_max,
                actual_value=None,
                units=requirement.units,
                status=status,
                margin=None,
                margin_pct=None,
                notes=f"Specification '{param_name}' not published or unverified in manufacturer datasheet.",
            )

        # Check bounds
        is_valid = True
        violation_notes = []
        margin: Optional[float] = None
        margin_pct: Optional[float] = None

        if req_min is not None:
            if actual_float < req_min:
                is_valid = False
                deficit = req_min - actual_float
                violation_notes.append(f"Below minimum: {actual_float} < {req_min} {requirement.units} (Deficit: {deficit:.3f})")
                margin = actual_float - req_min
                margin_pct = (margin / abs(req_min)) * 100.0 if req_min != 0 else 0.0
            else:
                margin = actual_float - req_min
                margin_pct = (margin / abs(req_min)) * 100.0 if req_min != 0 else 0.0

        if req_max is not None:
            if actual_float > req_max:
                is_valid = False
                excess = actual_float - req_max
                violation_notes.append(f"Exceeds maximum: {actual_float} > {req_max} {requirement.units} (Excess: {excess:.3f})")
                margin = req_max - actual_float
                margin_pct = (margin / abs(req_max)) * 100.0 if req_max != 0 else 0.0
            else:
                if margin is None or (req_max - actual_float) < margin:
                    margin = req_max - actual_float
                    margin_pct = (margin / abs(req_max)) * 100.0 if req_max != 0 else 0.0

        if is_valid:
            status = VerificationStatus.VERIFIED_MATCH
            notes = f"Verified: {actual_float} {requirement.units} satisfies envelope."
        else:
            status = VerificationStatus.FAILS_REQUIREMENT
            notes = "; ".join(violation_notes)

        return RequirementVerification(
            requirement_id=requirement.requirement_id,
            parameter=param_name,
            required_min=req_min,
            required_max=req_max,
            actual_value=actual_float,
            units=requirement.units,
            status=status,
            margin=margin,
            margin_pct=margin_pct,
            notes=notes,
        )

    @classmethod
    def verify_product(
        cls,
        product: CommercialProduct,
        requirements: List[HardwareRequirement],
    ) -> ProductVerificationReport:
        """
        Performs exhaustive verification of a product across all applicable requirements.
        """
        verifications: List[RequirementVerification] = []
        hard_passed = 0
        hard_failed = 0
        missing_count = 0
        rejection_reasons: List[str] = []

        for req in requirements:
            ver = cls.verify_parameter(product, req)
            verifications.append(ver)

            if req.hard_constraint:
                if ver.status == VerificationStatus.VERIFIED_MATCH:
                    hard_passed += 1
                elif ver.status == VerificationStatus.FAILS_REQUIREMENT:
                    hard_failed += 1
                    rejection_reasons.append(f"FAILED [{req.parameter}]: {ver.notes}")
                elif ver.status in (VerificationStatus.INSUFFICIENT_DATA, VerificationStatus.UNVERIFIED):
                    missing_count += 1
                    rejection_reasons.append(f"MISSING [{req.parameter}]: {ver.notes}")

        # Determine overall product status
        if hard_failed > 0:
            overall_status = VerificationStatus.FAILS_REQUIREMENT
        elif missing_count > 0:
            overall_status = VerificationStatus.INSUFFICIENT_DATA
        elif hard_passed > 0 and hard_failed == 0 and missing_count == 0:
            overall_status = VerificationStatus.VERIFIED_MATCH
        else:
            overall_status = VerificationStatus.PARTIAL_MATCH

        return ProductVerificationReport(
            product=product,
            verifications=verifications,
            overall_status=overall_status,
            hard_requirements_passed=hard_passed,
            hard_requirements_failed=hard_failed,
            missing_data_count=missing_count,
            rejection_reasons=rejection_reasons,
        )
