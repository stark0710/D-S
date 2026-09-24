from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus

class CGMarginRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="V_CG_STATIC_MARGIN",
            title="Static Margin Stability Verification",
            description="Verifies that the aircraft design has a stable static margin within safety limits [0.05, 0.25].",
            category=RuleCategory.CG,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        cg_spec = context.subsystem_specifications.get("CGSpecification")
        if not cg_spec:
            cg_spec = context.subsystem_specifications.get("CGOptimizer")
            
        if not cg_spec:
            return RuleStatus.NOT_APPLICABLE, "No CG specification found.", ""

        static_margin = getattr(cg_spec, "static_margin", 0.0)

        if static_margin < 0.05 - 1e-4:
            return (
                RuleStatus.FAIL,
                f"Static margin ({static_margin:.3f}) is below stable threshold of 0.05. Risk of pitch instability.",
                "Move movable masses (e.g. payload or battery) forward, or increase horizontal tail volume/area."
            )
        elif static_margin > 0.25 + 1e-4:
            return (
                RuleStatus.WARNING,
                f"Static margin ({static_margin:.3f}) is above standard limit of 0.25. High pitch stiffness and elevator authority penalty.",
                "Shift internal masses aft or adjust wing chord position forward."
            )

        return RuleStatus.PASS, f"Static margin of {static_margin:.3f} is in the stable safety envelope [0.05, 0.25].", ""
