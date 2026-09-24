from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class PackagingIntegrationRule(VerificationRule):
    """Verifies that the payload is physically packaged within the fuselage volume."""

    def __init__(self):
        super().__init__(
            rule_id="V_PACKAGING",
            title="Payload Packaging Integration Verification",
            description="Verifies that the payload fits within the sized fuselage cabin volume.",
            category=RuleCategory.GEOMETRY,
            severity=RuleSeverity.ERROR
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        payload_spec = context.subsystem_specifications.get("PayloadPackagingSpecification")
        if not payload_spec:
            payload_spec = context.subsystem_specifications.get("PayloadPackagingOptimizer")
        if not payload_spec:
            return RuleStatus.NOT_APPLICABLE, "No payload packaging specification found.", ""

        fuse_spec = context.subsystem_specifications.get("FuselageSpecification")
        if not fuse_spec:
            fuse_spec = context.subsystem_specifications.get("FuselageOptimizer")
        if not fuse_spec:
            return RuleStatus.NOT_APPLICABLE, "No fuselage specification found.", ""

        # Payload volume
        payload_vol = getattr(payload_spec, "total_volume_m3", getattr(payload_spec, "payload_volume_m3", 0.0))
        # Fuselage cabin volume
        cabin_length = getattr(fuse_spec, "cabin_length", 0.0)
        width = getattr(fuse_spec, "width", 0.0)
        height = getattr(fuse_spec, "height", 0.0)
        cabin_vol = cabin_length * width * height * 0.65  # 65% packing efficiency

        if payload_vol > 0 and cabin_vol > 0 and payload_vol > cabin_vol * 1.05:
            return (
                RuleStatus.FAIL,
                f"Payload volume ({payload_vol:.4f} m³) exceeds fuselage cabin capacity ({cabin_vol:.4f} m³).",
                "Increase fuselage dimensions or reduce payload volume."
            )

        return RuleStatus.PASS, "Payload packaging fits within fuselage cabin volume.", ""
