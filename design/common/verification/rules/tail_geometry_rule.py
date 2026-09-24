from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class TailGeometryRule(VerificationRule):
    """Verifies tail geometry and volume coefficients are within acceptable bounds."""

    def __init__(self):
        super().__init__(
            rule_id="V_TAIL_GEOMETRY",
            title="Tail Geometry and Volume Coefficient Validity",
            description="Verifies tail arm, tail areas, and volume coefficients are within bounds.",
            category=RuleCategory.TAIL,
            severity=RuleSeverity.ERROR
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        tail_spec = context.subsystem_specifications.get("TailSpecification")
        if not tail_spec:
            tail_spec = context.subsystem_specifications.get("TailOptimizer")
        if not tail_spec:
            return RuleStatus.NOT_APPLICABLE, "No tail specification found.", ""

        h_vol = getattr(tail_spec, "horizontal_volume_coefficient", 0.0)
        v_vol = getattr(tail_spec, "vertical_volume_coefficient", 0.0)
        tail_arm = getattr(tail_spec, "tail_arm", 0.0)

        fuse_spec = context.subsystem_specifications.get("FuselageSpecification")
        if not fuse_spec:
            fuse_spec = context.subsystem_specifications.get("FuselageOptimizer")
        fuse_length = (getattr(fuse_spec, "overall_length", None) or getattr(fuse_spec, "length", None) or 1.0) if fuse_spec else 1.0

        failures = []
        warnings = []

        if h_vol < 0.3:
            failures.append(f"horizontal volume coefficient ({h_vol:.3f}) is below stability minimum (< 0.30)")
        elif h_vol > 1.0:
            warnings.append(f"horizontal volume coefficient ({h_vol:.3f}) is unusually high (> 1.0)")

        if v_vol < 0.02:
            failures.append(f"vertical volume coefficient ({v_vol:.3f}) is below yaw stability minimum (< 0.02)")
        elif v_vol > 0.10:
            warnings.append(f"vertical volume coefficient ({v_vol:.3f}) is unusually high (> 0.10)")

        if tail_arm > 0 and fuse_length > 0:
            arm_ratio = tail_arm / fuse_length
            if arm_ratio > 0.85:
                failures.append(f"tail arm ratio ({arm_ratio:.3f}) exceeds 85% of fuselage length")
            elif arm_ratio < 0.25:
                failures.append(f"tail arm ratio ({arm_ratio:.3f}) is too short for adequate stability (< 25%)")

        if failures:
            return (
                RuleStatus.FAIL,
                "Tail geometry violations: " + "; ".join(failures) + ".",
                "Adjust tail volume coefficients or tail arm ratio within feasible bounds."
            )
        if warnings:
            return (
                RuleStatus.WARNING,
                "Tail geometry warnings: " + "; ".join(warnings) + ".",
                "Consider reviewing tail sizing for drag and weight optimality."
            )
        return RuleStatus.PASS, f"Tail geometry valid (V_h={h_vol:.3f}, V_v={v_vol:.3f}, arm={tail_arm:.3f} m).", ""
