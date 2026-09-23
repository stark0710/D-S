from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class FuselageGeometryRule(VerificationRule):
    """Verifies fuselage geometry parameters are within acceptable engineering bounds."""

    def __init__(self):
        super().__init__(
            rule_id="V_FUSELAGE_GEOMETRY",
            title="Fuselage Geometry Validity",
            description="Verifies fuselage length, width, height, and fineness ratio are within acceptable bounds.",
            category=RuleCategory.FUSELAGE,
            severity=RuleSeverity.ERROR
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        fuse_spec = context.subsystem_specifications.get("FuselageSpecification")
        if not fuse_spec:
            fuse_spec = context.subsystem_specifications.get("FuselageOptimizer")
        if not fuse_spec:
            return RuleStatus.NOT_APPLICABLE, "No fuselage specification found.", ""

        length = getattr(fuse_spec, "overall_length", None) or getattr(fuse_spec, "length", None) or 0.0
        width = getattr(fuse_spec, "width", None) or 0.0
        height = getattr(fuse_spec, "height", None) or 0.0
        fineness = getattr(fuse_spec, "fineness_ratio", None) or 0.0

        failures = []
        if length < 0.3:
            failures.append(f"fuselage length ({length:.3f} m) is too short (< 0.3 m)")
        if length > 4.0:
            failures.append(f"fuselage length ({length:.3f} m) is excessively long (> 4.0 m)")
        if width < 0.05:
            failures.append(f"fuselage width ({width:.3f} m) is too narrow (< 0.05 m)")
        if width > 0.8:
            failures.append(f"fuselage width ({width:.3f} m) is excessively wide (> 0.8 m)")
        if height < 0.05:
            failures.append(f"fuselage height ({height:.3f} m) is too shallow (< 0.05 m)")
        if fineness < 3.0:
            failures.append(f"fineness ratio ({fineness:.2f}) is below drag-optimal threshold (< 3.0)")
        if fineness > 15.0:
            failures.append(f"fineness ratio ({fineness:.2f}) is structurally impractical (> 15.0)")

        # Check wing root chord vs fuselage width compatibility
        wing_spec = context.subsystem_specifications.get("WingPlanformSpecification")
        if not wing_spec:
            wing_spec = context.subsystem_specifications.get("WingPlanformOptimizer")
        if wing_spec:
            root_chord = getattr(wing_spec, "root_chord", 0.0)
            if root_chord > 0 and width > root_chord * 1.05:
                failures.append(
                    f"fuselage width ({width:.3f} m) exceeds wing root chord ({root_chord:.3f} m) causing aerodynamic blockage"
                )

        if failures:
            return (
                RuleStatus.FAIL,
                "Fuselage geometry violations: " + "; ".join(failures) + ".",
                "Adjust fuselage cross-section or select a longer/narrower fuselage profile."
            )
        return RuleStatus.PASS, f"Fuselage geometry valid (L={length:.3f} m, W={width:.3f} m, H={height:.3f} m, FR={fineness:.2f}).", ""
