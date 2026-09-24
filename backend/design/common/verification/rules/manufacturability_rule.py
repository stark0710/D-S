from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class ManufacturabilityRule(VerificationRule):
    """Verifies that the sized aircraft dimensions are within manufacturing constraints."""

    def __init__(self):
        super().__init__(
            rule_id="V_MANUFACTURING",
            title="Manufacturability Feasibility",
            description="Verifies overall aircraft dimensions, structural margins, and component counts are manufacturable.",
            category=RuleCategory.MANUFACTURING,
            severity=RuleSeverity.WARNING
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        wing_spec = context.subsystem_specifications.get("WingPlanformSpecification")
        if not wing_spec:
            wing_spec = context.subsystem_specifications.get("WingPlanformOptimizer")

        fuse_spec = context.subsystem_specifications.get("FuselageSpecification")
        if not fuse_spec:
            fuse_spec = context.subsystem_specifications.get("FuselageOptimizer")

        if not wing_spec and not fuse_spec:
            return RuleStatus.NOT_APPLICABLE, "No geometry specifications found.", ""

        warnings = []

        if wing_spec:
            wingspan = getattr(wing_spec, "wingspan", getattr(wing_spec, "span", 0.0))
            tip_chord = getattr(wing_spec, "tip_chord", 0.0)
            if tip_chord > 0 and tip_chord < 0.04:
                warnings.append(f"wing tip chord ({tip_chord:.3f} m) is very thin and fragile for manufacturing")
            if wingspan > 3.5:
                warnings.append(f"wingspan ({wingspan:.2f} m) may require multi-section wing construction")

        if fuse_spec:
            height = getattr(fuse_spec, "height", 0.0)
            width = getattr(fuse_spec, "width", 0.0)
            if height > 0 and height < 0.08:
                warnings.append(f"fuselage height ({height:.3f} m) is very shallow for component integration")
            if width > 0 and width < 0.08:
                warnings.append(f"fuselage width ({width:.3f} m) is very narrow for component integration")

        if warnings:
            return (
                RuleStatus.WARNING,
                "Manufacturing feasibility warnings: " + "; ".join(warnings) + ".",
                "Consider adjusting dimensions to improve manufacturability and structural robustness."
            )
        return RuleStatus.PASS, "Aircraft dimensions are within standard manufacturing tolerances.", ""
