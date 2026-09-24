from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class ConvergenceValidityRule(VerificationRule):
    """Verifies that the design convergence loop completed successfully."""

    def __init__(self):
        super().__init__(
            rule_id="V_CONVERGENCE",
            title="Design Convergence Verification",
            description="Verifies that the convergence manager completed without divergence or oscillation.",
            category=RuleCategory.CERTIFICATION,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        report = context.convergence_report
        if not report:
            return RuleStatus.NOT_APPLICABLE, "No convergence report provided.", ""

        status = report.get("convergence_status", "Unknown") if isinstance(report, dict) else getattr(report, "convergence_status", "Unknown")

        if status == "Converged":
            iterations = report.get("iterations_performed", 0) if isinstance(report, dict) else getattr(report, "iterations_performed", 0)
            return RuleStatus.PASS, f"Design converged in {iterations} iterations.", ""
        elif status in ("Diverged", "Oscillated"):
            return (
                RuleStatus.FAIL,
                f"Design convergence failed with status: {status}.",
                "Review subsystem coupling and adjust convergence damping parameters."
            )
        elif status == "Max Iterations Exceeded":
            return (
                RuleStatus.WARNING,
                "Design did not converge within maximum iterations but may be near-stable.",
                "Increase max iterations or tighten subsystem tolerances."
            )
        else:
            return (
                RuleStatus.WARNING,
                f"Design convergence status is unknown: {status}.",
                "Check convergence manager output for diagnostics."
            )
