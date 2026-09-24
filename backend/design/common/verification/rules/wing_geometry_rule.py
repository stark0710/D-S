from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class WingGeometryRule(VerificationRule):
    """Verifies wing geometry parameters are within acceptable engineering bounds."""

    def __init__(self):
        super().__init__(
            rule_id="V_WING_GEOMETRY",
            title="Wing Geometry Validity",
            description="Verifies wing area, span, aspect ratio, and taper ratio are within acceptable bounds.",
            category=RuleCategory.WING,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        wing_spec = context.subsystem_specifications.get("WingPlanformSpecification")
        if not wing_spec:
            wing_spec = context.subsystem_specifications.get("WingPlanformOptimizer")
        if not wing_spec:
            return RuleStatus.NOT_APPLICABLE, "No wing specification found.", ""

        wing_area = getattr(wing_spec, "wing_area", None) or 0.0
        wingspan = getattr(wing_spec, "wing_span", None) or getattr(wing_spec, "wingspan", None) or getattr(wing_spec, "span", None) or 0.0
        aspect_ratio = getattr(wing_spec, "aspect_ratio", None) or 0.0
        taper_ratio = getattr(wing_spec, "taper_ratio", None) or 1.0

        failures = []
        if wing_area < 0.05:
            failures.append(f"wing area ({wing_area:.4f} m²) is unrealistically small (< 0.05 m²)")
        if wing_area > 5.0:
            failures.append(f"wing area ({wing_area:.4f} m²) is unrealistically large (> 5.0 m²)")
        if wingspan < 0.3:
            failures.append(f"wingspan ({wingspan:.3f} m) is too small (< 0.3 m)")
        if wingspan > 6.0:
            failures.append(f"wingspan ({wingspan:.3f} m) is excessively large (> 6.0 m)")
        if aspect_ratio < 3.0:
            failures.append(f"aspect ratio ({aspect_ratio:.2f}) is below minimum efficiency threshold (< 3.0)")
        if aspect_ratio > 20.0:
            failures.append(f"aspect ratio ({aspect_ratio:.2f}) is structurally infeasible (> 20.0)")
        if taper_ratio < 0.15:
            failures.append(f"taper ratio ({taper_ratio:.3f}) is too aggressive (< 0.15)")
        if taper_ratio > 1.05:
            failures.append(f"taper ratio ({taper_ratio:.3f}) exceeds physical bounds (> 1.05)")

        if failures:
            return (
                RuleStatus.FAIL,
                "Wing geometry violations: " + "; ".join(failures) + ".",
                "Re-examine wing planform optimizer design variable bounds."
            )
        return RuleStatus.PASS, f"Wing geometry valid (area={wing_area:.4f} m², span={wingspan:.3f} m, AR={aspect_ratio:.2f}, taper={taper_ratio:.3f}).", ""
