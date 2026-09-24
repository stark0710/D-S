from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus

class ElectricalBudgetRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="V_ELEC_CURRENT_BUDGET",
            title="Electrical Current Budget Compliance",
            description="Verifies that the sized electrical components operate within safety limits.",
            category=RuleCategory.ELECTRICAL,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        elec_spec = context.subsystem_specifications.get("ElectricalSystemSpecification")
        if not elec_spec:
            elec_spec = context.subsystem_specifications.get("ElectricalOptimizer")
            
        if not elec_spec:
            return RuleStatus.NOT_APPLICABLE, "No electrical system specification found.", ""

        max_drawn_current = getattr(elec_spec, "maximum_system_current_a", 0.0)
        esc_rating = getattr(elec_spec, "esc_rating_a", 0.0)
        battery_discharge = getattr(elec_spec, "battery_max_discharge_current_a", 0.0)

        if max_drawn_current > esc_rating + 1e-4:
            return (
                RuleStatus.FAIL,
                f"Peak current demand ({max_drawn_current:.1f} A) exceeds sized ESC continuous rating ({esc_rating:.1f} A).",
                "Select a larger ESC or limit maximum throttle/power targets."
            )
            
        if max_drawn_current > battery_discharge + 1e-4:
            return (
                RuleStatus.FAIL,
                f"Peak current demand ({max_drawn_current:.1f} A) exceeds battery discharge capability ({battery_discharge:.1f} A).",
                "Select a battery with higher capacity or C-rating."
            )

        return RuleStatus.PASS, f"Electrical currents ({max_drawn_current:.1f} A) are within component ratings (ESC: {esc_rating:.1f} A, Battery: {battery_discharge:.1f} A).", ""
